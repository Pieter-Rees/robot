#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
from Adafruit_PCA9685 import PCA9685
from ..base_controller import BaseRobotController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

class RobotController(BaseRobotController):
    """
    Real robot controller implementation using PCA9685 servo controller.
    """
    def __init__(self):
        super().__init__()
        # Initialize the PCA9685 with default address (0x40)
        self.pwm = PCA9685()
        self.pwm.set_pwm_freq(50)  # Set PWM frequency to 50Hz (standard for servos)
    
    def initialize_robot(self):
        """
        Initialize the robot and all its components.
        """
        print("Initializing robot...")
        
        # Center all servos
        for servo_index, angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, angle)
        
        print("Robot initialization complete!")
    
    def shutdown(self):
        """
        Shutdown the robot and release all resources.
        """
        print("Shutting down robot...")
        
        # Center all servos
        for servo_index, angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, angle)
        
        print("Robot shutdown complete!")
    
    def dance(self):
        """
        Execute a dance sequence combining various movements.
        """
        print("Starting dance routine!")
        
        # Initial pose
        self.set_servo(Servos.HEAD, 90)
        self.set_servo(Servos.SHOULDER_RIGHT, 60)
        self.set_servo(Servos.SHOULDER_LEFT, 120)
        self.set_servo(Servos.ELBOW_RIGHT, 120)
        self.set_servo(Servos.ELBOW_LEFT, 60)
        time.sleep(1)
        
        # First move: Rocking side to side with arms
        for _ in range(3):
            self.set_servo(Servos.HIP_RIGHT, 70)
            self.set_servo(Servos.HIP_LEFT, 110)
            self.set_servo(Servos.SHOULDER_RIGHT, 80)
            self.set_servo(Servos.SHOULDER_LEFT, 100)
            time.sleep(0.4)
            self.set_servo(Servos.HIP_RIGHT, 110)
            self.set_servo(Servos.HIP_LEFT, 70)
            self.set_servo(Servos.SHOULDER_RIGHT, 40)
            self.set_servo(Servos.SHOULDER_LEFT, 140)
            time.sleep(0.4)
        
        # Second move: Head bobbing with arm waves
        for _ in range(2):
            self.set_servo(Servos.HEAD, 70)
            self.set_servo(Servos.ELBOW_RIGHT, 150)
            self.set_servo(Servos.ELBOW_LEFT, 30)
            time.sleep(0.3)
            self.set_servo(Servos.HEAD, 110)
            self.set_servo(Servos.ELBOW_RIGHT, 90)
            self.set_servo(Servos.ELBOW_LEFT, 90)
            time.sleep(0.3)
        
        # Third move: Full body twist
        for _ in range(2):
            self.set_servo(Servos.HIP_RIGHT, 60)
            self.set_servo(Servos.HIP_LEFT, 120)
            self.set_servo(Servos.SHOULDER_RIGHT, 40)
            self.set_servo(Servos.SHOULDER_LEFT, 140)
            self.set_servo(Servos.HEAD, 60)
            time.sleep(0.5)
            self.set_servo(Servos.HIP_RIGHT, 120)
            self.set_servo(Servos.HIP_LEFT, 60)
            self.set_servo(Servos.SHOULDER_RIGHT, 140)
            self.set_servo(Servos.SHOULDER_LEFT, 40)
            self.set_servo(Servos.HEAD, 120)
            time.sleep(0.5)
        
        # Final pose
        self.set_servo(Servos.HEAD, 90)
        self.set_servo(Servos.SHOULDER_RIGHT, 60)
        self.set_servo(Servos.SHOULDER_LEFT, 120)
        self.set_servo(Servos.ELBOW_RIGHT, 120)
        self.set_servo(Servos.ELBOW_LEFT, 60)
        self.set_servo(Servos.HIP_RIGHT, 90)
        self.set_servo(Servos.HIP_LEFT, 90)
        time.sleep(1)
        
        print("Dance routine completed!")

if __name__ == "__main__":
    try:
        # Example usage
        controller = RobotController()
        controller.initialize_robot()
        time.sleep(2)
        
        controller.dance()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        controller.shutdown() 