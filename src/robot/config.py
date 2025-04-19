"""
Configuration file for the humanoid robot.
Defines servo indices, limits, and default positions.
"""
import platform

# Platform-specific I2C configuration
def get_i2c_config():
    """
    Get platform-specific I2C configuration.
    
    Returns:
        dict: Dictionary with I2C configuration for the current platform
    """
    system = platform.system()
    
    if system == 'Linux':
        # For Raspberry Pi
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if 'raspberry pi' in model:
                    # Standard RPi configuration
                    return {
                        'default_bus': 1,
                        'pca9685_address': 0x40
                    }
        except:
            pass
        
        # Generic Linux
        return {
            'default_bus': 1,
            'pca9685_address': 0x40
        }
    
    elif system == 'Windows':
        # Windows mock configuration
        return {
            'default_bus': 0,  # Mock value for Windows
            'pca9685_address': 0x40
        }
    
    else:
        # Default configuration for other platforms
        return {
            'default_bus': 0,
            'pca9685_address': 0x40
        }

# Get the I2C configuration
I2C_CONFIG = get_i2c_config()

# Servo indices (channels on the PCA9685)
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
    Servos.ELBOW_RIGHT: (60, 180),
    Servos.ELBOW_LEFT: (0, 120),
    Servos.HIP_RIGHT: (60, 120),
    Servos.HIP_LEFT: (60, 120),
    Servos.KNEE_RIGHT: (60, 120),
    Servos.KNEE_LEFT: (60, 120),
    Servos.ANKLE_RIGHT: (60, 120),
    Servos.ANKLE_LEFT: (60, 120),
    Servos.WRIST_RIGHT: (30, 150),
    Servos.WRIST_LEFT: (30, 150)
} 