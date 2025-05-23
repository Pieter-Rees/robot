"""
Configuration file for the humanoid robot.
Defines servo indices, limits, and default positions.
"""
import platform
import json
import os
from typing import Dict

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
        # Other platforms (macOS, etc.)
        return {
            'default_bus': 0,  # Mock value
            'pca9685_address': 0x40
        }

# Export I2C configuration
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
    Servos.HEAD: (0, 180),
    Servos.SHOULDER_RIGHT: (0, 180),
    Servos.SHOULDER_LEFT: (0, 180),
    Servos.ELBOW_RIGHT: (0, 180),
    Servos.ELBOW_LEFT: (0, 180),
    Servos.HIP_RIGHT: (0, 180),
    Servos.HIP_LEFT: (0, 180),
    Servos.KNEE_RIGHT: (0, 180),
    Servos.KNEE_LEFT: (0, 180),
    Servos.ANKLE_RIGHT: (0, 180),
    Servos.ANKLE_LEFT: (0, 180),
    Servos.WRIST_RIGHT: (0, 180),
    Servos.WRIST_LEFT: (0, 180)
}

def load_calibrated_positions() -> Dict[int, int]:
    """
    Load calibrated positions from the JSON file.
    Returns a dictionary mapping servo indices to their calibrated positions.
    """
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'servo_calibration.json')
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            named_positions = data['calibrated_positions']
            
            # Convert names back to indices
            calibrated_positions = {}
            for servo_name, servo_index in vars(Servos).items():
                if not servo_name.startswith('_') and servo_name in named_positions:
                    calibrated_positions[servo_index] = named_positions[servo_name]
            
            return calibrated_positions
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return DEFAULT_POSITIONS.copy()

# Load calibrated positions
CALIBRATED_POSITIONS = load_calibrated_positions()

class Config:
    """Configuration class for the robot."""
    def __init__(self):
        self.i2c_config = I2C_CONFIG
        self.default_positions = DEFAULT_POSITIONS
        self.servo_limits = SERVO_LIMITS
        self.calibrated_positions = CALIBRATED_POSITIONS

    def get_servo_config(self, servo_id: int) -> dict:
        """
        Get configuration for a specific servo.
        
        Args:
            servo_id: The ID of the servo
            
        Returns:
            dict: Configuration including min_angle, max_angle, and default position
            
        Raises:
            ValueError: If servo_id is invalid
        """
        if servo_id not in self.servo_limits:
            raise ValueError(f"Invalid servo ID: {servo_id}")
            
        min_angle, max_angle = self.servo_limits[servo_id]
        return {
            'min_angle': min_angle,
            'max_angle': max_angle,
            'default_position': self.default_positions[servo_id],
            'calibrated_position': self.calibrated_positions.get(servo_id, 
                                                              self.default_positions[servo_id])
        }

# Create global config instance
config = Config() 