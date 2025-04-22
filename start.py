#!/usr/bin/env python3
"""
Startup script for the humanoid robot control system.

This module provides a menu-driven interface to access the various components
of the humanoid robot control system. It handles dependency management,
system initialization, and provides access to different control interfaces.

The main components accessible through this interface are:
- Web Interface: Browser-based control panel
- Command Line Controller: Terminal-based control interface
- Calibration Tool: Utility for calibrating servo motors
"""
from pathlib import Path
import os
import platform
import subprocess
import sys
import time
from typing import List, Optional, Set
import json

# Add src and parent directories to Python path in one go
PATHS_TO_ADD = [
    str(Path(__file__).parent / "src"),
    str(Path(__file__).parent)
]

for path in PATHS_TO_ADD:
    if path not in sys.path:
        sys.path.insert(0, path)

# Cache for Raspberry Pi detection
_is_raspberry_pi: Optional[bool] = None

# Add this near the top with other global variables
_calibration: Optional[dict] = None

def is_raspberry_pi() -> bool:
    """
    Check if the code is running on a Raspberry Pi.
    Uses caching to avoid repeated checks.

    Returns:
        bool: True if running on a Raspberry Pi, False otherwise
    """
    global _is_raspberry_pi
    if _is_raspberry_pi is not None:
        return _is_raspberry_pi

    try:
        from robot.controllers.controller_factory import is_raspberry_pi as pi_check
        _is_raspberry_pi = pi_check()
    except ImportError:
        try:
            with open('/proc/device-tree/model', 'r') as f:
                _is_raspberry_pi = 'raspberry pi' in f.read().lower()
        except:
            _is_raspberry_pi = False
    return _is_raspberry_pi

def clear_screen() -> None:
    """Clear the terminal screen in an OS-independent way."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Cache for dependency checking
_required_deps: Set[str] = {
    'flask',
    'robot.base_controller',
    'robot.controllers.robot_controller',
    'robot.controllers.mock_robot_controller'
}

def check_dependencies() -> bool:
    """
    Check if required Python dependencies are installed.
    Uses a set for O(1) lookups and caches missing dependencies.

    Returns:
        bool: True if all dependencies are present, False otherwise
    """
    missing_deps: List[str] = []
    
    for dep in _required_deps:
        try:
            if dep == 'flask':
                import flask
            elif dep.startswith('robot'):
                __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    # Check for platform-specific dependencies
    if is_raspberry_pi():
        try:
            import RPi.GPIO as GPIO
        except ImportError:
            missing_deps.append("RPi.GPIO")
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        return False
    return True

def install_dependencies() -> bool:
    """
    Install dependencies from requirements.txt file.

    Attempts to install all project dependencies using pip in editable mode.

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

def display_header() -> None:
    """Display the application header with title and information."""
    clear_screen()
    print("=" * 60)
    print("       HUMANOID ROBOT CONTROL SYSTEM")
    print("=" * 60)
    print("A control system for Raspberry Pi Zero W with PCA9685 servo controller")
    print("-" * 60)

def display_ip() -> None:
    """
    Display the Raspberry Pi's IP address for web interface access.
    
    This function attempts to retrieve and display the device's IP address
    using the hostname command.
    """
    try:
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

def load_calibration() -> None:
    """Load calibration data from servo_calibration.json file."""
    global _calibration
    try:
        with open('servo_calibration.json', 'r') as f:
            _calibration = json.load(f)
            print("Calibration loaded successfully!")
            return _calibration
    except FileNotFoundError:
        print("Warning: servo_calibration.json not found. Using default calibration.")
        return None
    except json.JSONDecodeError:
        print("Warning: Invalid calibration file format. Using default calibration.")
        return None

