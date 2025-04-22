#!/usr/bin/env python3
"""
Robot initialization test script.
This script attempts to initialize the robot and diagnose any issues.
"""
import time
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def run_test():
    """Run the initialization test and report any issues."""
    print("=== Robot Initialization Test ===")
    
    try:
        print("\n1. Importing robot controller...")
        from robot.controllers import create_controller
        print("✓ Successfully imported controller")
    except Exception as e:
        print(f"✗ Error importing controller: {str(e)}")
        print("  Check your Python path and installation")
        return
        
    try:
        print("\n2. Creating controller instance...")
        controller = create_controller()
        
        if hasattr(controller, 'using_mock_pwm') and controller.using_mock_pwm:
            print("✓ Created controller in MOCK mode")
        else:
            print("✓ Created hardware controller")
            
        if hasattr(controller, 'initialization_error') and controller.initialization_error:
            print(f"⚠ Warning: {controller.initialization_error}")
    except Exception as e:
        print(f"✗ Error creating controller: {str(e)}")
        print("  Check hardware connections and dependencies")
        return
    
    try:
        print("\n3. Initializing robot...")
        controller.initialize_robot()
        print("✓ Robot initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing robot: {str(e)}")
        print("  Check servo configurations and hardware connections")
        return
        
    try:
        print("\n4. Testing servo movement...")
        print("  Moving head servo (ID 0) to 90 degrees...")
        controller.set_servo(0, 90)
        time.sleep(1)
        print("✓ Servo movement successful")
    except Exception as e:
        print(f"✗ Error moving servo: {str(e)}")
        print("  Check servo connections and power supply")
        return
    
    print("\n=== All Tests Passed ===")
    print("Robot is properly initialized and functioning")
    
    try:
        print("\nShutting down robot...")
        controller.shutdown()
        print("✓ Robot shutdown successful")
    except Exception as e:
        print(f"⚠ Warning during shutdown: {str(e)}")
        
if __name__ == "__main__":
    run_test() 