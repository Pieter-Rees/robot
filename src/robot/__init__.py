"""
Robot Controller Package

A Python-based controller for a humanoid robot using the PCA9685 servo controller.
"""

__version__ = "0.1.0"

# Expose main interfaces
from .controllers.robot_controller import RobotController
from .controllers.mock_robot_controller import MockRobotController
from .controllers.controller_factory import create_controller, is_raspberry_pi
from .sensors import OT703C86, MPU6050
from .web.web_server import app as web_app

__all__ = [
    'RobotController',
    'MockRobotController',
    'create_controller',
    'is_raspberry_pi',
    'OT703C86',
    'MPU6050',
    'web_app',
] 