"""
Robot package for controlling a humanoid robot.
Provides interfaces for both real and mock robot controllers.
"""

from robot.base_controller import BaseRobotController
from robot.config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

__all__ = ['BaseRobotController', 'Servos', 'DEFAULT_POSITIONS', 'SERVO_LIMITS'] 