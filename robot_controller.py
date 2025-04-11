#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
from Adafruit_PCA9685 import PCA9685
from sensors import OT703C86

# Initialize the PCA9685 with default address (0x40)
pwm = PCA9685()
pwm.set_pwm_freq(50)  # Set PWM frequency to 50Hz (standard for servos)

# Initialize the OT703-C86 sensor
eye_sensor = OT703C86()

# Define servo indices for each joint
class Servos:
    """
    Constants defining servo motor indices for each joint in the robot.
    """
    # Example servo mapping - adjust according to your robot's configuration
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
# Values are in degrees - adjust these based on your servos and robot's needs
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
    # Format: servo_index: (min_angle, max_angle)
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

def set_servo(servo_index, angle, speed=0.01):
    """
    Set a servo to a specific angle with controlled speed.
    
    Args:
        servo_index (int): Index of the servo to control
        angle (float): Target angle in degrees
        speed (float): Time delay between angle increments (lower = faster)
    """
    # Apply safety limits
    min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
    safe_angle = max(min_angle, min(max_angle, angle))
    
    # Convert angle to PWM value (0-4095)
    # Servos typically use 1ms to 2ms pulse width (0-180 degrees)
    # For 50Hz (20ms period), this is 5% to 10% duty cycle
    # 4095 * 0.05 = 205 (0 degrees)
    # 4095 * 0.10 = 410 (180 degrees)
    pwm_value = int(205 + (safe_angle / 180.0) * 205)
    
    # Get current position
    current_angle = DEFAULT_POSITIONS.get(servo_index, 90)
    
    # Gradually move to target position
    if current_angle < safe_angle:
        for a in range(int(current_angle), int(safe_angle) + 1):
            pwm_value = int(205 + (a / 180.0) * 205)
            pwm.set_pwm(servo_index, 0, pwm_value)
            time.sleep(speed)
    else:
        for a in range(int(current_angle), int(safe_angle) - 1, -1):
            pwm_value = int(205 + (a / 180.0) * 205)
            pwm.set_pwm(servo_index, 0, pwm_value)
            time.sleep(speed)

def initialize_robot():
    """
    Initialize the robot and all its components.
    """
    print("Initializing robot...")
    
    # Initialize the eye sensor
    if not eye_sensor.initialize():
        print("Warning: Failed to initialize eye sensor")
    
    # Center all servos
    for servo_index, angle in DEFAULT_POSITIONS.items():
        set_servo(servo_index, angle)
    
    print("Robot initialization complete!")

def stand_up():
    """
    Execute sequence to make the robot stand up from a sitting/lying position.
    """
    print("Standing up...")
    
    # This is a simplified stand-up sequence
    # Actual sequence depends on robot's initial position and joint configuration
    
    # First, center all servos
    for servo_index, angle in DEFAULT_POSITIONS.items():
        set_servo(servo_index, angle)
    
    # Bend knees
    set_servo(Servos.KNEE_RIGHT, 120)
    set_servo(Servos.KNEE_LEFT, 120)
    time.sleep(0.5)
    
    # Lean forward slightly
    set_servo(Servos.HIP_RIGHT, 110)
    set_servo(Servos.HIP_LEFT, 110)
    time.sleep(0.5)
    
    # Straighten knees to stand up
    set_servo(Servos.KNEE_RIGHT, 90)
    set_servo(Servos.KNEE_LEFT, 90)
    time.sleep(0.5)
    
    # Return hips to center
    set_servo(Servos.HIP_RIGHT, 90)
    set_servo(Servos.HIP_LEFT, 90)
    
    print("Robot is now standing!")

def step_forward():
    """
    Make the robot take a single step forward.
    """
    print("Taking a step forward...")
    
    # Shift weight to right leg
    set_servo(Servos.HIP_RIGHT, 100)
    set_servo(Servos.HIP_LEFT, 100)
    time.sleep(0.5)
    
    # Lift left leg
    set_servo(Servos.KNEE_LEFT, 120)
    time.sleep(0.5)
    
    # Move left leg forward
    set_servo(Servos.HIP_LEFT, 70)
    time.sleep(0.5)
    
    # Lower left leg
    set_servo(Servos.KNEE_LEFT, 90)
    time.sleep(0.5)
    
    # Shift weight to left leg
    set_servo(Servos.HIP_RIGHT, 80)
    set_servo(Servos.HIP_LEFT, 80)
    time.sleep(0.5)
    
    # Lift right leg
    set_servo(Servos.KNEE_RIGHT, 120)
    time.sleep(0.5)
    
    # Move right leg forward
    set_servo(Servos.HIP_RIGHT, 110)
    time.sleep(0.5)
    
    # Lower right leg
    set_servo(Servos.KNEE_RIGHT, 90)
    time.sleep(0.5)
    
    # Center hips
    set_servo(Servos.HIP_RIGHT, 90)
    set_servo(Servos.HIP_LEFT, 90)
    
    print("Step completed!")

