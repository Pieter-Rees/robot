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
from robot_controller import (
    initialize_robot, 
    set_servo, 
    stand_up, 
    step_forward, 
    shutdown,
    Servos,
    DEFAULT_POSITIONS,
    SERVO_LIMITS
)

app = Flask(__name__)

# Flag to track if robot is initialized
robot_initialized = False

# Mutex to prevent concurrent servo operations
servo_lock = threading.Lock()

# Current positions of servos
current_positions = DEFAULT_POSITIONS.copy()

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
    """
    Serve the main control page.
    
    Returns:
        Rendered index.html template
    """
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_robot():
    """
    Initialize the robot's servos to default positions.
    
    Returns:
        JSON response with status
    """
    global robot_initialized
    
    try:
        safe_robot_action(initialize_robot)
        robot_initialized = True
        return jsonify({"status": "success", "message": "Robot initialized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/servo', methods=['POST'])
def move_servo():
    """
    Move a specific servo to a position.
    
    Request JSON:
        servo: Servo index
        angle: Target angle
        speed: Speed of movement (optional)
        
    Returns:
        JSON response with status and position
    """
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    data = request.json
    servo_index = data.get('servo')
    angle = data.get('angle')
    speed = data.get('speed', 0.01)
    
    if servo_index is None or angle is None:
        return jsonify({"status": "error", "message": "Missing servo index or angle"}), 400
    
    try:
        servo_index = int(servo_index)
        angle = int(angle)
        
        # Update current position
        current_positions[servo_index] = angle
        
        safe_robot_action(set_servo, servo_index, angle, speed)
        return jsonify({"status": "success", "position": angle})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/servo/<int:servo_index>', methods=['GET'])
def get_servo_position(servo_index):
    """
    Get the current position of a servo.
    
    Args:
        servo_index: Index of the servo
        
    Returns:
        JSON response with status, position and limits
    """
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        position = current_positions.get(servo_index, DEFAULT_POSITIONS.get(servo_index, 90))
        limits = SERVO_LIMITS.get(servo_index, (0, 180))
        
        return jsonify({
            "status": "success", 
            "position": position,
            "min": limits[0],
            "max": limits[1]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stand', methods=['POST'])
def stand():
    """
    Make the robot stand up.
    
    Returns:
        JSON response with status
    """
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    try:
        # Run in a separate thread to not block the response
        thread = threading.Thread(target=safe_robot_action, args=(stand_up,))
        thread.start()
        return jsonify({"status": "success", "message": "Standing up initiated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/walk', methods=['POST'])
def walk():
    """
    Make the robot walk forward a specified number of steps.
    
    Request JSON:
        steps: Number of steps to take (default: 1)
        
    Returns:
        JSON response with status
    """
    if not robot_initialized:
        return jsonify({"status": "error", "message": "Robot not initialized"}), 400
    
    data = request.json
    steps = data.get('steps', 1)
    
    try:
        steps = int(steps)
        
        def walk_steps():
            """Execute multiple steps in sequence."""
            for _ in range(steps):
                safe_robot_action(step_forward)
                time.sleep(0.5)
        
        # Run in a separate thread to not block the response
        thread = threading.Thread(target=walk_steps)
        thread.start()
        
        return jsonify({"status": "success", "message": f"Walking {steps} steps initiated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/shutdown', methods=['POST'])
def shutdown_robot():
    """
    Shutdown the robot safely.
    
    Returns:
        JSON response with status
    """
    global robot_initialized
    
    try:
        safe_robot_action(shutdown)
        robot_initialized = False
        return jsonify({"status": "success", "message": "Robot shutdown complete"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/robot_info', methods=['GET'])
def get_robot_info():
    """
    Get information about the robot configuration.
    
    Returns:
        JSON response with robot status and servo information
    """
    servo_info = {}
    
    for servo_index in DEFAULT_POSITIONS.keys():
        limits = SERVO_LIMITS.get(servo_index, (0, 180))
        position = current_positions.get(servo_index, DEFAULT_POSITIONS.get(servo_index, 90))
        
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