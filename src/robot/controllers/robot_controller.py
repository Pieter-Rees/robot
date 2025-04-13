#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
import logging
from Adafruit_PCA9685 import PCA9685
from ..base_controller import BaseRobotController
from ..config import Servos, DEFAULT_POSITIONS, SERVO_LIMITS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobotController(BaseRobotController):
    """
    Real robot controller implementation using PCA9685 servo controller.
    """
    def __init__(self):
        super().__init__()
        try:
            logger.info("Initializing PCA9685 servo controller...")
            # Initialize the PCA9685 with default address (0x40)
            self.pwm = PCA9685()
            self.pwm.set_pwm_freq(50)  # Set PWM frequency to 50Hz (standard for servos)
            logger.info("PCA9685 initialized successfully")
            
            # Test PWM output
            self.test_pwm_output()
        except Exception as e:
            logger.error(f"Failed to initialize PCA9685: {str(e)}")
            raise
    
    def test_pwm_output(self):
        """
        Test PWM output on a single servo to verify basic functionality.
        """
        logger.info("Testing PWM output...")
        test_servo = Servos.HEAD  # Using head servo for test
        try:
            # Test minimum position
            logger.info(f"Testing minimum position on servo {test_servo}")
            self.set_servo(test_servo, 0)
            time.sleep(1)
            
            # Test maximum position
            logger.info(f"Testing maximum position on servo {test_servo}")
            self.set_servo(test_servo, 180)
            time.sleep(1)
            
            # Return to center
            logger.info(f"Returning servo {test_servo} to center position")
            self.set_servo(test_servo, 90)
            time.sleep(1)
            
            logger.info("PWM test completed")
        except Exception as e:
            logger.error(f"PWM test failed: {str(e)}")
            raise
    
    def set_servo(self, servo_index, angle, speed=0.01):
        """
        Set a servo to a specific angle with controlled speed.
        
        Args:
            servo_index (int): Index of the servo to control
            angle (float): Target angle in degrees
            speed (float): Time delay between angle increments (lower = faster)
        """
        try:
            # Apply safety limits
            min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
            safe_angle = max(min_angle, min(max_angle, angle))
            
            # Get current position
            current_angle = self.current_positions.get(servo_index, 90)
            
            # Calculate step size based on speed
            step = 1 if current_angle < safe_angle else -1
            
            logger.info(f"Moving servo {servo_index} from {current_angle}° to {safe_angle}°")
            
            # Move servo gradually
            for a in range(int(current_angle), int(safe_angle) + step, step):
                # Convert angle to pulse width
                # For 180-degree servos:
                # 0 degrees = 150 microseconds (minimum pulse width)
                # 180 degrees = 600 microseconds (maximum pulse width)
                # PCA9685 resolution is 4096 for 20ms period (50Hz)
                # So we need to convert microseconds to PCA9685 counts
                min_pulse = 150  # microseconds
                max_pulse = 600  # microseconds
                period = 20000   # microseconds (20ms for 50Hz)
                
                # Convert angle to microseconds
                pulse_us = min_pulse + (max_pulse - min_pulse) * (a / 180.0)
                
                # Convert microseconds to PCA9685 counts
                pulse = int((pulse_us / period) * 4096)
                
                logger.debug(f"Setting servo {servo_index} to angle {a}° (pulse width: {pulse_us}μs, PCA9685 value: {pulse})")
                self.pwm.set_pwm(servo_index, 0, pulse)
                self.current_positions[servo_index] = a
                time.sleep(speed)
            logger.info(f"Servo {servo_index} moved to {safe_angle} degrees")
        except Exception as e:
            logger.error(f"Error moving servo {servo_index}: {str(e)}")
            raise
    
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