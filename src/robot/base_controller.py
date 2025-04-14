"""
Abstract base class for robot controllers.
Defines the interface that all robot controllers must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional
from robot.config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

class BaseRobotController(ABC):
    """
    Abstract base class for robot controllers.
    Provides common functionality and defines the interface that all controllers must implement.
    """
    
    def __init__(self):
        self.current_positions = DEFAULT_POSITIONS.copy()
        self.movement_queue = []
    
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
    def set_servos(self, positions_dict, speed=0.01):
        """
        Set multiple servos at once to reduce latency.
        
        Args:
            positions_dict (dict): Dictionary mapping servo indices to target angles
            speed (float): Time delay between angle increments
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
    
    def queue_movement(self, positions_dict: Dict[int, float], duration: float = 0.5):
        """
        Queue a movement to be executed later.
        
        Args:
            positions_dict (Dict[int, float]): Dictionary mapping servo indices to target angles
            duration (float): Duration of the movement in seconds
        """
        self.movement_queue.append((positions_dict, duration))
    
    def execute_queue(self):
        """
        Execute all queued movements in sequence.
        """
        for positions, duration in self.movement_queue:
            self.set_servos(positions, speed=duration/len(positions))
        
        # Clear the queue after execution
        self.movement_queue.clear()
    
    def stand_up(self):
        """
        Execute sequence to make the robot stand up from a sitting/lying position.
        This is an optimized version using batched servo movements.
        """
        # Center all servos
        self.set_servos(DEFAULT_POSITIONS)
        
        # Bend knees and lean forward in one movement
        self.set_servos({
            Servos.KNEE_RIGHT: 120,
            Servos.KNEE_LEFT: 120,
            Servos.HIP_RIGHT: 110,
            Servos.HIP_LEFT: 110
        })
        
        # Straighten knees to stand up and center hips in one movement
        self.set_servos({
            Servos.KNEE_RIGHT: 90,
            Servos.KNEE_LEFT: 90,
            Servos.HIP_RIGHT: 90,
            Servos.HIP_LEFT: 90
        })
    
    def balance_correction(self, accel_data: Optional[Tuple[float, float, float]] = None):
        """
        Apply balance correction based on accelerometer data.
        
        Args:
            accel_data (Tuple[float, float, float], optional): 
                Accelerometer data (x, y, z) if available.
                If None, the method will attempt to get data from the sensor.
        
        Returns:
            bool: True if correction was applied, False otherwise
        """
        # This is a placeholder - concrete implementations should override this
        # with actual balance correction logic using accelerometer data
        return False
    
    def step_forward(self):
        """
        Make the robot take a single step forward.
        Optimized version using batched servo movements.
        """
        # Shift weight to right leg
        self.set_servos({
            Servos.HIP_RIGHT: 100,
            Servos.HIP_LEFT: 100
        })
        
        # Lift left leg and move forward
        self.set_servos({
            Servos.KNEE_LEFT: 120,
            Servos.HIP_LEFT: 70
        })
        
        # Lower left leg
        self.set_servos({
            Servos.KNEE_LEFT: 90
        })
        
        # Shift weight to left leg
        self.set_servos({
            Servos.HIP_RIGHT: 80,
            Servos.HIP_LEFT: 80
        })
        
        # Lift right leg and move forward
        self.set_servos({
            Servos.KNEE_RIGHT: 120,
            Servos.HIP_RIGHT: 110
        })
        
        # Lower right leg
        self.set_servos({
            Servos.KNEE_RIGHT: 90
        })
        
        # Center hips
        self.set_servos({
            Servos.HIP_RIGHT: 90,
            Servos.HIP_LEFT: 90
        })
    
    def walk_forward(self, steps: int = 3):
        """
        Make the robot walk forward a specified number of steps.
        
        Args:
            steps (int): Number of steps to take
        """
        for _ in range(steps):
            self.step_forward()

    def dance(self):
        """
        Execute a fun dance sequence.
        The dance consists of a series of movements that make the robot appear to dance.
        """
        # Initial pose
        self.set_servos(DEFAULT_POSITIONS)
        
        # Dance sequence
        # 1. Rock side to side
        for _ in range(2):
            self.set_servos({
                Servos.HIP_RIGHT: 70,
                Servos.HIP_LEFT: 110
            })
            self.set_servos({
                Servos.HIP_RIGHT: 110,
                Servos.HIP_LEFT: 70
            })
        
        # 2. Knee bends
        for _ in range(2):
            self.set_servos({
                Servos.KNEE_RIGHT: 120,
                Servos.KNEE_LEFT: 120
            })
            self.set_servos({
                Servos.KNEE_RIGHT: 90,
                Servos.KNEE_LEFT: 90
            })
        
        # 3. Twist and turn
        for _ in range(2):
            self.set_servos({
                Servos.HIP_RIGHT: 60,
                Servos.HIP_LEFT: 60
            })
            self.set_servos({
                Servos.HIP_RIGHT: 120,
                Servos.HIP_LEFT: 120
            })
        
        # 4. Final pose
        self.set_servos(DEFAULT_POSITIONS) 