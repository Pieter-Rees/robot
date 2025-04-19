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
    def __init__(self):
        super().__init__()
        print("Initializing Mock Robot Controller (no hardware required)")
        
        # Mock sensor data
        self.mock_distance = 50.0  # Initial distance in cm
        self.mock_light = 128  # Initial light level (0-255)
        self.mock_accel = (0.0, 0.0, 1.0)  # Initial accelerometer data (x, y, z)
        self.mock_gyro = (0.0, 0.0, 0.0)  # Initial gyroscope data (x, y, z)
        
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
        Shutdown the mock robot controller.
        """
        print("Shutting down mock robot controller")
        self.initialized = False
    
    def get_eye_data(self):
        """
        Get mock data from the eye sensor.
        
        Returns:
            dict: Dictionary containing simulated distance and ambient light readings
        """
        # Simulate distance between 10 and 200 cm
        distance = random.uniform(10, 200)
        
        # Simulate ambient light between 0 and 255
        light = random.randint(0, 255)
        
        return {
            "distance": distance,
            "ambient_light": light
        }

    def get_mpu6050_data(self):
        """
        Get mock data from the MPU-6050 sensor.
        
        Returns:
            dict: Dictionary containing simulated accelerometer and gyroscope readings
        """
        # Simulate accelerometer data (±2g range)
        accel_x = random.uniform(-2.0, 2.0)
        accel_y = random.uniform(-2.0, 2.0)
        accel_z = random.uniform(-2.0, 2.0)
        
        # Simulate gyroscope data (±250°/s range)
        gyro_x = random.uniform(-250.0, 250.0)
        gyro_y = random.uniform(-250.0, 250.0)
        gyro_z = random.uniform(-250.0, 250.0)
        
        return {
            "accelerometer": {
                "x": accel_x,
                "y": accel_y,
                "z": accel_z
            },
            "gyroscope": {
                "x": gyro_x,
                "y": gyro_y,
                "z": gyro_z
            }
        }

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