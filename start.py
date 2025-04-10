#!/usr/bin/env python3
"""
Startup script for the humanoid robot control system.
Provides a menu-driven interface to access the various components of the system.
"""
import os
import sys
import subprocess
import time

def clear_screen():
    """
    Clear the terminal screen.
    OS-independent implementation.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def check_dependencies():
    """
    Check if required Python dependencies are installed.
    
    Returns:
        bool: True if all dependencies are present, False otherwise
    """
    try:
        import flask
        import adafruit_pca9685
        import adafruit_servokit
        import RPi.GPIO as GPIO
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """
    Install dependencies from requirements.txt file.
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please install them manually.")
        return False

def display_header():
    """
    Display the application header with title and information.
    """
    clear_screen()
    print("=" * 60)
    print("       HUMANOID ROBOT CONTROL SYSTEM")
    print("=" * 60)
    print("A control system for Raspberry Pi Zero W with PCA9685 servo controller")
    print("-" * 60)

def display_ip():
    """
    Display the Raspberry Pi's IP address for web interface access.
    """
    try:
        # Using hostname -I to get IP address
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        ip = result.stdout.strip()
        if ip:
            print(f"Your Raspberry Pi's IP address: {ip}")
            print(f"Access the web interface at: http://{ip}:5000")
        else:
            print("Could not determine IP address.")
    except Exception:
        print("Could not determine IP address.")
    print("-" * 60)

def main_menu():
    """
    Display the main menu and handle user input for program selection.
    Provides options to start different components of the system.
    """
    while True:
        display_header()
        display_ip()
        
        print("\nSelect an option:")
        print("1. Start Web Interface")
        print("2. Start Command Line Controller")
        print("3. Run Calibration Tool")
        print("4. Check and Install Dependencies")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Start web interface
            clear_screen()
            print("Starting web interface on port 5000...")
            print("Press Ctrl+C to stop and return to menu")
            try:
                subprocess.run([sys.executable, "web_server.py"])
            except KeyboardInterrupt:
                print("\nWeb interface stopped")
                input("Press Enter to continue...")
                
        elif choice == '2':
            # Start command line controller
            clear_screen()
            print("Starting command line controller...")
            print("Press Ctrl+C to stop and return to menu")
            try:
                subprocess.run([sys.executable, "robot_controller.py"])
            except KeyboardInterrupt:
                print("\nController stopped")
                input("Press Enter to continue...")
                
        elif choice == '3':
            # Run calibration tool
            clear_screen()
            print("Starting calibration tool...")
            print("Follow the on-screen instructions to calibrate your servos")
            try:
                subprocess.run([sys.executable, "calibration.py"])
            except KeyboardInterrupt:
                print("\nCalibration tool stopped")
            input("Press Enter to continue...")
            
        elif choice == '4':
            # Check dependencies
            clear_screen()
            print("Checking dependencies...")
            if check_dependencies():
                print("All dependencies are installed!")
            else:
                install = input("Would you like to install missing dependencies? (y/n): ").strip().lower()
                if install == 'y':
                    install_dependencies()
            input("Press Enter to continue...")
            
        elif choice == '5':
            # Exit
            clear_screen()
            print("Thank you for using the Humanoid Robot Control System!")
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu() 