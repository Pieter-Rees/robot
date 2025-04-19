"""
Abstract base class for robot controllers.
Defines the interface that all robot controllers must implement.
"""
from abc import ABC, abstractmethod
from robot.config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

class BaseRobotController(ABC):
    """
    Abstract base class for robot controllers.
    Provides common functionality and defines the interface that all controllers must implement.
    """
    
    def __init__(self):
        self.current_positions = DEFAULT_POSITIONS.copy()
    
    @abstractmethod
    def set_servo(self, servo_index, angle, speed=0.01):
        """
        Set a servo to a specific angle with controlled speed.
        
        Args:
            servo_index (int): Index of the servo to control
            angle (float): Target angle in degrees
            speed (float): Time delay between angle increments (lower = faster)
        """
        pass
    
    @abstractmethod
    def initialize_robot(self):
        """
        Initialize the robot controller and prepare for operation.
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """
        Shutdown the robot controller and release resources.
        """
        pass
    
    def stand_up(self):
        """
        Move the robot to a standing position.
        """
        for servo_index, default_angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, default_angle)
    
    def step_forward(self):
        """
        Make the robot take a step forward.
        """
        # Step forward sequence implementation
        pass
    
    def dance(self):
        """
        Perform a dance sequence.
        """
        # Dance sequence implementation
        pass 