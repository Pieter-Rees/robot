#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
from functools import lru_cache
import numpy as np
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
        
        # Calculate servo angle to PWM value conversion factors once
        self.min_pwm = 205  # 0 degrees (1ms pulse at 50Hz)
        self.pwm_range = 205  # Range from 0 to 180 degrees
        
        # Cache for servo positions to avoid redundant movements
        self._servo_cache = {}
        
        # Last sensor reading timestamps
        self._last_eye_reading = 0
        self._last_mpu_reading = 0
        self._sensor_cache_time = 0.1  # 100ms cache validity
    
    def _angle_to_pwm(self, angle):
        """Convert angle in degrees to PWM value."""
        return int(self.min_pwm + (angle / 180.0) * self.pwm_range)
    
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
        
        # Get current position
        current_angle = self.current_positions.get(servo_index, 90)
        
        # Skip if the servo is already at the requested position (with small tolerance)
        if abs(current_angle - safe_angle) < 0.5:
            return
            
        # Use numpy for more efficient angle range generation
        if current_angle < safe_angle:
            angles = np.linspace(current_angle, safe_angle, int(abs(safe_angle - current_angle)) + 1)
            for a in angles:
                pwm_value = self._angle_to_pwm(a)
                self.pwm.set_pwm(servo_index, 0, pwm_value)
                self.current_positions[servo_index] = a
                time.sleep(speed)
        else:
            angles = np.linspace(current_angle, safe_angle, int(abs(current_angle - safe_angle)) + 1)
            for a in angles:
                pwm_value = self._angle_to_pwm(a)
                self.pwm.set_pwm(servo_index, 0, pwm_value)
                self.current_positions[servo_index] = a
                time.sleep(speed)
    
    def set_servos(self, positions_dict, speed=0.01):
        """
        Set multiple servos at once to reduce latency.
        
        Args:
            positions_dict (dict): Dictionary mapping servo indices to target angles
            speed (float): Time delay between angle increments
        """
        # Find min and max movement required
        max_diff = 0
        servo_targets = {}
        
        for servo_index, angle in positions_dict.items():
            min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
            safe_angle = max(min_angle, min(max_angle, angle))
            current_angle = self.current_positions.get(servo_index, 90)
            diff = abs(current_angle - safe_angle)
            max_diff = max(max_diff, diff)
            servo_targets[servo_index] = safe_angle
        
        if max_diff < 0.5:
            return
            
        # Number of steps based on the servo that needs to move the most
        steps = int(max_diff) + 1
        
        # Move all servos incrementally
        for step in range(1, steps + 1):
            for servo_index, target in servo_targets.items():
                current = self.current_positions.get(servo_index, 90)
                if abs(current - target) < 0.5:
                    continue
                    
                # Calculate next position
                fraction = step / steps
                next_angle = current + fraction * (target - current)
                pwm_value = self._angle_to_pwm(next_angle)
                self.pwm.set_pwm(servo_index, 0, pwm_value)
                self.current_positions[servo_index] = next_angle
            
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
        
        # Center all servos using the batch method
        self.set_servos(DEFAULT_POSITIONS)
        
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
        self.set_servos(DEFAULT_POSITIONS)
        
        print("Robot shutdown complete!")
    
    def get_eye_data(self):
        """
        Get data from the eye sensor.
        
        Returns:
            dict: Dictionary containing distance and ambient light readings
        """
        # Check if we should use cached value
        current_time = time.time()
        if current_time - self._last_eye_reading < self._sensor_cache_time:
            return self._eye_data_cache
            
        distance = self.eye_sensor.read_distance()
        light = self.eye_sensor.read_ambient_light()
        
        # Cache the reading
        self._eye_data_cache = {
            "distance": distance,
            "ambient_light": light
        }
        self._last_eye_reading = current_time
        
        return self._eye_data_cache
    
    def get_mpu6050_data(self):
        """
        Get data from the MPU-6050 sensor.
        
        Returns:
            dict: Dictionary containing accelerometer and gyroscope readings
        """
        # Check if we should use cached value
        current_time = time.time()
        if current_time - self._last_mpu_reading < self._sensor_cache_time:
            return self._mpu_data_cache
            
        accel_data = self.mpu6050.read_accelerometer()
        gyro_data = self.mpu6050.read_gyroscope()
        
        # Cache the reading
        self._mpu_data_cache = {
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
        self._last_mpu_reading = current_time
        
        return self._mpu_data_cache
    
    def dance(self):
        """
        Execute a dance sequence combining various movements.
        """
        print("Starting dance routine!")
        
        # Initial pose
        self.set_servos({
            Servos.HEAD: 90,
            Servos.SHOULDER_RIGHT: 60,
            Servos.SHOULDER_LEFT: 120,
            Servos.ELBOW_RIGHT: 120,
            Servos.ELBOW_LEFT: 60
        })
        time.sleep(1)
        
        # First move: Rocking side to side with arms
        for _ in range(3):
            self.set_servos({
                Servos.HIP_RIGHT: 70,
                Servos.HIP_LEFT: 110,
                Servos.SHOULDER_RIGHT: 80,
                Servos.SHOULDER_LEFT: 100
            })
            time.sleep(0.4)
            self.set_servos({
                Servos.HIP_RIGHT: 110,
                Servos.HIP_LEFT: 70,
                Servos.SHOULDER_RIGHT: 40,
                Servos.SHOULDER_LEFT: 140
            })
            time.sleep(0.4)
        
        # Second move: Head bobbing with arm waves
        for _ in range(2):
            self.set_servos({
                Servos.HEAD: 70,
                Servos.ELBOW_RIGHT: 150,
                Servos.ELBOW_LEFT: 30
            })
            time.sleep(0.3)
            self.set_servos({
                Servos.HEAD: 110,
                Servos.ELBOW_RIGHT: 90,
                Servos.ELBOW_LEFT: 90
            })
            time.sleep(0.3)
        
        # Third move: Full body twist
        for _ in range(2):
            self.set_servos({
                Servos.HIP_RIGHT: 60,
                Servos.HIP_LEFT: 120,
                Servos.SHOULDER_RIGHT: 40,
                Servos.SHOULDER_LEFT: 140,
                Servos.HEAD: 60
            })
            time.sleep(0.5)
            self.set_servos({
                Servos.HIP_RIGHT: 120,
                Servos.HIP_LEFT: 60,
                Servos.SHOULDER_RIGHT: 140,
                Servos.SHOULDER_LEFT: 40,
                Servos.HEAD: 120
            })
            time.sleep(0.5)
        
        # Final pose
        self.set_servos({
            Servos.HEAD: 90,
            Servos.SHOULDER_RIGHT: 60,
            Servos.SHOULDER_LEFT: 120,
            Servos.ELBOW_RIGHT: 120,
            Servos.ELBOW_LEFT: 60,
            Servos.HIP_RIGHT: 90,
            Servos.HIP_LEFT: 90
        })
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