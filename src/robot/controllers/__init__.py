"""
Robot controller package.
Provides both real and mock implementations of the robot controller.
"""

from .robot_controller import RobotController
from .mock_robot_controller import MockRobotController
from .controller_factory import create_controller, is_raspberry_pi

__all__ = ['RobotController', 'MockRobotController', 'create_controller', 'is_raspberry_pi'] 