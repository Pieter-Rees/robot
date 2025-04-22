#!/usr/bin/env python3
"""
Web server for controlling the humanoid robot through a web interface.
Provides REST API endpoints for robot control and a web UI.

API Endpoints:
- GET /: Main web interface
- GET /api/robot_info: Get robot status and information
- POST /api/init: Initialize the robot
- POST /api/shutdown: Shutdown the robot
- GET /api/servo/<id>: Get servo position
- POST /api/servo: Move a servo
- GET /api/servos: Get all servo positions
- POST /api/stand: Make robot stand
- POST /api/walk: Make robot walk
- POST /api/dance: Make robot dance
- GET /api/calibration: Get calibration data
- POST /api/calibration: Save calibration data
- POST /api/calibration/servo/<id>: Calibrate specific servo 
"""
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import json
import os
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from http import HTTPStatus
from functools import lru_cache, wraps
import platform
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.profiler import ProfilerMiddleware
import gzip
from io import BytesIO

from robot.controllers.mock_robot_controller import MockRobotController
from robot.controllers.robot_controller import RobotController, ServoError, RobotControllerError
from robot.config import config, Servos
from robot.calibration import load_calibration, save_calibration

# Custom exception for API errors
class APIError(Exception):
    """Custom exception for API errors with status code."""
    def __init__(self, message: str, status_code: int = HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

@dataclass
class APIResponse:
    """Standard API response format."""
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

def format_response(response: APIResponse, status_code: int = HTTPStatus.OK) -> Tuple[Dict[str, Any], int]:
    """Format API response with consistent structure."""
    result = {"status": response.status}
    if response.message:
        result["message"] = response.message
    if response.data:
        result["data"] = response.data
    return result, status_code

def is_raspberry_pi() -> bool:
    """Check if the code is running on a Raspberry Pi."""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return 'raspberry pi' in f.read().lower()
    except:
        return False

# Get the absolute path to the web directory
web_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(web_dir, 'templates')
static_dir = os.path.join(web_dir, 'static')

app = Flask(__name__, 
            template_folder=templates_dir,
            static_folder=static_dir,
            static_url_path='/static')

# Configure Flask for better performance
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # Cache static files for 1 hour
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['JSONIFY_MIMETYPE'] = 'application/json'

# Add gzip compression
@app.after_request
def after_request(response):
    """Add gzip compression to responses."""
    if response.status_code < 200 or response.status_code >= 300:
        return response
    
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if 'gzip' not in accept_encoding.lower():
        return response
    
    response.direct_passthrough = False
    content = response.get_data()
    gzip_buffer = BytesIO()
    gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
    gzip_file.write(content)
    gzip_file.close()
    
    response.set_data(gzip_buffer.getvalue())
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(response.get_data())
    
    return response

# Add connection pooling
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

# Create robot controller instance based on platform
if is_raspberry_pi():
    print("Running on Raspberry Pi - using real robot controller")
    robot = RobotController()
else:
    print("Not running on Raspberry Pi - using mock robot controller")
    robot = MockRobotController()

# Flag to track if robot is initialized
robot_initialized = False

# Initialize thread pool with optimal worker count
cpu_count = os.cpu_count() or 4
thread_pool = ThreadPoolExecutor(max_workers=min(cpu_count, 8))

# Mutex to prevent concurrent servo operations
servo_lock = threading.Lock()

# Cache for frequently accessed data
servo_info_cache = {}
cache_lock = threading.Lock()

# Response cache
response_cache = {}
response_cache_lock = threading.Lock()

def cache_response(timeout=60):
    """Decorator to cache API responses."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            with response_cache_lock:
                if cache_key in response_cache:
                    cached_data, timestamp = response_cache[cache_key]
                    if time.time() - timestamp < timeout:
                        return cached_data
            
            # Generate new response
            response = f(*args, **kwargs)
            
            # Cache the response
            with response_cache_lock:
                response_cache[cache_key] = (response, time.time())
            
            return response
        return decorated_function
    return decorator

def require_initialized(f):
    """Decorator to ensure robot is initialized before operation."""
    def wrapper(*args, **kwargs):
        if not robot_initialized:
            raise APIError("Robot not initialized", HTTPStatus.BAD_REQUEST)
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def safe_robot_action(action_func, *args, **kwargs):
    """Execute robot actions with mutex lock to prevent concurrent operations."""
    with servo_lock:
        return action_func(*args, **kwargs)

@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors."""
    return format_response(
        APIResponse("error", error.message),
        error.status_code
    )

@app.errorhandler(Exception)
def handle_error(error):
    """Handle unexpected errors."""
    return format_response(
        APIResponse("error", str(error)),
        HTTPStatus.INTERNAL_SERVER_ERROR
    )

@app.route('/')
def index():
    """Render the main web interface."""
    # Get servo information for the template
    servos = []
    for servo_name, servo_id in vars(Servos).items():
        if not servo_name.startswith('_'):
            try:
                servo_config = config.get_servo_config(servo_id)
                servos.append({
                    'id': servo_id,
                    'name': servo_name,
                    'min': servo_config['min_angle'],
                    'max': servo_config['max_angle'],
                    'default': servo_config['default_position']
                })
            except ValueError:
                continue
    
    return render_template('index.html', servos=servos)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files with optimized caching."""
    return send_from_directory(
        static_dir,
        filename,
        cache_timeout=3600,
        conditional=True
    )

@app.route('/api/init', methods=['POST'])
def init_robot():
    """
    Initialize the robot.
    
    Returns:
        200: Robot initialized successfully
        500: Initialization failed
    """
    global robot_initialized
    try:
        safe_robot_action(robot.initialize_robot)
        robot_initialized = True
        return format_response(
            APIResponse("success", "Robot initialized successfully")
        )
    except Exception as e:
        robot_initialized = False
        raise APIError(f"Failed to initialize robot: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/servo', methods=['POST'])
@require_initialized
def move_servo():
    """Move a specific servo to a given angle with optimized validation."""
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided")
        
        # Get and validate parameters in parallel
        futures = []
        for key in ['servo', 'angle', 'speed']:
            if key in data:
                future = thread_pool.submit(validate_parameter, key, data[key])
                futures.append((key, future))
        
        # Collect validated parameters
        params = {}
        for key, future in futures:
            try:
                params[key] = future.result()
            except ValueError as e:
                raise APIError(str(e))
        
        # Submit servo movement to thread pool
        future = thread_pool.submit(
            safe_robot_action,
            robot.set_servo,
            params.get('servo'),
            params.get('angle'),
            params.get('speed', 0.01)
        )
        future.result()  # Wait for completion
        
        # Clear relevant caches
        with response_cache_lock:
            for key in list(response_cache.keys()):
                if key.startswith('get_all_servos'):
                    del response_cache[key]
        
        return format_response(
            APIResponse("success", f"Moved servo {params['servo']} to {params['angle']} degrees")
        )
        
    except ServoError as e:
        raise APIError(str(e))
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

def validate_parameter(key: str, value: Any) -> Any:
    """Validate and convert parameter values."""
    if key == 'servo':
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError("Invalid servo index")
    elif key == 'angle':
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError("Invalid angle/position")
    elif key == 'speed':
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.01
    return value

@app.route('/api/servo/<int:servo_id>', methods=['GET'])
@require_initialized
def get_servo_position(servo_id):
    """
    Get the current position of a specific servo.
    
    Args:
        servo_id (int): The ID of the servo
        
    Returns:
        200: Servo position
        400: Invalid servo ID
        500: Error getting position
    """
    try:
        state = robot.get_servo_state(servo_id)
        return format_response(
            APIResponse("success", data={
                "servo": servo_id,
                "position": state.position,
                "moving": state.moving,
                "target_position": state.target_position
            })
        )
    except ServoError as e:
        raise APIError(str(e))
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/servos', methods=['GET'])
@require_initialized
@cache_response(timeout=0.5)  # Cache for 500ms
def get_all_servos():
    """Get information about all servos with caching and compression."""
    try:
        # Format servo data for the frontend
        servo_info = {}
        futures = []
        
        # Submit all servo info requests in parallel
        for servo_id in vars(Servos).values():
            if isinstance(servo_id, int):
                future = thread_pool.submit(get_servo_info, servo_id)
                futures.append((servo_id, future))
        
        # Collect results as they complete
        for servo_id, future in futures:
            try:
                info = future.result()
                if info is not None:
                    servo_info[servo_id] = info
            except:
                continue
        
        return format_response(
            APIResponse("success", data={"servos": servo_info})
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@lru_cache(maxsize=32)
def get_servo_info(servo_id: int) -> Optional[Dict[str, Any]]:
    """Get cached servo information."""
    try:
        state = robot.get_servo_state(servo_id)
        config_data = config.get_servo_config(servo_id)
        return {
            "position": state.position,
            "moving": state.moving,
            "target_position": state.target_position,
            "min": config_data['min_angle'],
            "max": config_data['max_angle'],
            "default": config_data['default_position']
        }
    except (ServoError, ValueError):
        return None

@app.route('/api/stand', methods=['POST'])
@require_initialized
def stand():
    """
    Make the robot stand up.
    
    Returns:
        200: Stand up successful
        500: Stand up failed
    """
    try:
        future = thread_pool.submit(safe_robot_action, robot.stand_up)
        future.result()
        return format_response(
            APIResponse("success", "Robot stood up successfully")
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/walk', methods=['POST'])
@require_initialized
def walk():
    """
    Make the robot walk forward.
    
    JSON Parameters:
        steps (int, optional): Number of steps to take (default: 1)
        
    Returns:
        200: Walk command accepted
        500: Walk command failed
    """
    try:
        data = request.get_json()
        steps = data.get('steps', 1) if data else 1
        
        def walk_steps():
            for _ in range(steps):
                safe_robot_action(robot.step_forward)
                time.sleep(0.5)
        
        thread_pool.submit(walk_steps)
        return format_response(
            APIResponse("success", f"Walking {steps} steps")
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/shutdown', methods=['POST'])
def shutdown_robot():
    """
    Shutdown the robot.
    
    Returns:
        200: Shutdown successful
        500: Shutdown failed
    """
    global robot_initialized
    try:
        future = thread_pool.submit(safe_robot_action, robot.shutdown)
        future.result(timeout=5.0)  # 5 second timeout for shutdown
        robot_initialized = False
        return format_response(
            APIResponse("success", "Robot shut down successfully")
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/robot_info', methods=['GET'])
def get_robot_info():
    """
    Get information about the robot's current state.
    
    Returns:
        200: Robot information
    """
    return format_response(
        APIResponse("success", data={
            "initialized": robot_initialized,
            "platform": "Raspberry Pi" if is_raspberry_pi() else "Other",
            "controller_type": type(robot).__name__
        })
    )

@app.route('/api/dance', methods=['POST'])
@require_initialized
def dance():
    """
    Make the robot perform a dance sequence.
    
    Returns:
        200: Dance command accepted
        500: Dance command failed
    """
    try:
        future = thread_pool.submit(safe_robot_action, robot.dance)
        future.result()
        return format_response(
            APIResponse("success", "Dance routine completed")
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/calibration', methods=['GET'])
def get_calibration():
    """Get current calibration values with caching."""
    try:
        # Try to get from cache first
        with cache_lock:
            if 'calibration' in servo_info_cache:
                return format_response(
                    APIResponse("success", data={"calibration": servo_info_cache['calibration']})
                )
        
        # Load and cache calibration
        calibration = load_calibration()
        with cache_lock:
            servo_info_cache['calibration'] = calibration
        
        return format_response(
            APIResponse("success", data={"calibration": calibration})
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/calibration', methods=['POST'])
def save_calibration_values():
    """
    Save new calibration values.
    
    JSON Parameters:
        calibration (dict): Mapping of servo IDs to calibrated positions
        
    Returns:
        200: Calibration saved
        400: Invalid calibration data
        500: Error saving calibration
    """
    try:
        data = request.get_json()
        if not data or 'calibration' not in data:
            raise APIError("Missing calibration data")
            
        calibration = data['calibration']
        save_calibration(calibration)
        return format_response(
            APIResponse("success", "Calibration saved successfully")
        )
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/calibration/servo/<int:servo_id>', methods=['POST'])
@require_initialized
def calibrate_servo_endpoint(servo_id):
    """
    Calibrate a specific servo.
    
    Args:
        servo_id (int): The ID of the servo to calibrate
        
    JSON Parameters:
        position (float): Calibration position
        
    Returns:
        200: Calibration successful
        400: Invalid parameters
        500: Calibration failed
    """
    try:
        data = request.get_json()
        if not data or 'position' not in data:
            raise APIError("Missing position data")
            
        try:
            position = float(data['position'])
        except (ValueError, TypeError):
            raise APIError("Invalid position value")
            
        # Move servo to calibration position
        future = thread_pool.submit(safe_robot_action, robot.set_servo, servo_id, position)
        future.result()
        
        # Update calibration
        calibration = load_calibration()
        calibration[servo_id] = position
        save_calibration(calibration)
        
        return format_response(
            APIResponse("success", f"Servo {servo_id} calibrated to position {position}")
        )
    except ServoError as e:
        raise APIError(str(e))
    except Exception as e:
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

def cleanup():
    """Clean up resources when the server shuts down."""
    if robot_initialized:
        try:
            robot.shutdown()
        except:
            pass
    
    # Clear all caches
    with response_cache_lock:
        response_cache.clear()
    
    thread_pool.shutdown(wait=True)

# Register cleanup handler
import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    try:
        # Start the server with optimized settings
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Disable debug mode for production
            threaded=True,
            processes=1
        )
    except KeyboardInterrupt:
        print("\nWeb server interrupted")
        if robot_initialized:
            print("Shutting down robot...")
            cleanup()
            print("Robot shutdown complete") 