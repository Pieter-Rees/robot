#!/usr/bin/env python3
"""
Mock Robot Controller module for testing without hardware.
Simulates servo motor control for robot movements.
"""
import time
import random
from robot.base_controller import BaseRobotController
from robot.config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

class MockRobotController(BaseRobotController):
    """
    Mock robot controller implementation for testing without hardware.
    """
    def __init__(self):
        super().__init__()
        print("Initializing mock robot controller...")
    
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