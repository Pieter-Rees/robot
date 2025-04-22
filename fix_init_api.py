#!/usr/bin/env python3
"""
Script to fix the API initialization issue
"""
import requests
import time
import sys
import traceback
from pathlib import Path
import os

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def fix_init_api(base_url="http://192.168.1.107:5000", max_retries=3):
    """Fix the API initialization issue with retries"""
    
    print(f"Attempting to fix API initialization at {base_url}")
    print("This script will:")
    print("1. Test direct connection to web server")
    print("2. Try to restart the web server if needed")
    print("3. Test direct access to the PCA9685 board")
    print("4. Retry API initialization")
    
    # Step 1: Test web server connection
    print("\nStep 1: Testing web server connection...")
    server_reachable = False
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/robot_info", timeout=5)
            print(f"✓ Web server is reachable (status {response.status_code})")
            server_reachable = True
            break
        except requests.RequestException as e:
            print(f"✗ Attempt {attempt+1}/{max_retries}: Cannot reach web server: {str(e)}")
            time.sleep(2)
    
    if not server_reachable:
        restart = input("\nWeb server not reachable. Would you like to try restarting it? (y/n): ")
        if restart.lower() == 'y':
            print("Attempting to restart web server...")
            try:
                import subprocess
                # Kill existing process
                subprocess.run("pkill -f 'python.*start.py'", shell=True)
                time.sleep(2)
                # Start new process
                subprocess.Popen(["python3", "start.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
                print("Web server restart initiated. Waiting 10 seconds...")
                time.sleep(10)
            except Exception as e:
                print(f"Error restarting web server: {str(e)}")
    
    # Step 2: Test direct PCA9685 access
    print("\nStep 2: Testing direct PCA9685 access...")
    pca9685_ok = False
    
    try:
        from Adafruit_PCA9685 import PCA9685
        pwm = PCA9685(address=0x40, busnum=1)
        pwm.set_pwm_freq(50)
        # Try a simple servo movement
        pwm.set_pwm(0, 0, 307)  # Center position
        time.sleep(0.5)
        pca9685_ok = True
        print("✓ PCA9685 connection is working")
    except ImportError:
        print("✗ Adafruit_PCA9685 module not installed")
        install = input("   Would you like to install it now? (y/n): ")
        if install.lower() == 'y':
            try:
                import subprocess
                subprocess.run(["pip", "install", "adafruit-pca9685"], check=True)
                print("✓ Adafruit_PCA9685 installed successfully. Retrying...")
                try:
                    from Adafruit_PCA9685 import PCA9685
                    pwm = PCA9685(address=0x40, busnum=1)
                    pwm.set_pwm_freq(50)
                    pca9685_ok = True
                    print("✓ PCA9685 connection is working now")
                except Exception as e:
                    print(f"✗ Still cannot access PCA9685: {str(e)}")
            except Exception as e:
                print(f"✗ Failed to install Adafruit_PCA9685: {str(e)}")
    except Exception as e:
        print(f"✗ Cannot access PCA9685: {str(e)}")
    
    # Step 3: Try API initialization
    print("\nStep 3: Testing API initialization...")
    init_success = False
    
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{base_url}/api/init", timeout=10)
            if response.status_code == 200:
                print(f"✓ SUCCESS: API initialization successful")
                print(f"  Response: {response.json()}")
                init_success = True
                break
            else:
                print(f"✗ Attempt {attempt+1}/{max_retries}: API initialization failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                time.sleep(2)
        except requests.RequestException as e:
            print(f"✗ Attempt {attempt+1}/{max_retries}: API request failed: {str(e)}")
            time.sleep(2)
    
    # Final status report
    print("\n=== Final Status ===")
    print(f"Web server reachable: {'Yes' if server_reachable else 'No'}")
    print(f"PCA9685 access working: {'Yes' if pca9685_ok else 'No'}")
    print(f"API initialization successful: {'Yes' if init_success else 'No'}")
    
    if init_success:
        print("\nThe API initialization issue has been fixed!")
        return 0
    else:
        print("\nThe API initialization issue could not be fixed automatically.")
        print("Try the following steps:")
        print("1. Check your I2C connections")
        print("2. Restart the Raspberry Pi")
        print("3. Make sure the PCA9685 board is receiving power")
        print("4. Run 'python3 test_i2c.py' to test direct communication")
        return 1

if __name__ == "__main__":
    try:
        # Use command line argument for base URL if provided
        if len(sys.argv) > 1:
            sys.exit(fix_init_api(sys.argv[1]))
        else:
            sys.exit(fix_init_api())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 