def main_menu() -> None:
    """
    Display the main menu and handle user input for program selection.
    Uses a dictionary for menu options to improve maintainability and performance.
    """
    # Load calibration at startup
    load_calibration()
    
    menu_options = {
        '1': {
            'title': 'Start Web Interface',
            'action': lambda: start_web_interface()
        },
        '2': {
            'title': 'Start Command Line Controller',
            'action': lambda: start_command_line_controller()
        },
        '3': {
            'title': 'Run Calibration Tool',
            'action': lambda: run_calibration_tool()
        },
        '4': {
            'title': 'Load Calibration from File',
            'action': lambda: load_calibration_from_file()
        },
        '5': {
            'title': 'Check and Install Dependencies',
            'action': lambda: handle_dependencies()
        },
        '6': {
            'title': 'Exit',
            'action': lambda: exit_program()
        }
    }

    while True:
        display_header()
        display_ip()
        
        print("\nSelect an option:")
        for key, option in menu_options.items():
            print(f"{key}. {option['title']}")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice in menu_options:
            menu_options[choice]['action']()
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

def start_web_interface() -> None:
    """Start the web interface server."""
    clear_screen()
    print("Starting web interface on port 5000...")
    print("Press Ctrl+C to stop and return to menu")
    try:
        from robot.web.web_server import app
        # Pass calibration data to the web server
        if _calibration:
            app.config['CALIBRATION'] = _calibration
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nWeb interface stopped")
        input("Press Enter to continue...")

def start_command_line_controller() -> None:
    """Start the command line controller."""
    clear_screen()
    print("Starting command line controller...")
    print("Press Ctrl+C to stop and return to menu")
    try:
        from robot.controllers import create_controller
        controller = create_controller()
        # Pass calibration data to controller if available
        if _calibration:
            controller.current_positions = _calibration.get('calibrated_positions', {})
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

def run_calibration_tool() -> None:
    """Run the calibration tool for servo motors."""
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

def load_calibration_from_file() -> None:
    """Load calibration data from a JSON file."""
    clear_screen()
    print("Loading calibration from file...")
    
    try:
        if not is_raspberry_pi():
            print("This feature is only available on Raspberry Pi")
            print("Please run this on your actual robot hardware")
            input("Press Enter to continue...")
            return
            
        from robot.calibration import load_calibration, save_calibration
        from robot.controllers import create_controller
        
        # Get the JSON file path
        print("\nEnter the path to the calibration JSON file")
        print("(Press Enter to use 'servo_calibration.json' in current directory)")
        file_path = input("File path: ").strip()
        
        if not file_path:
            file_path = 'servo_calibration.json'
        
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found")
            input("Press Enter to continue...")
            return
        
        # Load the calibration data
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'calibrated_positions' not in data:
                    print("Error: Invalid calibration file format")
                    input("Press Enter to continue...")
                    return
                
                # Convert named positions to indices
                from robot.config import Servos
                calibrated_positions = {}
                for servo_name, position in data['calibrated_positions'].items():
                    if hasattr(Servos, servo_name):
                        servo_index = getattr(Servos, servo_name)
                        calibrated_positions[servo_index] = position
                
                # Save to system configuration
                save_calibration(calibrated_positions)
                print(f"\nCalibration loaded successfully from: {file_path}")
                
                # Test the calibration
                if input("\nWould you like to test the loaded calibration? (y/n): ").lower() == 'y':
                    controller = create_controller()
                    controller.initialize_robot()
                    try:
                        for servo_index, position in calibrated_positions.items():
                            print(f"Moving servo {servo_index} to position {position}°")
                            controller.set_servo(servo_index, position)
                            time.sleep(1)
                    finally:
                        controller.cleanup()
                
        except json.JSONDecodeError:
            print("Error: Invalid JSON file")
        except Exception as e:
            print(f"Error loading calibration: {e}")
            
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure all dependencies are installed")
    
    input("Press Enter to continue...")

def handle_dependencies() -> None:
    """Handle dependency checking and installation."""
    clear_screen()
    print("Checking dependencies...")
    if check_dependencies():
        print("All dependencies are installed!")
    else:
        install = input("Would you like to install missing dependencies? (y/n): ").strip().lower()
        if install == 'y':
            install_dependencies()
    input("Press Enter to continue...")

def exit_program() -> None:
    """Exit the program gracefully."""
    clear_screen()
    print("Thank you for using the Humanoid Robot Control System!")
    print("Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    main_menu() 