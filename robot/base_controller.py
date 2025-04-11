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
        """Initialize the robot and all its components."""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Shutdown the robot and release all resources."""
        pass
    
    @abstractmethod
    def get_eye_data(self):
        """
        Get data from the eye sensor.
        
        Returns:
            dict: Dictionary containing distance and ambient light readings
        """
        pass
    
    def stand_up(self):
        """
        Execute sequence to make the robot stand up from a sitting/lying position.
        """
        # Center all servos
        for servo_index, angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, angle)
        
        # Bend knees
        self.set_servo(Servos.KNEE_RIGHT, 120)
        self.set_servo(Servos.KNEE_LEFT, 120)
        
        # Lean forward slightly
        self.set_servo(Servos.HIP_RIGHT, 110)
        self.set_servo(Servos.HIP_LEFT, 110)
        
        # Straighten knees to stand up
        self.set_servo(Servos.KNEE_RIGHT, 90)
        self.set_servo(Servos.KNEE_LEFT, 90)
        
        # Return hips to center
        self.set_servo(Servos.HIP_RIGHT, 90)
        self.set_servo(Servos.HIP_LEFT, 90)
    
    def step_forward(self):
        """
        Make the robot take a single step forward.
        """
        # Shift weight to right leg
        self.set_servo(Servos.HIP_RIGHT, 100)
        self.set_servo(Servos.HIP_LEFT, 100)
        
        # Lift left leg
        self.set_servo(Servos.KNEE_LEFT, 120)
        
        # Move left leg forward
        self.set_servo(Servos.HIP_LEFT, 70)
        
        # Lower left leg
        self.set_servo(Servos.KNEE_LEFT, 90)
        
        # Shift weight to left leg
        self.set_servo(Servos.HIP_RIGHT, 80)
        self.set_servo(Servos.HIP_LEFT, 80)
        
        # Lift right leg
        self.set_servo(Servos.KNEE_RIGHT, 120)
        
        # Move right leg forward
        self.set_servo(Servos.HIP_RIGHT, 110)
        
        # Lower right leg
        self.set_servo(Servos.KNEE_RIGHT, 90)
        
        # Center hips
        self.set_servo(Servos.HIP_RIGHT, 90)
        self.set_servo(Servos.HIP_LEFT, 90) 