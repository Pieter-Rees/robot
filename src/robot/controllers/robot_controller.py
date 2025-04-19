#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
import platform
import sys

# Handle platform-specific imports
try:
    from Adafruit_PCA9685 import PCA9685
except ImportError:
    if platform.system() == 'Windows':
        print("Warning: Running on Windows - using mock PCA9685 implementation")
        # Mock PCA9685 implementation for Windows
        class MockPCA9685:
            def __init__(self, address=0x40, busnum=None):
                self.address = address
                self.busnum = busnum
                print(f"Initialized Mock PCA9685 on bus {busnum}, address {hex(address)}")
                
            def set_pwm_freq(self, freq):
                print(f"Mock set PWM frequency to {freq}Hz")
                
            def set_pwm(self, channel, on, off):
                print(f"Mock set PWM: channel={channel}, on={on}, off={off}")
                
        PCA9685 = MockPCA9685
    else:
        print("Error: Adafruit_PCA9685 module not found. Install with: pip install adafruit-pca9685")
        sys.exit(1)

from ..sensors import OT703C86, MPU6050
from ..base_controller import BaseController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS, I2C_CONFIG

class RobotController(BaseController):
    """
    Concrete implementation of a robot controller.
    This class handles the actual robot hardware control.
    """
    
    def __init__(self):
        """Initialize the robot controller."""
        self.initialized = False
        self.current_positions = {}  # Initialize current positions dictionary
        
        print("Initializing RobotController...")
        print(f"I2C_CONFIG: {I2C_CONFIG}")
        
        # Initialize the PCA9685 using I2C_CONFIG
        try:
            print(f"Attempting to initialize PCA9685 on bus {I2C_CONFIG['default_bus']}, address {hex(I2C_CONFIG['pca9685_address'])}")
            self.pwm = PCA9685(address=I2C_CONFIG['pca9685_address'], busnum=I2C_CONFIG['default_bus'])
            self.pwm.set_pwm_freq(50)  # Set PWM frequency to 50Hz (standard for servos)
            print("PCA9685 initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize PCA9685: {str(e)}")
            if platform.system() == 'Windows':
                print("Using mock PCA9685 implementation on Windows")
                self.pwm = MockPCA9685(address=I2C_CONFIG['pca9685_address'], busnum=I2C_CONFIG['default_bus'])
                self.pwm.set_pwm_freq(50)
            else:
                print("Hardware control will not be available")
                self.pwm = None
        
        # Initialize the OT703-C86 sensor
        try:
            self.eye_sensor = OT703C86()
            print("Eye sensor initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize eye sensor: {str(e)}")
            self.eye_sensor = None
        
        # Initialize the MPU-6050 sensor
        try:
            self.mpu6050 = MPU6050()
            print("MPU6050 sensor initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize MPU6050 sensor: {str(e)}")
            self.mpu6050 = None
    
    def initialize_robot(self) -> None:
        """
        Initialize the robot hardware and move all servos to their default positions.
        """
        if not self.initialized:
            print("Initializing robot hardware...")
            
            # Move all servos to their default positions
            print("Moving servos to default positions...")
            for servo_index, default_angle in DEFAULT_POSITIONS.items():
                print(f"Moving servo {servo_index} to {default_angle} degrees")
                self.set_servo(servo_index, default_angle)
                time.sleep(0.1)  # Small delay between servo movements
            
            print("Robot initialization complete")
            self.initialized = True
    
    def cleanup(self) -> None:
        """
        Clean up resources and safely shut down the robot.
        """
        if self.initialized:
            # TODO: Add actual cleanup code here
            print("Cleaning up robot resources...")
            self.initialized = False
    
    def shutdown(self) -> None:
        """
        Shutdown the robot controller and clean up resources.
        This method should be called when the program is exiting.
        """
        try:
            print("Shutting down robot controller...")
            
            # Release all servos to neutral position
            for servo_index in range(len(Servos)):
                self.set_servo(servo_index, 90)  # Move to neutral position
            
            # Call the existing cleanup method
            self.cleanup()
            
            # Additional cleanup for hardware
            if hasattr(self, 'pwm') and self.pwm is not None:
                # Reset all PWM channels
                for channel in range(16):  # PCA9685 has 16 channels
                    self.pwm.set_pwm(channel, 0, 0)
            
            print("Robot controller shutdown complete")
        except Exception as e:
            print(f"Error during shutdown: {e}")
    
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
        
        # Check if PWM controller is available
        if self.pwm is None:
            print(f"Mock servo movement: servo {servo_index} to angle {safe_angle}")
            self.current_positions[servo_index] = safe_angle
            return
        
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

    def stand_up(self):
        """
        Make the robot stand up by moving all servos to their default positions.
        """
        print("Standing up robot...")
        
        if not self.initialized:
            print("Error: Robot not initialized. Call initialize_robot() first.")
            return False
            
        if self.pwm is None:
            print("Error: PCA9685 controller not available")
            return False
            
        print(f"Using PCA9685 controller: {self.pwm}")
        print(f"Default positions: {DEFAULT_POSITIONS}")
        
        try:
            # Move all servos to their default positions
            for servo_index, default_angle in DEFAULT_POSITIONS.items():
                print(f"Moving servo {servo_index} to {default_angle} degrees")
                self.set_servo(servo_index, default_angle)
                time.sleep(0.1)  # Small delay between servo movements
            
            print("Robot is standing up")
            return True
            
        except Exception as e:
            print(f"Error during stand_up: {str(e)}")
            return False

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
        controller.cleanup() 