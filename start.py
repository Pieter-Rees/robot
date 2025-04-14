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
import socket
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('robot')

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def is_raspberry_pi() -> bool:
    """
    Check if the code is running on a Raspberry Pi.
    
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise
    """
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return 'raspberry pi' in f.read().lower()
    except FileNotFoundError:
        return platform.machine().startswith('arm') or platform.machine().startswith('aarch')
    except Exception as e:
        logger.warning(f"Error checking for Raspberry Pi: {e}")
        return False

def clear_screen() -> None:
    """
    Clear the terminal screen.
    OS-independent implementation.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def check_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if required Python dependencies are installed.
    
    Returns:
        Tuple[bool, List[str]]: (True if all dependencies are present, list of missing dependencies)
    """
    missing_deps = []
    all_present = True
    
    dependencies = [
        ('flask', None),
        ('Adafruit_PCA9685', None)
    ]
    
    if is_raspberry_pi():
        dependencies.append(('RPi.GPIO', None))
    
    for module_name, _ in dependencies:
        try:
            __import__(module_name)
        except ImportError:
            missing_deps.append(module_name)
            all_present = False
    
    try:
        from robot.controllers.robot_controller import RobotController
        from robot.controllers.mock_robot_controller import MockRobotController
        from robot.sensors import OT703C86, MPU6050
    except ImportError as e:
        missing_deps.append(str(e))
        all_present = False
    
    return all_present, missing_deps

def install_dependencies() -> bool:
    """
    Install dependencies from requirements.txt file.
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    logger.info("Installing dependencies...")
    try:
        # Using subprocess with check=True to raise an exception on failure
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                       check=True, capture_output=True, text=True)
        logger.info("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e.stderr}")
        print("Failed to install dependencies. Please install them manually.")
        return False

def display_header() -> None:
    """
    Display the application header with title and information.
    """
    clear_screen()
    print("=" * 60)
    print("       HUMANOID ROBOT CONTROL SYSTEM")
    print("=" * 60)
    print("A control system for Raspberry Pi Zero W with PCA9685 servo controller")
    print("-" * 60)

def get_ip_address() -> Optional[str]:
    """
    Get the device's IP address.
    
    Returns:
        Optional[str]: IP address as string, or None if not found
    """
    try:
        # This gets a non-loopback IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"Error getting IP address: {e}")
        # Fall back to hostname if socket method fails
        try:
            result = subprocess.run(["hostname", "-I"], 
                                   capture_output=True, text=True, check=True)
            ip = result.stdout.strip().split()[0]  # Get first IP if multiple
            return ip if ip else None
        except Exception as e2:
            logger.warning(f"Error getting IP address from hostname: {e2}")
            return None

def display_ip() -> None:
    """
    Display the device's IP address for web interface access.
    """
    ip = get_ip_address()
    if ip:
        print(f"Your device's IP address: {ip}")
        print(f"Access the web interface at: http://{ip}:5000")
    else:
        print("Could not determine IP address.")
    print("-" * 60)

def run_with_error_handling(func: Callable, *args, **kwargs) -> None:
    """
    Run a function with proper error handling and logging.
    
    Args:
        func: Function to run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    """
    try:
        func(*args, **kwargs)
    except KeyboardInterrupt:
        print("\nOperation stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        print(f"An error occurred: {e}")
    finally:
        input("Press Enter to continue...")

def start_web_interface() -> None:
    """
    Start the web interface for robot control.
    """
    print("Starting web interface on port 5000...")
    print("Press Ctrl+C to stop and return to menu")
    
    try:
        from robot.web.web_server import app
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except ImportError as e:
        logger.error(f"Error importing web server: {e}")
        print(f"Could not start web interface: {e}")
    except KeyboardInterrupt:
        print("\nWeb interface stopped")

def start_command_line_controller() -> None:
    """
    Start the command line controller for direct robot control.
    """
    print("Starting command line controller...")
    print("Press Ctrl+C to stop and return to menu")
    
    controller = None
    try:
        if is_raspberry_pi():
            from robot.controllers.robot_controller import RobotController
            controller_class = RobotController
            print("Using real robot controller (Raspberry Pi detected)")
        else:
            from robot.controllers.mock_robot_controller import MockRobotController
            controller_class = MockRobotController
            print("Using mock robot controller (non-Raspberry Pi environment)")
        
        controller = controller_class()
        controller.initialize_robot()
        
        # Simple command menu
        while True:
            print("\nCommands: [d]ance, [s]tand, [w]alk, [q]uit")
            cmd = input("Enter command: ").strip().lower()
            
            if cmd == 'd':
                controller.dance()
            elif cmd == 's':
                controller.stand_up()
            elif cmd == 'w':
                steps = input("Number of steps (default: 3): ").strip()
                steps = int(steps) if steps.isdigit() else 3
                for _ in range(steps):
                    controller.step_forward()
            elif cmd == 'q':
                break
            else:
                print("Unknown command")
                
    except ImportError as e:
        logger.error(f"Error importing controller: {e}")
        print(f"Could not start controller: {e}")
    except KeyboardInterrupt:
        print("\nController stopped")
    finally:
        if controller:
            controller.shutdown()

def run_calibration_tool() -> None:
    """
    Run the servo calibration tool.
    """
    print("Starting calibration tool...")
    print("Follow the on-screen instructions to calibrate your servos")
    
    if not is_raspberry_pi():
        print("Calibration tool is only available on Raspberry Pi")
        print("Please run this on your actual robot hardware")
        return
        
    try:
        from robot.calibration import run_calibration
        run_calibration()
    except ImportError as e:
        logger.error(f"Error importing calibration tool: {e}")
        print(f"Could not start calibration tool: {e}")
    except KeyboardInterrupt:
        print("\nCalibration tool stopped")

def check_and_install_dependencies() -> None:
    """
    Check for dependencies and offer to install missing ones.
    """
    print("Checking dependencies...")
    all_present, missing = check_dependencies()
    
    if all_present:
        print("All dependencies are installed!")
    else:
        print("Missing dependencies:")
        for dep in missing:
            print(f" - {dep}")
            
        install = input("Would you like to install missing dependencies? (y/n): ").strip().lower()
        if install == 'y':
            success = install_dependencies()
            if success:
                print("Dependencies installed successfully!")
            else:
                print("Some dependencies could not be installed.")
                print("Please install them manually using pip.")

def main_menu() -> None:
    """
    Display the main menu and handle user input for program selection.
    Provides options to start different components of the system.
    """
    menu_options = {
        '1': ('Start Web Interface', lambda: run_with_error_handling(start_web_interface)),
        '2': ('Start Command Line Controller', lambda: run_with_error_handling(start_command_line_controller)),
        '3': ('Run Calibration Tool', lambda: run_with_error_handling(run_calibration_tool)),
        '4': ('Check and Install Dependencies', lambda: run_with_error_handling(check_and_install_dependencies)),
        '5': ('Exit', None)
    }
    
    while True:
        display_header()
        display_ip()
        
        print("\nSelect an option:")
        for key, (label, _) in menu_options.items():
            print(f"{key}. {label}")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice in menu_options:
            if choice == '5':
                # Exit
                clear_screen()
                print("Thank you for using the Humanoid Robot Control System!")
                print("Exiting...")
                break
                
            # Run the selected function
            action = menu_options[choice][1]
            if action:
                action()
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
        print("Please check the logs for more information.")
        sys.exit(1) 