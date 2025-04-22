#!/usr/bin/env python3
"""
Mock Robot Controller module for testing and development without hardware.
Provides a simulation of the real RobotController for software development.
"""
import time
import platform
import random
from ..base_controller import BaseRobotController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

class MockRobotController(BaseRobotController):
    """
    Mock implementation of the robot controller for testing and development.
    Simulates the behavior of the real controller without requiring hardware.
    """
    def __init__(self, config=None):
        super().__init__()
        self.initialized = False
        self.current_positions = DEFAULT_POSITIONS.copy()
        self._pwm_cache = {}  # Cache for PWM values
        self.config = config
        
        # Flag to indicate if the controller is initialized
        self.is_initialized = False
        
        # Set platform for informational purposes
        self.platform = platform.system()
        print(f"Running on: {self.platform}")
    
    def _angle_to_pwm(self, angle):
        """Convert angle to PWM value with caching."""
        if angle not in self._pwm_cache:
            self._pwm_cache[angle] = int(205 + (angle / 180.0) * 205)
        return self._pwm_cache[angle]
    
    def set_servo(self, servo_index, angle, speed=0.01):
        """
        Simulate setting a servo to a specific angle.
        
        Args:
            servo_index (int): Index of the servo to control
            angle (float): Target angle in degrees
            speed (float): Time delay between angle increments (lower = faster)
        """
        # Apply safety limits
        min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
        safe_angle = max(min_angle, min(max_angle, angle))
        
        # Get current position
        current_angle = self.current_positions.get(servo_index, 90)
        
        # Calculate step direction and range
        step = 1 if current_angle < safe_angle else -1
        start = int(current_angle)
        end = int(safe_angle) + step
        
        # Simulate gradual movement
        for a in range(start, end, step):
            self.current_positions[servo_index] = a
            time.sleep(speed)
        
        print(f"Servo {servo_index} moved to {safe_angle} degrees")
    
    def _move_to_default_positions(self, speed=0.01):
        """Move all servos to their default positions."""
        for servo_index, default_angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, default_angle, speed=speed)

    def initialize_robot(self):
        """Simulate initializing the robot to default positions."""
        if not self.initialized:
            self._move_to_default_positions()
            self.initialized = True

    def stand_up(self):
        """Simulate standing up."""
        if not self.initialized:
            return False
            
        try:
            self._move_to_default_positions()
            return True
        except Exception:
            return False

    def shutdown(self):
        """Simulate shutting down the robot."""
        try:
            self._move_to_default_positions()
            self.initialized = False
        except Exception:
            pass  # Ensure shutdown completes even if errors occur
    
    def dance(self):
        """Simulate a dance routine."""
        # Define dance sequences with minimal memory usage
        sequences = (
            # Initial pose
            ((Servos.HEAD, 90), (Servos.SHOULDER_RIGHT, 60), (Servos.SHOULDER_LEFT, 120),
             (Servos.ELBOW_RIGHT, 120), (Servos.ELBOW_LEFT, 60)),
            # First move: Rocking side to side with arms
            ((Servos.HIP_RIGHT, 70), (Servos.HIP_LEFT, 110), (Servos.SHOULDER_RIGHT, 80),
             (Servos.SHOULDER_LEFT, 100)),
            ((Servos.HIP_RIGHT, 110), (Servos.HIP_LEFT, 70), (Servos.SHOULDER_RIGHT, 40),
             (Servos.SHOULDER_LEFT, 140)),
            # Second move: Head bobbing with arm waves
            ((Servos.HEAD, 70), (Servos.ELBOW_RIGHT, 150), (Servos.ELBOW_LEFT, 30)),
            ((Servos.HEAD, 110), (Servos.ELBOW_RIGHT, 90), (Servos.ELBOW_LEFT, 90)),
            # Third move: Full body twist
            ((Servos.HIP_RIGHT, 60), (Servos.HIP_LEFT, 120), (Servos.SHOULDER_RIGHT, 40),
             (Servos.SHOULDER_LEFT, 140), (Servos.HEAD, 60)),
            ((Servos.HIP_RIGHT, 120), (Servos.HIP_LEFT, 60), (Servos.SHOULDER_RIGHT, 140),
             (Servos.SHOULDER_LEFT, 40), (Servos.HEAD, 120)),
            # Final pose
            ((Servos.HEAD, 90), (Servos.SHOULDER_RIGHT, 60), (Servos.SHOULDER_LEFT, 120),
             (Servos.ELBOW_RIGHT, 120), (Servos.ELBOW_LEFT, 60), (Servos.HIP_RIGHT, 90),
             (Servos.HIP_LEFT, 90))
        )
        
        # Execute dance sequences
        for sequence in sequences:
            # Move all servos in the sequence simultaneously
            for servo_index, angle in sequence:
                self.set_servo(servo_index, angle, speed=0.01)
        # Simulate some basic movements
        for _ in range(3):
            self.set_servo(Servos.HEAD, 70)
            self.set_servo(Servos.SHOULDER_RIGHT, 60)
            time.sleep(0.5)
            self.set_servo(Servos.HEAD, 110)
            self.set_servo(Servos.SHOULDER_LEFT, 120)
            time.sleep(0.5)
        
        print("Mock dance routine completed!")
    
    def step_forward(self):
        """Simulate taking a step forward."""
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

if __name__ == "__main__":
    try:
        # Example usage
        controller = MockRobotController()
        controller.initialize_robot()
        time.sleep(2)
        
        controller.stand_up()
        time.sleep(2)
        
        controller.step_forward()
        time.sleep(2)
        
        controller.dance()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        controller.shutdown() 