#!/usr/bin/env python3
"""
Startup script for the humanoid robot control system.
Provides a menu-driven interface to access the various components of the system.
"""
import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Also add the parent directory to support 'robot' imports
parent_path = str(Path(__file__).parent)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

def is_raspberry_pi():
    """
    Check if the code is running on a Raspberry Pi.
    
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise
    """
    try:
        # Import relative to src directory that was added to sys.path
        from robot.controllers.controller_factory import is_raspberry_pi as pi_check
        return pi_check()
    except ImportError:
        # Fallback if import fails
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'raspberry pi' in f.read().lower()
        except:
            return False

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
    missing_deps = []
    
    # Check for Flask
    try:
        import flask
    except ImportError:
        missing_deps.append("flask")
    
    # Check for basic robot packages
    try:
        from robot.base_controller import BaseRobotController
    except ImportError:
        missing_deps.append("robot.base_controller")
    
    # Check for the controllers
    try:
        from robot.controllers.robot_controller import RobotController
    except ImportError:
        missing_deps.append("robot.controllers.robot_controller")
    
    try:
        from robot.controllers.mock_robot_controller import MockRobotController
    except ImportError:
        missing_deps.append("robot.controllers.mock_robot_controller")
    
    # Check for platform-specific dependencies
    if is_raspberry_pi():
        try:
            import RPi.GPIO as GPIO
        except ImportError:
            missing_deps.append("RPi.GPIO")
    
    # Report results
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        return False
    else:
        return True

def install_dependencies():
    """
    Install dependencies from requirements.txt file.
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
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
        print("1. Start Web Interface (WiFi & Bluetooth)")
        print("2. Start Command Line Controller")
        print("3. Run Calibration Tool")
        print("4. Check and Install Dependencies")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Start web interface with Bluetooth support
            clear_screen()
            print("Starting web interface on port 5000...")
            print("Press Ctrl+C to stop and return to menu")
            try:
                from robot.web.web_server import app
                from robot.bluetooth_server import BluetoothWebServer
                
                with BluetoothWebServer(app):
                    print("Web interface and Bluetooth server started")
                    print("Connect to the robot via Bluetooth to get the web interface URL")
                    while True:
                        time.sleep(1)
            except KeyboardInterrupt:
                print("\nWeb interface stopped")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"Error starting web interface: {e}")
                input("Press Enter to continue...")
                
        elif choice == '2':
            # Start command line controller
            clear_screen()
            print("Starting command line controller...")
            print("Press Ctrl+C to stop and return to menu")
            try:
                # Import this way to avoid potential circular imports
                sys.path.insert(0, src_path)  # Ensure src path is first in sys.path
                from robot.controllers import create_controller
                controller = create_controller()
                controller.initialize_robot()
                while True:
                    time.sleep(1)
            except ImportError as e:
                print(f"Import error: {e}")
                print("Try running 'pip install -e .' from the project root directory")
                input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\nController stopped")
                if 'controller' in locals():
                    controller.shutdown()
                input("Press Enter to continue...")
                
        elif choice == '3':
            # Run calibration tool
            clear_screen()
            print("Starting calibration tool...")
            print("Follow the on-screen instructions to calibrate your servos")
            try:
                if is_raspberry_pi():
                    from robot.calibration import run_calibration
                    run_calibration()
                else:
                    print("Calibration tool is only available on Raspberry Pi")
                    print("Please run this on your actual robot hardware")
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