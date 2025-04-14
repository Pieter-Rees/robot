#!/usr/bin/env python3
"""
Servo calibration tool for humanoid robot.
Allows interactive calibration of servo motors and saves calibration data.
"""
import os
import time
import json
import threading
import logging
from typing import Dict, Optional, Union, List, Tuple
import numpy as np
from Adafruit_PCA9685 import PCA9685

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('calibration')

# Initialize the PCA9685 with default address (0x40)
try:
    pwm = PCA9685()
    pwm.set_pwm_freq(50)  # Set PWM frequency to 50Hz (standard for servos)
    HARDWARE_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not initialize PCA9685: {e}")
    logger.warning("Running in simulation mode")
    HARDWARE_AVAILABLE = False

# Number of servos on the robot
NUM_SERVOS = 13

# Servo names for better user experience
SERVO_NAMES = {
    0: "HEAD",
    1: "SHOULDER_RIGHT",
    2: "SHOULDER_LEFT",
    3: "ELBOW_RIGHT",
    4: "ELBOW_LEFT",
    5: "HIP_RIGHT",
    6: "HIP_LEFT",
    7: "KNEE_RIGHT",
    8: "KNEE_LEFT",
    9: "ANKLE_RIGHT",
    10: "ANKLE_LEFT",
    11: "WRIST_RIGHT",
    12: "WRIST_LEFT"
}

# Movement limits for safety
SERVO_LIMITS = {
    0: (45, 135),  # HEAD
    1: (30, 150),  # SHOULDER_RIGHT
    2: (30, 150),  # SHOULDER_LEFT
    3: (30, 150),  # ELBOW_RIGHT
    4: (30, 150),  # ELBOW_LEFT
    5: (30, 150),  # HIP_RIGHT
    6: (30, 150),  # HIP_LEFT
    7: (30, 150),  # KNEE_RIGHT
    8: (30, 150),  # KNEE_LEFT
    9: (30, 150),  # ANKLE_RIGHT
    10: (30, 150), # ANKLE_LEFT
    11: (30, 150), # WRIST_RIGHT
    12: (30, 150)  # WRIST_LEFT
}

# Cache of current servo positions
current_positions = {}

