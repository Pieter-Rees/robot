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

from robot.base_controller import BaseRobotController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS, I2C_CONFIG

class RobotController(BaseRobotController):
    """
    Concrete implementation of a robot controller.
    This class handles the actual robot hardware control.
    """
    
    def __init__(self, config=None):
        """Initialize the robot controller."""
        super().__init__()
        self.initialized = False
        self.current_positions = DEFAULT_POSITIONS.copy()  # Initialize with default positions
        self._pwm_cache = {}  # Cache for PWM values
        
        # Use provided config or fall back to I2C_CONFIG
        self.config = config or I2C_CONFIG
        
        # Initialize the PCA9685 using config
        try:
            self.pwm = PCA9685(address=self.config['pca9685_address'], busnum=self.config['default_bus'])
            self.pwm.set_pwm_freq(50)  # Set PWM frequency to 50Hz (standard for servos)
        except Exception as e:
            if platform.system() == 'Windows':
                self.pwm = MockPCA9685(address=self.config['pca9685_address'], busnum=self.config['default_bus'])
                self.pwm.set_pwm_freq(50)
            else:
                print(f"Warning: Failed to initialize PCA9685: {str(e)}")
                self.pwm = None
    
    def _move_to_default_positions(self, speed=0.01):
        """Move all servos to their default positions."""
        for servo_index, default_angle in DEFAULT_POSITIONS.items():
            self.set_servo(servo_index, default_angle, speed=speed)

    def initialize_robot(self) -> None:
        """Initialize the robot hardware and move all servos to their default positions."""
        if not self.initialized:
            self._move_to_default_positions()
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
        """Shutdown the robot controller and clean up resources."""
        try:
            # Move to neutral position and cleanup
            self._move_to_default_positions()
            self.cleanup()
            
            # Reset all PWM channels
            if hasattr(self, 'pwm') and self.pwm is not None:
                for channel in range(16):
                    self.pwm.set_pwm(channel, 0, 0)
        except Exception:
            pass  # Ensure shutdown completes even if errors occur
    
    def _angle_to_pwm(self, angle):
        """Convert angle to PWM value with caching."""
        if angle not in self._pwm_cache:
            self._pwm_cache[angle] = int(205 + (angle / 180.0) * 205)
        return self._pwm_cache[angle]

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
        
        # Check if PWM controller is available
        if self.pwm is None:
            self.current_positions[servo_index] = safe_angle
            return
        
        # Calculate step direction and range
        step = 1 if current_angle < safe_angle else -1
        start = int(current_angle)
        end = int(safe_angle) + step
        
        # Move to target position
        for a in range(start, end, step):
            pwm_value = self._angle_to_pwm(a)
            self.pwm.set_pwm(servo_index, 0, pwm_value)
            self.current_positions[servo_index] = a
            time.sleep(speed)
    
    def dance(self):
        """
        Execute a dance sequence combining various movements.
        """
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
            time.sleep(0.4)
        
        print("Dance routine completed!")

    def stand_up(self):
        """Make the robot stand up by moving all servos to their default positions."""
        if not self.initialized:
            return False
            
        if self.pwm is None:
            return False
            
        try:
            self._move_to_default_positions()
            return True
        except Exception:
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