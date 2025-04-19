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

from ..base_controller import BaseRobotController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS, I2C_CONFIG
from robot.controllers.base_controller import BaseController

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
        Set a servo to a specific angle with smooth movement.
        
        Args:
            servo_index (int): Index of the servo to move
            angle (int): Target angle (0-180)
            speed (float): Movement speed in seconds per degree
        """
        if servo_index not in range(13):
            raise ValueError("Invalid servo index")
            
        # Get current position
        current = self.get_servo(servo_index)
        
        # Calculate steps for smooth movement
        steps = abs(angle - current)
        if steps == 0:
            return
            
        # Move servo smoothly
        step_size = 1 if angle > current else -1
        for i in range(steps):
            self._set_pwm(servo_index, current + (i + 1) * step_size)
            time.sleep(speed)
            
    def dance(self):
        """
        Perform a dance sequence.
        """
        # Dance sequence implementation
        pass
        
    def stand_up(self):
        """
        Move the robot to a standing position.
        """
        # Stand up sequence implementation
        pass

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