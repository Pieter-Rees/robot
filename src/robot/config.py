"""
Configuration file for the robot project.
Contains shared constants and configurations used across different modules.
"""

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