"""
Robot Controller Package

A Python-based controller for a humanoid robot using the PCA9685 servo controller.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Expose main interfaces
from .controllers.controller_factory import create_controller, is_raspberry_pi
from .web.web_server import app as web_app
from .base_controller import BaseRobotController
from .config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS, I2C_CONFIG

__all__ = [
    'create_controller',
    'is_raspberry_pi',
    'web_app',
    'BaseRobotController',
    'Servos',
    'DEFAULT_POSITIONS',
    'SERVO_LIMITS',
    'I2C_CONFIG',
] 