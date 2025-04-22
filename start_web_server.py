#!/usr/bin/env python3
"""
Dedicated script to start just the web server with detailed error handling
"""
import sys
import os
import time
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def start_web_server():
    """Start the web server with detailed error handling"""
    try:
        print("Importing required modules...")
        from flask import Flask
        try:
            from Adafruit_PCA9685 import PCA9685
            print("✓ Successfully imported Adafruit_PCA9685")
        except ImportError:
            print("✗ Adafruit_PCA9685 not found. Installing...")
            import subprocess
            subprocess.run(["pip", "install", "adafruit-pca9685"], check=True)
            print("✓ Installed Adafruit_PCA9685. Trying to import again...")
            try:
                from Adafruit_PCA9685 import PCA9685
                print("✓ Successfully imported Adafruit_PCA9685 after installation")
            except ImportError as e:
                print(f"✗ Still cannot import Adafruit_PCA9685: {str(e)}")
                return False
                
        print("\nChecking I2C connectivity...")
        try:
            pwm = PCA9685(address=0x40, busnum=1)
            pwm.set_pwm_freq(50)
            print("✓ Successfully connected to PCA9685")
        except Exception as e:
            print(f"✗ Error connecting to PCA9685: {str(e)}")
            print("  Check I2C connections and make sure the device is powered")
            return False
            
        print("\nStarting web server...")
        try:
            from robot.web.web_server import app
            print("✓ Successfully imported web server")
            print("\nWeb server starting on http://0.0.0.0:5000")
            print("Press Ctrl+C to stop")
            app.run(host='0.0.0.0', port=5000, debug=True)
            return True
        except Exception as e:
            print(f"✗ Error starting web server: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except KeyboardInterrupt:
        print("\nWeb server stopped by user")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = start_web_server()
    sys.exit(0 if success else 1) 