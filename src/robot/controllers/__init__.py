"""
Robot controller package.
Provides both real and mock implementations of the robot controller.
"""

from .controller_factory import create_controller, is_raspberry_pi

__all__ = ['create_controller', 'is_raspberry_pi'] 