#!/usr/bin/env python3
"""
Web server for controlling the humanoid robot through a web interface.
Provides REST API endpoints for robot control and a web UI.
"""
from flask import Flask, render_template, request, jsonify
import threading
import time
import json
import os
import logging
from ..controllers.mock_robot_controller import MockRobotController
from ..controllers.robot_controller import RobotController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

app = Flask(__name__)

# Create robot controller instance based on platform
if is_raspberry_pi():
    logger.info("Running on Raspberry Pi - using real robot controller")
    robot = RobotController()
else:
    logger.info("Not running on Raspberry Pi - using mock robot controller")
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
        try:
            logger.debug(f"Executing robot action: {action_func.__name__}")
            return action_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing robot action {action_func.__name__}: {str(e)}")
            raise

@app.route('/')
def index():
    """Render the main web interface."""
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_robot():
    """Initialize the robot."""
    global robot_initialized
    try:
        if robot_initialized:
            logger.warning("Robot already initialized")
            return jsonify({"status": "warning", "message": "Robot already initialized"})
        
        logger.info("Starting robot initialization...")
        safe_robot_action(robot.initialize_robot)
        robot_initialized = True
        logger.info("Robot initialization complete")
        return jsonify({"status": "success", "message": "Robot initialized"})
    except Exception as e:
        logger.error(f"Robot initialization failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/servo', methods=['POST'])
def move_servo():
    """Move a specific servo to a given angle."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = request.get_json()
        servo_index = data.get('servo')
        angle = data.get('angle')
        speed = data.get('speed', 0.01)
        
        if servo_index is None or angle is None:
            return jsonify({"status": "error", "message": "Missing servo or angle"}), 400
        
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

@app.route('/api/eyes', methods=['GET'])
def get_eyes_data():
    """Get data from the robot's eye sensor."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = safe_robot_action(robot.get_eye_data)
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mpu6050', methods=['GET'])
def get_mpu6050_data():
    """Get data from the MPU-6050 sensor."""
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        data = safe_robot_action(robot.get_mpu6050_data)
        return jsonify({
            "status": "success",
            "data": data
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