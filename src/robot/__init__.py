"""
Robot control package for humanoid robots.
This package provides classes and functions for controlling humanoid robots
using a Raspberry Pi with a PCA9685 servo controller.
"""
import os
import sys
import logging
from pathlib import Path

__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import commonly used classes for easier access
try:
    from .controllers.robot_controller import RobotController
    from .controllers.mock_robot_controller import MockRobotController
    from .config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS
except ImportError as e:
    logger.warning(f"Could not import some components: {e}")

def is_raspberry_pi():
    """
    Check if the code is running on a Raspberry Pi.
    
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise
    """
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return 'raspberry pi' in f.read().lower()
    except FileNotFoundError:
        import platform
        return platform.machine().startswith('arm') or platform.machine().startswith('aarch')
    except Exception as e:
        logger.warning(f"Error checking for Raspberry Pi: {e}")
        return False

def get_controller():
    """
    Get the appropriate controller based on the platform.
    
    Returns:
        BaseRobotController: Either RobotController or MockRobotController
    """
    if is_raspberry_pi():
        logger.info("Using real robot controller (Raspberry Pi detected)")
        return RobotController()
    else:
        logger.info("Using mock robot controller (non-Raspberry Pi environment)")
        return MockRobotController()

def main():
    """
    Entry point for the robot package when used as a command.
    This function starts the main menu from start.py.
    """
    # Add the parent directory to sys.path to import start.py
    parent_dir = str(Path(__file__).parent.parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    try:
        from start import main_menu
        main_menu()
    except ImportError as e:
        logger.error(f"Error importing main menu: {e}")
        print(f"Could not start robot control system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 