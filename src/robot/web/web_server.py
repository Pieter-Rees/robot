#!/usr/bin/env python3
"""
Web server for controlling the humanoid robot through a web interface.
Provides REST API endpoints for robot control and a web UI.
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import time
import json
import os
from robot.controllers.mock_robot_controller import MockRobotController
from robot.controllers.robot_controller import RobotController
from robot.config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS
from robot.calibration import load_calibration, save_calibration

def is_raspberry_pi():
    """
    Check if the code is running on a Raspberry Pi.
    
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise
    """
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

# Create robot controller instance based on platform
if is_raspberry_pi():
    print("Running on Raspberry Pi - using real robot controller")
    robot = RobotController()
else:
    print("Not running on Raspberry Pi - using mock robot controller")
    robot = MockRobotController()

# Flag to track if robot is initialized
robot_initialized = False

# Mutex to prevent concurrent servo operations
servo_lock = threading.Lock()

# Safely execute robot functions with lock
def safe_robot_action(action_func, *args, **kwargs):
    """
    Execute robot actions with a mutex lock to prevent concurrent operations.
    
    Args:
        action_func: The function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The return value of the action_func
    """
    with servo_lock:
        return action_func(*args, **kwargs)

@app.route('/')
def index():
    """Render the main web interface."""
    # Get servo information for the template
    servos = []
    for servo_name, servo_index in vars(Servos).items():
        if not servo_name.startswith('_'):  # Skip private attributes
            limits = SERVO_LIMITS.get(servo_index, (0, 180))
            default = DEFAULT_POSITIONS.get(servo_index, 90)
            servos.append({
                'id': servo_index,
                'name': servo_name,
                'min': limits[0],
                'max': limits[1],
                'default': default
            })
    
    return render_template('index.html', servos=servos)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(static_dir, filename)

@app.route('/api/init', methods=['POST'])
def init_robot():
    """Initialize the robot."""
    global robot_initialized
    try:
        safe_robot_action(robot.initialize_robot)
        robot_initialized = True
        return jsonify({
            "status": "success",
            "message": "Robot initialized successfully"
        })
    except Exception as e:
        robot_initialized = False
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize robot: {str(e)}"
        }), 500

@app.route('/api/servo', methods=['POST'])
def move_servo():
    """Move a specific servo to a given angle."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        # Get and validate servo index
        servo_index = data.get('servo')
        if servo_index is None:
            return jsonify({"status": "error", "message": "Missing servo index"}), 400
        try:
            servo_index = int(servo_index)
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Invalid servo index"}), 400
            
        # Get and validate angle/position (support both parameter names)
        angle = data.get('angle') or data.get('position')
        if angle is None:
            return jsonify({"status": "error", "message": "Missing angle/position"}), 400
        try:
            angle = float(angle)
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Invalid angle/position"}), 400
            
        # Get and validate speed (optional)
        speed = data.get('speed', 0.01)
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            speed = 0.01  # Use default if invalid
        
        # Validate servo index exists
        if servo_index not in DEFAULT_POSITIONS:
            return jsonify({"status": "error", "message": f"Invalid servo index: {servo_index}"}), 400
            
        # Validate angle is within limits
        min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
        if not min_angle <= angle <= max_angle:
            return jsonify({
                "status": "error", 
                "message": f"Angle {angle} is outside valid range [{min_angle}, {max_angle}]"
            }), 400
        
        safe_robot_action(robot.set_servo, servo_index, angle, speed)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/servo/<int:servo_index>', methods=['GET'])
def get_servo_position(servo_index):
    """Get the current position of a specific servo."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        position = robot.current_positions.get(servo_index, 90)
        return jsonify({
            "status": "success",
            "servo": servo_index,
            "position": position
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/servos', methods=['GET'])
def get_all_servos():
    """Get information about all servos."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        # Format servo data for the frontend
        servo_info = {}
        for servo_index in DEFAULT_POSITIONS.keys():
            position = robot.current_positions.get(servo_index, 90)
            limits = SERVO_LIMITS.get(servo_index, (0, 180))
            servo_info[servo_index] = {
                "position": position,
                "min": limits[0],
                "max": limits[1]
            }
        
        return jsonify({
            "status": "success",
            "servos": servo_info
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stand', methods=['POST'])
def stand():
    """Make the robot stand up."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        safe_robot_action(robot.stand_up)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/walk', methods=['POST'])
def walk():
    """Make the robot walk forward."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = request.get_json()
        steps = data.get('steps', 1)
        
        def walk_steps():
            for _ in range(steps):
                safe_robot_action(robot.step_forward)
                time.sleep(0.5)
        
        # Run walking in a separate thread to avoid blocking
        threading.Thread(target=walk_steps).start()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/shutdown', methods=['POST'])
def shutdown_robot():
    """Shutdown the robot."""
    global robot_initialized
    try:
        safe_robot_action(robot.shutdown)
        robot_initialized = False
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/robot_info', methods=['GET'])
def get_robot_info():
    """Get information about the robot's current state."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        # Format servo data for the frontend
        servo_info = {}
        for servo_index in DEFAULT_POSITIONS.keys():
            position = robot.current_positions.get(servo_index, 90)
            limits = SERVO_LIMITS.get(servo_index, (0, 180))
            servo_info[servo_index] = {
                "position": position,
                "min": limits[0],
                "max": limits[1]
            }
        
        return jsonify({
            "status": "success",
            "initialized": robot_initialized,
            "servos": servo_info
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/dance', methods=['POST'])
def dance():
    """Make the robot perform a dance routine."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        # Run dance in a separate thread to avoid blocking
        threading.Thread(target=safe_robot_action, args=(robot.dance,)).start()
        return jsonify({"status": "success", "message": "Dance routine started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/calibration', methods=['GET'])
def get_calibration():
    """Get the current calibration values."""
    try:
        calibrated_positions = load_calibration()
        return jsonify({
            "status": "success",
            "calibration": calibrated_positions
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/calibration', methods=['POST'])
def save_calibration_values():
    """Save new calibration values."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = request.get_json()
        calibrated_positions = data.get('calibration')
        
        if not calibrated_positions:
            return jsonify({"status": "error", "message": "No calibration data provided"}), 400
        
        # Convert string keys to integers
        calibrated_positions = {int(k): v for k, v in calibrated_positions.items()}
        
        # Save the calibration
        save_calibration(calibrated_positions)
        return jsonify({"status": "success", "message": "Calibration saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/calibration/servo/<int:servo_index>', methods=['POST'])
def calibrate_servo_endpoint(servo_index):
    """Calibrate a specific servo."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = request.get_json()
        position = data.get('position')
        
        if position is None:
            return jsonify({"status": "error", "message": "No position provided"}), 400
        
        # Update the servo position
        safe_robot_action(robot.set_servo, servo_index, position)
        
        # Get current calibration
        calibrated_positions = load_calibration()
        calibrated_positions[servo_index] = position
        
        # Save updated calibration
        save_calibration(calibrated_positions)
        
        return jsonify({
            "status": "success",
            "message": f"Servo {servo_index} calibrated to position {position}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    try:
        # Start the server on all interfaces, port 5000
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nWeb server interrupted")
        if robot_initialized:
            print("Shutting down robot...")
            shutdown()
            print("Robot shutdown complete") 