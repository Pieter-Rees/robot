#!/usr/bin/env python3
"""
Mock Robot Controller module for testing without hardware.
Simulates servo motor control for robot movements.
"""
import time
import random

# Define servo indices for each joint
class Servos:
    """
    Constants defining servo motor indices for each joint in the robot.
    """
    HEAD = 0
    SHOULDER_RIGHT = 1
    SHOULDER_LEFT = 2
    ELBOW_RIGHT = 3
    ELBOW_LEFT = 4
    HIP_RIGHT = 5
    HIP_LEFT = 6
    KNEE_RIGHT = 7
    KNEE_LEFT = 8
    ANKLE_RIGHT = 9
    ANKLE_LEFT = 10
    WRIST_RIGHT = 11
    WRIST_LEFT = 12

# Default positions (neutral standing position)
DEFAULT_POSITIONS = {
    Servos.HEAD: 90,
    Servos.SHOULDER_RIGHT: 90,
    Servos.SHOULDER_LEFT: 90,
    Servos.ELBOW_RIGHT: 90,
    Servos.ELBOW_LEFT: 90,
    Servos.HIP_RIGHT: 90,
    Servos.HIP_LEFT: 90,
    Servos.KNEE_RIGHT: 90,
    Servos.KNEE_LEFT: 90,
    Servos.ANKLE_RIGHT: 90,
    Servos.ANKLE_LEFT: 90,
    Servos.WRIST_RIGHT: 90,
    Servos.WRIST_LEFT: 90
}

# Minimum and maximum angles for each servo to prevent damage
SERVO_LIMITS = {
    Servos.HEAD: (45, 135),
    Servos.SHOULDER_RIGHT: (30, 150),
    Servos.SHOULDER_LEFT: (30, 150),
    Servos.ELBOW_RIGHT: (30, 150),
    Servos.ELBOW_LEFT: (30, 150),
    Servos.HIP_RIGHT: (30, 150),
    Servos.HIP_LEFT: (30, 150),
    Servos.KNEE_RIGHT: (30, 150),
    Servos.KNEE_LEFT: (30, 150),
    Servos.ANKLE_RIGHT: (30, 150),
    Servos.ANKLE_LEFT: (30, 150),
    Servos.WRIST_RIGHT: (30, 150),
    Servos.WRIST_LEFT: (30, 150)
}

# Current positions of servos
current_positions = DEFAULT_POSITIONS.copy()

def set_servo(servo_index, angle, speed=0.01):
    """
    Simulate setting a servo to a specific angle.
    
    Args:
        servo_index (int): Index of the servo to control
        angle (float): Target angle in degrees
        speed (float): Time delay between angle increments (lower = faster)
    """
    # Apply safety limits
    min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
    safe_angle = max(min_angle, min(max_angle, angle))
    
    # Get current position
    current_angle = current_positions.get(servo_index, 90)
    
    # Simulate gradual movement
    if current_angle < safe_angle:
        for a in range(int(current_angle), int(safe_angle) + 1):
            current_positions[servo_index] = a
            time.sleep(speed)
    else:
        for a in range(int(current_angle), int(safe_angle) - 1, -1):
            current_positions[servo_index] = a
            time.sleep(speed)
    
    print(f"Servo {servo_index} moved to {safe_angle} degrees")

def initialize_robot():
    """
    Simulate initializing the robot to default positions.
    """
    print("Initializing robot to default position...")
    for servo_index, angle in DEFAULT_POSITIONS.items():
        current_positions[servo_index] = angle
        time.sleep(0.1)
    print("Robot initialized!")

def stand_up():
    """
    Simulate the robot standing up sequence.
    """
    print("Standing up...")
    
    # Center all servos
    for servo_index, angle in DEFAULT_POSITIONS.items():
        set_servo(servo_index, angle)
    
    # Simulate standing sequence
    set_servo(Servos.KNEE_RIGHT, 120)
    set_servo(Servos.KNEE_LEFT, 120)
    time.sleep(0.5)
    
    set_servo(Servos.HIP_RIGHT, 110)
    set_servo(Servos.HIP_LEFT, 110)
    time.sleep(0.5)
    
    set_servo(Servos.KNEE_RIGHT, 90)
    set_servo(Servos.KNEE_LEFT, 90)
    time.sleep(0.5)
    
    set_servo(Servos.HIP_RIGHT, 90)
    set_servo(Servos.HIP_LEFT, 90)
    
    print("Robot is now standing!")

def step_forward():
    """
    Simulate the robot taking a step forward.
    """
    print("Taking a step forward...")
    
    # Simulate walking sequence
    set_servo(Servos.HIP_RIGHT, 100)
    set_servo(Servos.HIP_LEFT, 100)
    time.sleep(0.5)
    
    set_servo(Servos.KNEE_LEFT, 120)
    time.sleep(0.5)
    
    set_servo(Servos.HIP_LEFT, 70)
    time.sleep(0.5)
    
    set_servo(Servos.KNEE_LEFT, 90)
    time.sleep(0.5)
    
    set_servo(Servos.HIP_RIGHT, 80)
    set_servo(Servos.HIP_LEFT, 80)
    time.sleep(0.5)
    
    set_servo(Servos.KNEE_RIGHT, 120)
    time.sleep(0.5)
    
    set_servo(Servos.HIP_RIGHT, 110)
    time.sleep(0.5)
    
    set_servo(Servos.KNEE_RIGHT, 90)
    time.sleep(0.5)
    
    set_servo(Servos.HIP_RIGHT, 90)
    set_servo(Servos.HIP_LEFT, 90)
    
    print("Step completed!")

def shutdown():
    """
    Simulate shutting down the robot.
    """
    print("Shutting down robot...")
    for servo_index in DEFAULT_POSITIONS.keys():
        current_positions[servo_index] = 90
    print("Robot shutdown complete!")

def get_eye_data():
    """
    Get mock data from the eye sensor.
    
    Returns:
        dict: Dictionary containing simulated distance and ambient light readings
    """
    # Simulate distance between 10 and 200 cm
    distance = random.uniform(10, 200)
    
    # Simulate ambient light between 0 and 255
    light = random.randint(0, 255)
    
    return {
        "distance": distance,
        "ambient_light": light
    } 