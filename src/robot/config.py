"""
Configuration management for the humanoid robot.
Provides centralized configuration handling with type safety.
"""
import platform
import json
import os
from pathlib import Path
from typing import Dict, Tuple, Optional, Any, TypedDict

class ServoConfig(TypedDict):
    """Type definition for servo configuration."""
    min_angle: int
    max_angle: int
    default_position: int

class I2CConfig(TypedDict):
    """Type definition for I2C configuration."""
    default_bus: int
    pca9685_address: int

class Config:
    """Centralized configuration management for the robot."""
    
    _instance: Optional['Config'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Config':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration if not already initialized."""
        if not self._initialized:
            self._i2c_config: I2CConfig = self._get_i2c_config()
            self._servo_config: Dict[int, ServoConfig] = self._init_servo_config()
            self._calibrated_positions: Dict[int, int] = self._load_calibration()
            self._initialized = True
    
    @staticmethod
    def _get_i2c_config() -> I2CConfig:
        """Get platform-specific I2C configuration."""
        system = platform.system()
        
        if system == 'Linux':
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    if 'raspberry pi' in f.read().lower():
                        return {
                            'default_bus': 1,
                            'pca9685_address': 0x40
                        }
            except:
                pass
        
        # Default configuration for non-RPi platforms
        return {
            'default_bus': 0,
            'pca9685_address': 0x40
        }
    
    def _init_servo_config(self) -> Dict[int, ServoConfig]:
        """Initialize servo configuration with limits and defaults."""
        return {
            Servos.HEAD: {'min_angle': 45, 'max_angle': 135, 'default_position': 90},
            Servos.SHOULDER_RIGHT: {'min_angle': 30, 'max_angle': 150, 'default_position': 90},
            Servos.SHOULDER_LEFT: {'min_angle': 30, 'max_angle': 150, 'default_position': 90},
            Servos.ELBOW_RIGHT: {'min_angle': 60, 'max_angle': 180, 'default_position': 90},
            Servos.ELBOW_LEFT: {'min_angle': 0, 'max_angle': 120, 'default_position': 90},
            Servos.HIP_RIGHT: {'min_angle': 60, 'max_angle': 120, 'default_position': 90},
            Servos.HIP_LEFT: {'min_angle': 60, 'max_angle': 120, 'default_position': 90},
            Servos.KNEE_RIGHT: {'min_angle': 60, 'max_angle': 120, 'default_position': 90},
            Servos.KNEE_LEFT: {'min_angle': 60, 'max_angle': 120, 'default_position': 90},
            Servos.ANKLE_RIGHT: {'min_angle': 60, 'max_angle': 120, 'default_position': 90},
            Servos.ANKLE_LEFT: {'min_angle': 60, 'max_angle': 120, 'default_position': 90},
            Servos.WRIST_RIGHT: {'min_angle': 30, 'max_angle': 150, 'default_position': 90},
            Servos.WRIST_LEFT: {'min_angle': 30, 'max_angle': 150, 'default_position': 90}
        }
    
    def _load_calibration(self) -> Dict[int, int]:
        """Load calibrated positions from configuration files."""
        config_paths = [
            Path('/etc/robot/servo_calibration.json'),
            Path.home() / '.robot' / 'servo_calibration.json'),
            Path(__file__).parent / 'config' / 'servo_calibration.json'
        ]
        
        for config_path in config_paths:
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    named_positions = data['calibrated_positions']
                    
                    # Convert names to indices
                    return {
                        getattr(Servos, name): pos
                        for name, pos in named_positions.items()
                        if hasattr(Servos, name)
                    }
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                continue
        
        # Return default positions if no calibration found
        return {
            servo_id: config['default_position']
            for servo_id, config in self._servo_config.items()
        }
    
    @property
    def i2c(self) -> I2CConfig:
        """Get I2C configuration."""
        return self._i2c_config
    
    def get_servo_config(self, servo_id: int) -> ServoConfig:
        """Get configuration for a specific servo."""
        if servo_id not in self._servo_config:
            raise ValueError(f"Invalid servo ID: {servo_id}")
        return self._servo_config[servo_id]
    
    def get_servo_limits(self, servo_id: int) -> Tuple[int, int]:
        """Get angle limits for a specific servo."""
        config = self.get_servo_config(servo_id)
        return config['min_angle'], config['max_angle']
    
    def get_calibrated_position(self, servo_id: int) -> int:
        """Get calibrated position for a specific servo."""
        return self._calibrated_positions.get(
            servo_id,
            self._servo_config[servo_id]['default_position']
        )
    
    def get_all_calibrated_positions(self) -> Dict[int, int]:
        """Get all calibrated positions."""
        return self._calibrated_positions.copy()

class Servos:
    """Constants defining servo motor indices for each joint."""
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

# Create global configuration instance
config = Config()

# Backwards compatibility exports
I2C_CONFIG = config.i2c
DEFAULT_POSITIONS = {
    servo_id: cfg['default_position']
    for servo_id, cfg in config._servo_config.items()
}
SERVO_LIMITS = {
    servo_id: (cfg['min_angle'], cfg['max_angle'])
    for servo_id, cfg in config._servo_config.items()
}
CALIBRATED_POSITIONS = config.get_all_calibrated_positions() 