def set_servo(servo_index: int, angle: Optional[float], speed: float = 0) -> bool:
    """
    Set servo position using PCA9685 with optional speed control.
    
    Args:
        servo_index (int): The servo channel number (0-15)
        angle (float): The angle to set (0-180) or None to release the servo
        speed (float): Speed of movement (0 for instant, higher for slower)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not HARDWARE_AVAILABLE:
        logger.info(f"Simulation: Setting servo {servo_index} to {angle} degrees")
        if angle is not None:
            current_positions[servo_index] = angle
        return True
    
    try:
        if angle is None:
            # Release the servo (no signal)
            pwm.set_pwm(servo_index, 0, 0)
            if servo_index in current_positions:
                del current_positions[servo_index]
            return True

        # Apply safety limits
        min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
        safe_angle = max(min_angle, min(max_angle, angle))
        
        # Get current position
        current_angle = current_positions.get(servo_index, 90)
        
        # Skip if already at target position (within tolerance)
        if abs(current_angle - safe_angle) < 0.5:
            return True
            
        # Convert angle to pulse width (improved calculation)
        min_pulse = 150  # ~1ms pulse at 50Hz
        max_pulse = 600  # ~2ms pulse at 50Hz
        pulse_range = max_pulse - min_pulse
        
        # If speed is specified, move gradually
        if speed > 0 and abs(current_angle - safe_angle) > 5:
            # Create a smooth movement trajectory
            steps = max(int(abs(current_angle - safe_angle) / 2), 5)
            angles = np.linspace(current_angle, safe_angle, steps)
            
            for a in angles:
                pulse = int(min_pulse + (a / 180.0) * pulse_range)
                pwm.set_pwm(servo_index, 0, pulse)
                time.sleep(speed)
        else:
            # Move immediately
            pulse = int(min_pulse + (safe_angle / 180.0) * pulse_range)
            pwm.set_pwm(servo_index, 0, pulse)
        
        # Update cache
        current_positions[servo_index] = safe_angle
        return True
        
    except Exception as e:
        logger.error(f"Error setting servo {servo_index}: {e}")
        return False

def load_existing_calibration() -> Dict[int, float]:
    """
    Load existing calibration data if available.
    
    Returns:
        Dict[int, float]: Dictionary mapping servo indices to calibrated angles
    """
    calibration_data = {}
    
    # Try to load from Python file first
    try:
        # Try to import the calibration file if it exists
        import servo_calibration
        calibration_data = getattr(servo_calibration, 'DEFAULT_POSITIONS', {})
        logger.info(f"Loaded calibration data from servo_calibration.py")
    except ImportError:
        pass
        
    # If Python import failed, try JSON
    if not calibration_data:
        try:
            if os.path.exists('servo_calibration.json'):
                with open('servo_calibration.json', 'r') as f:
                    calibration_data = json.load(f)
                logger.info(f"Loaded calibration data from servo_calibration.json")
        except Exception as e:
            logger.warning(f"Could not load calibration data: {e}")
    
    return calibration_data

def servo_test() -> None:
    """
    Test all servos by moving each to a neutral position.
    
    Moves each servo to 90 degrees sequentially to verify functionality.
    """
    print("Testing all servos...")
    
    # First center all servos
    for servo in range(NUM_SERVOS):
        set_servo(servo, 90)
    time.sleep(1)
    
    # Then test each one individually with movement
    for servo in range(NUM_SERVOS):
        servo_name = SERVO_NAMES.get(servo, f"Servo {servo}")
        print(f"Testing {servo_name} (#{servo})")
        
        # Move to minimum angle
        min_angle, _ = SERVO_LIMITS.get(servo, (45, 135))
        set_servo(servo, min_angle, 0.01)
        time.sleep(0.5)
        
        # Move to maximum angle
        _, max_angle = SERVO_LIMITS.get(servo, (45, 135))
        set_servo(servo, max_angle, 0.01)
        time.sleep(0.5)
        
        # Return to center
        set_servo(servo, 90, 0.01)
        time.sleep(0.5)
    
    print("Servo test complete!")

def calibrate_servo(servo_index: int) -> Optional[float]:
    """
    Interactively calibrate a specific servo.
    
    Args:
        servo_index (int): Index of the servo to calibrate
        
    Returns:
        Optional[float]: The calibrated angle for the servo, or None if aborted
    """
    servo_name = SERVO_NAMES.get(servo_index, f"Servo {servo_index}")
    print(f"\nCalibrating {servo_name} (#{servo_index})")
    print("----------------------------------------")
    print("Controls:")
    print("  +/=  : Increase angle by 5 degrees")
    print("  -    : Decrease angle by 5 degrees")
    print("  1-9  : Adjust by 1-9 degrees")
    print("  f1-f9: Fine adjust by 0.1-0.9 degrees")
    print("  q    : Quit calibration for this servo")
    print("  s    : Save current position")
    print("  r    : Reset to 90 degrees")
    print("  l    : Show servo limits")
    print("----------------------------------------")
    
    # Start at current position or 90 degrees
    current_angle = current_positions.get(servo_index, 90)
    success = set_servo(servo_index, current_angle)
    if not success:
        print(f"Warning: Could not set initial position for {servo_name}")
    
    min_angle, max_angle = SERVO_LIMITS.get(servo_index, (0, 180))
    print(f"Current angle: {current_angle:.1f}")
    print(f"Limits: {min_angle} to {max_angle} degrees")
    
    while True:
        command = input("Enter command: ").strip().lower()
        
        if command in ['+', '=']:
            current_angle = min(max_angle, current_angle + 5)
            set_servo(servo_index, current_angle)
            print(f"Current angle: {current_angle:.1f}")
        elif command == '-':
            current_angle = max(min_angle, current_angle - 5)
            set_servo(servo_index, current_angle)
            print(f"Current angle: {current_angle:.1f}")
        elif command.isdigit() and 1 <= int(command) <= 9:
            adjustment = int(command)
            current_angle = min(max_angle, current_angle + adjustment)
            set_servo(servo_index, current_angle)
            print(f"Current angle: {current_angle:.1f}")
        elif command.startswith('f') and len(command) == 2 and command[1].isdigit() and 1 <= int(command[1]) <= 9:
            fine_adjustment = int(command[1]) / 10.0
            current_angle = min(max_angle, current_angle + fine_adjustment)
            set_servo(servo_index, current_angle)
            print(f"Current angle: {current_angle:.1f}")
        elif command == 'r':
            current_angle = 90
            set_servo(servo_index, current_angle)
            print(f"Reset to 90 degrees")
        elif command == 'l':
            print(f"Servo limits: {min_angle} to {max_angle} degrees")
        elif command == 's':
            print(f"Saved position: {servo_name} = {current_angle:.1f} degrees")
            return current_angle
        elif command == 'q':
            print(f"Quitting calibration for {servo_name}")
            return None
        else:
            print("Invalid command")

def save_calibration(calibration_data: Dict[int, float]) -> None:
    """
    Save calibration data to files.
    
    Creates both a Python file and a JSON file with calibrated servo positions.
    
    Args:
        calibration_data (Dict[int, float]): Dictionary of servo indices and calibrated angles
    """
    # Save as Python file
    with open('servo_calibration.py', 'w') as f:
        f.write("# Servo calibration values\n\n")
        f.write("# Default positions for each servo (calibrated values)\n")
        f.write("DEFAULT_POSITIONS = {\n")
        
        for servo_index, angle in sorted(calibration_data.items()):
            servo_name = SERVO_NAMES.get(servo_index, f"Servo {servo_index}")
            f.write(f"    {servo_index}: {angle:.1f},  # {servo_name}\n")
        
        f.write("}\n\n")
        f.write("# Servo limits for safety\n")
        f.write("SERVO_LIMITS = {\n")
        
        for servo_index, limits in sorted(SERVO_LIMITS.items()):
            servo_name = SERVO_NAMES.get(servo_index, f"Servo {servo_index}")
            f.write(f"    {servo_index}: {limits},  # {servo_name}\n")
        
        f.write("}\n")
    
    # Also save as JSON for easier programmatic access
    with open('servo_calibration.json', 'w') as f:
        json.dump({
            'positions': calibration_data,
            'limits': SERVO_LIMITS
        }, f, indent=2)
    
    print("\nCalibration data saved to 'servo_calibration.py' and 'servo_calibration.json'")

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu() -> str:
    """
    Display the main calibration menu.
    
    Returns:
        str: The user's menu choice
    """
    print("\n=== Robot Servo Calibration Menu ===")
    print("1. Test all servos")
    print("2. Calibrate a specific servo")
    print("3. Calibrate all servos")
    print("4. Save current calibration")
    print("5. Load saved calibration")
    print("6. Reset all servos to default")
    print("7. Exit")
    
    choice = input("Enter your choice (1-7): ").strip()
    return choice

def run_calibration() -> None:
    """
    Main calibration function that can be imported and called from other modules.
    """
    main()

def main() -> None:
    """
    Main calibration program.
    
    Handles menu navigation and calibration workflow.
    """
    calibration_data = load_existing_calibration()
    
    if not HARDWARE_AVAILABLE:
        print("WARNING: Hardware not detected. Running in simulation mode.")
        print("Some functions may not work as expected.")
    
    clear_screen()
    print("===================================")
    print("Humanoid Robot Servo Calibration Tool")
    print("===================================")
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            servo_test()
        elif choice == '2':
            try:
                servo_display = '\n'.join([f"{i}: {SERVO_NAMES.get(i, f'Servo {i}')}" for i in range(NUM_SERVOS)])
                print(f"\nAvailable servos:\n{servo_display}")
                servo_index = int(input("\nEnter servo number (0-12): ").strip())
                if 0 <= servo_index < NUM_SERVOS:
                    angle = calibrate_servo(servo_index)
                    if angle is not None:
                        calibration_data[servo_index] = angle
                else:
                    print(f"Error: Servo index must be between 0 and {NUM_SERVOS-1}")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == '3':
            print("\nCalibrating all servos sequentially...")
            for i in range(NUM_SERVOS):
                servo_name = SERVO_NAMES.get(i, f"Servo {i}")
                print(f"\n{servo_name} (#{i}):")
                angle = calibrate_servo(i)
                if angle is not None:
                    calibration_data[i] = angle
        elif choice == '4':
            if calibration_data:
                save_calibration(calibration_data)
            else:
                print("No calibration data to save.")
        elif choice == '5':
            calibration_data = load_existing_calibration()
            if calibration_data:
                print("Loaded calibration data:")
                for servo_index, angle in sorted(calibration_data.items()):
                    servo_name = SERVO_NAMES.get(servo_index, f"Servo {servo_index}")
                    print(f"  {servo_name} (#{servo_index}): {angle:.1f} degrees")
            else:
                print("No calibration data found.")
        elif choice == '6':
            print("Resetting all servos to default position (90 degrees)...")
            for i in range(NUM_SERVOS):
                set_servo(i, 90, 0.01)
            time.sleep(1)
            print("Reset complete.")
        elif choice == '7':
            if calibration_data:
                save = input("Do you want to save the calibration data before exiting? (y/n): ").strip().lower()
                if save == 'y':
                    save_calibration(calibration_data)
            print("Exiting calibration tool")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCalibration program interrupted by user")
    finally:
        # Release all servos
        for i in range(NUM_SERVOS):
            set_servo(i, None) 