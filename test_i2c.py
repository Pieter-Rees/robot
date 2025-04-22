#!/usr/bin/env python3
"""
Simple test script to check PCA9685 connectivity
"""
import time
import sys
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_pca9685():
    """Test if we can communicate with the PCA9685 device"""
    try:
        print("Importing Adafruit_PCA9685...")
        from Adafruit_PCA9685 import PCA9685
        print("✓ Successfully imported Adafruit_PCA9685")
    except ImportError as e:
        print(f"✗ Error importing Adafruit_PCA9685: {e}")
        print("  Try: pip install adafruit-pca9685")
        return False
    
    try:
        print("\nTrying to initialize PCA9685 at address 0x40...")
        pwm = PCA9685(address=0x40, busnum=1)
        print("✓ Successfully initialized PCA9685 device")
    except Exception as e:
        print(f"✗ Error initializing PCA9685: {e}")
        print("  Check your I2C connections and address")
        return False
    
    try:
        print("\nSetting PWM frequency to 50Hz...")
        pwm.set_pwm_freq(50)
        print("✓ Successfully set PWM frequency")
    except Exception as e:
        print(f"✗ Error setting PWM frequency: {e}")
        return False
    
    try:
        print("\nTesting servo control (channel 0, head servo)...")
        # Center position (90 degrees)
        print("  Moving to center position...")
        pwm.set_pwm(0, 0, 307)  # ~90 degrees (205 + (90/180) * 205)
        time.sleep(1)
        
        # 45 degrees
        print("  Moving to 45 degrees...")
        pwm.set_pwm(0, 0, 256)  # ~45 degrees (205 + (45/180) * 205)
        time.sleep(1)
        
        # Back to center
        print("  Moving back to center position...")
        pwm.set_pwm(0, 0, 307)
        time.sleep(1)
        
        print("✓ Successfully tested servo control")
    except Exception as e:
        print(f"✗ Error controlling servo: {e}")
        return False
    
    print("\n=== PCA9685 Test Successful ===")
    return True

if __name__ == "__main__":
    test_pca9685() 