def shutdown():
    """
    Shutdown the robot and release all resources.
    """
    print("Shutting down robot...")
    
    # Shutdown the eye sensor
    eye_sensor.shutdown()
    
    # Center all servos
    for servo_index, angle in DEFAULT_POSITIONS.items():
        set_servo(servo_index, angle)
    
    print("Robot shutdown complete!")

def get_eye_data():
    """
    Get data from the eye sensor.
    
    Returns:
        dict: Dictionary containing distance and ambient light readings
    """
    distance = eye_sensor.read_distance()
    light = eye_sensor.read_ambient_light()
    
    return {
        "distance": distance,
        "ambient_light": light
    }

def dance():
    """
    Execute a dance sequence combining various movements.
    """
    print("Starting dance routine!")
    
    # Initial pose
    set_servo(Servos.HEAD, 90)
    set_servo(Servos.SHOULDER_RIGHT, 60)
    set_servo(Servos.SHOULDER_LEFT, 120)
    set_servo(Servos.ELBOW_RIGHT, 120)
    set_servo(Servos.ELBOW_LEFT, 60)
    time.sleep(1)
    
    # First move: Rocking side to side
    for _ in range(3):
        set_servo(Servos.HIP_RIGHT, 70)
        set_servo(Servos.HIP_LEFT, 110)
        time.sleep(0.5)
        set_servo(Servos.HIP_RIGHT, 110)
        set_servo(Servos.HIP_LEFT, 70)
        time.sleep(0.5)
    
    # Second move: Arm wave
    for _ in range(2):
        set_servo(Servos.SHOULDER_RIGHT, 30)
        set_servo(Servos.ELBOW_RIGHT, 150)
        time.sleep(0.3)
        set_servo(Servos.SHOULDER_RIGHT, 90)
        set_servo(Servos.ELBOW_RIGHT, 90)
        time.sleep(0.3)
        set_servo(Servos.SHOULDER_LEFT, 150)
        set_servo(Servos.ELBOW_LEFT, 30)
        time.sleep(0.3)
        set_servo(Servos.SHOULDER_LEFT, 90)
        set_servo(Servos.ELBOW_LEFT, 90)
        time.sleep(0.3)
    
    # Third move: Head bobbing with knee bends
    for _ in range(4):
        set_servo(Servos.HEAD, 60)
        set_servo(Servos.KNEE_RIGHT, 120)
        set_servo(Servos.KNEE_LEFT, 120)
        time.sleep(0.3)
        set_servo(Servos.HEAD, 120)
        set_servo(Servos.KNEE_RIGHT, 60)
        set_servo(Servos.KNEE_LEFT, 60)
        time.sleep(0.3)
    
    # Final pose
    set_servo(Servos.HEAD, 90)
    set_servo(Servos.SHOULDER_RIGHT, 120)
    set_servo(Servos.SHOULDER_LEFT, 60)
    set_servo(Servos.ELBOW_RIGHT, 60)
    set_servo(Servos.ELBOW_LEFT, 120)
    set_servo(Servos.HIP_RIGHT, 90)
    set_servo(Servos.HIP_LEFT, 90)
    set_servo(Servos.KNEE_RIGHT, 90)
    set_servo(Servos.KNEE_LEFT, 90)
    time.sleep(1)
    
    print("Dance routine completed!")

if __name__ == "__main__":
    try:
        # Example usage
        initialize_robot()
        time.sleep(2)
        
        stand_up()
        time.sleep(2)
        
        # Uncomment to test dancing
        dance()
        
        # Uncomment to test walking
        # step_forward()
        # time.sleep(1)
        # step_forward()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        shutdown() 