#!/usr/bin/env python3
"""
Servo calibration tool for humanoid robot.
Allows interactive calibration of servo motors and saves calibration data.
"""
import time
import sys
from adafruit_servokit import ServoKit

# Initialize the PCA9685 with 16 channels
kit = ServoKit(channels=16)

# Number of servos on the robot
NUM_SERVOS = 13

def servo_test():
    """
    Test all servos by moving each to a neutral position.
    
    Moves each servo to 90 degrees sequentially to verify functionality.
    """
    print("Testing all servos by setting them to 90 degrees...")
    for i in range(NUM_SERVOS):
        print(f"Setting servo {i} to 90 degrees")
        kit.servo[i].angle = 90
        time.sleep(0.5)
    print("Test complete!")

def calibrate_servo(servo_index):
    """
    Interactively calibrate a specific servo.
    
    Args:
        servo_index (int): Index of the servo to calibrate
        
    Returns:
        int or None: The calibrated angle for the servo, or None if aborted
    """
    print(f"\nCalibrating Servo #{servo_index}")
    print("----------------------------------------")
    print("Controls:")
    print("  +/=  : Increase angle by 5 degrees")
    print("  -    : Decrease angle by 5 degrees")
    print("  q    : Quit calibration for this servo")
    print("  s    : Save current position")
    print("  r    : Reset to 90 degrees")
    print("----------------------------------------")
    
    # Start at 90 degrees
    current_angle = 90
    kit.servo[servo_index].angle = current_angle
    print(f"Current angle: {current_angle}")
    
    while True:
        command = input("Enter command: ").strip().lower()
        
        if command in ['+', '=']:
            current_angle = min(180, current_angle + 5)
            kit.servo[servo_index].angle = current_angle
            print(f"Current angle: {current_angle}")
        elif command == '-':
            current_angle = max(0, current_angle - 5)
            kit.servo[servo_index].angle = current_angle
            print(f"Current angle: {current_angle}")
        elif command == 'r':
            current_angle = 90
            kit.servo[servo_index].angle = current_angle
            print(f"Reset to 90 degrees")
        elif command == 's':
            print(f"Saved position: Servo {servo_index} = {current_angle} degrees")
            return current_angle
        elif command == 'q':
            print("Quitting calibration for this servo")
            return None
        else:
            print("Invalid command")

def save_calibration(calibration_data):
    """
    Save calibration data to a file.
    
    Creates a Python file with calibrated servo positions that can be imported
    by the main robot controller.
    
    Args:
        calibration_data (dict): Dictionary of servo indices and calibrated angles
    """
    with open('servo_calibration.py', 'w') as f:
        f.write("# Servo calibration values\n\n")
        f.write("# Default positions for each servo (calibrated values)\n")
        f.write("DEFAULT_POSITIONS = {\n")
        
        for servo_index, angle in sorted(calibration_data.items()):
            f.write(f"    {servo_index}: {angle},  # Servo {servo_index}\n")
        
        f.write("}\n")
    
    print("\nCalibration data saved to 'servo_calibration.py'")
    print("You can import these values in your main robot controller.")

def main_menu():
    """
    Display the main calibration menu.
    
    Returns:
        str: The user's menu choice
    """
    print("\n=== Robot Servo Calibration Menu ===")
    print("1. Test all servos")
    print("2. Calibrate a specific servo")
    print("3. Calibrate all servos")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ").strip()
    return choice

def main():
    """
    Main calibration program.
    
    Handles menu navigation and calibration workflow.
    """
    calibration_data = {}
    
    print("===================================")
    print("Humanoid Robot Servo Calibration Tool")
    print("===================================")
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            servo_test()
        elif choice == '2':
            try:
                servo_index = int(input("Enter servo number (0-12): ").strip())
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
                print(f"\nServo {i}:")
                angle = calibrate_servo(i)
                if angle is not None:
                    calibration_data[i] = angle
        elif choice == '4':
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
            kit.servo[i].angle = None 