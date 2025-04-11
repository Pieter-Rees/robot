#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
from Adafruit_PCA9685 import PCA9685
from ..sensors import OT703C86, MPU6050
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
        
        # Initialize the OT703-C86 sensor
        self.eye_sensor = OT703C86()
        
        # Initialize the MPU-6050 sensor
        self.mpu6050 = MPU6050()
    
    def set_servo(self, servo_index, angle, speed=0.01):
        """
        Set a servo to a specific angle with controlled speed.
        
        Args:
            servo_index (int): Index of the servo to control
            angle (float): Target angle in degrees
            speed (float): Time delay between angle increments (lower = faster)
        """
        # Apply safety limits
        min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
        safe_angle = max(min_angle, min(max_angle, angle))
        
        # Convert angle to PWM value (0-4095)
        # Servos typically use 1ms to 2ms pulse width (0-180 degrees)
        # For 50Hz (20ms period), this is 5% to 10% duty cycle
        # 4095 * 0.05 = 205 (0 degrees)
        # 4095 * 0.10 = 410 (180 degrees)
        pwm_value = int(205 + (safe_angle / 180.0) * 205)
        
        # Get current position
        current_angle = self.current_positions.get(servo_index, 90)
        
        # Gradually move to target position
        if current_angle < safe_angle:
            for a in range(int(current_angle), int(safe_angle) + 1):
                pwm_value = int(205 + (a / 180.0) * 205)
                self.pwm.set_pwm(servo_index, 0, pwm_value)
                self.current_positions[servo_index] = a
                time.sleep(speed)
        else:
            for a in range(int(current_angle), int(safe_angle) - 1, -1):
                pwm_value = int(205 + (a / 180.0) * 205)
                self.pwm.set_pwm(servo_index, 0, pwm_value)
                self.current_positions[servo_index] = a
                time.sleep(speed)
    
    def initialize_robot(self):
        """
        Initialize the robot and all its components.
        """
        print("Initializing robot...")
        
        # Initialize the eye sensor
        if not self.eye_sensor.initialize():
            print("Warning: Failed to initialize eye sensor")
            
        # Initialize the MPU-6050 sensor
        if not self.mpu6050.initialize():
            print("Warning: Failed to initialize MPU-6050 sensor")
        
        # Center all servos
        for servo_index, angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, angle)
        
        print("Robot initialization complete!")
    
    def shutdown(self):
        """
        Shutdown the robot and release all resources.
        """
        print("Shutting down robot...")
        
        # Shutdown the eye sensor
        self.eye_sensor.shutdown()
        
        # Shutdown the MPU-6050 sensor
        self.mpu6050.shutdown()
        
        # Center all servos
        for servo_index, angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, angle)
        
        print("Robot shutdown complete!")
    
    def get_eye_data(self):
        """
        Get data from the eye sensor.
        
        Returns:
            dict: Dictionary containing distance and ambient light readings
        """
        distance = self.eye_sensor.read_distance()
        light = self.eye_sensor.read_ambient_light()
        
        return {
            "distance": distance,
            "ambient_light": light
        }
    
    def get_mpu6050_data(self):
        """
        Get data from the MPU-6050 sensor.
        
        Returns:
            dict: Dictionary containing accelerometer and gyroscope readings
        """
        accel_data = self.mpu6050.read_accelerometer()
        gyro_data = self.mpu6050.read_gyroscope()
        
        return {
            "accelerometer": {
                "x": accel_data[0] if accel_data else None,
                "y": accel_data[1] if accel_data else None,
                "z": accel_data[2] if accel_data else None
            },
            "gyroscope": {
                "x": gyro_data[0] if gyro_data else None,
                "y": gyro_data[1] if gyro_data else None,
                "z": gyro_data[2] if gyro_data else None
            }
        }
    
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
        
        # First move: Rocking side to side
        for _ in range(3):
            self.set_servo(Servos.HIP_RIGHT, 70)
            self.set_servo(Servos.HIP_LEFT, 110)
            time.sleep(0.5)
            self.set_servo(Servos.HIP_RIGHT, 110)
            self.set_servo(Servos.HIP_LEFT, 70)
            time.sleep(0.5)
        
        # Return to center
        self.set_servo(Servos.HIP_RIGHT, 90)
        self.set_servo(Servos.HIP_LEFT, 90)
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