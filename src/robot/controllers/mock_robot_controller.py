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
        print("Initializing Mock Robot Controller (no hardware required)")
        
        # Store config for reference
        self.config = config
        
        # Flag to indicate if the controller is initialized
        self.is_initialized = False
        
        # Set platform for informational purposes
        self.platform = platform.system()
        print(f"Running on: {self.platform}")
    
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
        
        # Simulate gradual movement
        if current_angle < safe_angle:
            for a in range(int(current_angle), int(safe_angle) + 1):
                self.current_positions[servo_index] = a
                time.sleep(speed)
        else:
            for a in range(int(current_angle), int(safe_angle) - 1, -1):
                self.current_positions[servo_index] = a
                time.sleep(speed)
        
        print(f"Servo {servo_index} moved to {safe_angle} degrees")
    
    def initialize_robot(self):
        """
        Simulate initializing the robot to default positions.
        """
        print("Initializing robot to default position...")
        for servo_index, angle in DEFAULT_POSITIONS.items():
            self.current_positions[servo_index] = angle
            time.sleep(0.1)
        print("Robot initialized!")
    
    def shutdown(self):
        """
        Simulate shutting down the robot.
        """
        print("Shutting down robot...")
        for servo_index in DEFAULT_POSITIONS.keys():
            self.current_positions[servo_index] = 90
        print("Robot shutdown complete!")
    
    def dance(self):
        """Simulate a dance routine."""
        print("Starting mock dance routine!")
        
        # Simulate some basic movements
        for _ in range(3):
            self.set_servo(Servos.HEAD, 70)
            self.set_servo(Servos.SHOULDER_RIGHT, 60)
            time.sleep(0.5)
            self.set_servo(Servos.HEAD, 110)
            self.set_servo(Servos.SHOULDER_LEFT, 120)
            time.sleep(0.5)
        
        print("Mock dance routine completed!")
    
    def stand_up(self):
        """Simulate standing up."""
        print("Mock robot standing up...")
        for servo_index, default_angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, default_angle)
        print("Mock robot is standing")
    
    def step_forward(self):
        """Simulate taking a step forward."""
        print("Mock robot stepping forward...")
        
        # Simulate leg movement
        self.set_servo(Servos.HIP_RIGHT, 60)
        self.set_servo(Servos.KNEE_RIGHT, 120)
        time.sleep(0.5)
        
        self.set_servo(Servos.HIP_LEFT, 120)
        self.set_servo(Servos.KNEE_LEFT, 60)
        time.sleep(0.5)
        
        # Return to standing position
        self.stand_up()
        print("Mock robot step completed")

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