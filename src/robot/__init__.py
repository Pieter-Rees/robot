"""
Robot Controller Package

A Python-based controller for a humanoid robot using the PCA9685 servo controller.
"""

__version__ = "0.1.0"

# Expose main interfaces
from .controllers.robot_controller import RobotController
from .controllers.mock_robot_controller import MockRobotController
from .controllers.controller_factory import create_controller, is_raspberry_pi
from .web.web_server import app as web_app
from .calibration import run_calibration

__all__ = [
    'RobotController',
    'MockRobotController',
    'create_controller',
    'is_raspberry_pi',
    'web_app',
    'run_calibration',
] 