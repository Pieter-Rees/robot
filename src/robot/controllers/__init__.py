"""
Robot controller package.
Provides both real and mock implementations of the robot controller.
"""

from .robot_controller import RobotController
from .mock_robot_controller import MockRobotController

__all__ = ['RobotController', 'MockRobotController'] 