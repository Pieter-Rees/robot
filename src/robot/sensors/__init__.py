#!/usr/bin/env python3
"""
Sensor module for the humanoid robot.
"""
import time
import platform
import sys
from ..config import I2C_CONFIG

# Handle platform-specific imports
try:
    import smbus2
except ImportError:
    if platform.system() == 'Windows':
        print("Warning: Running on Windows - using mock I2C implementation")
        # Mock SMBus implementation for Windows
        class MockSMBus:
            def __init__(self, bus=None):
                self.bus = bus
                print(f"Initialized Mock SMBus on bus {bus}")
                
            def write_byte_data(self, addr, reg, data):
                print(f"Mock write: addr={hex(addr)}, reg={hex(reg)}, data={hex(data)}")
                return None
                
            def read_byte_data(self, addr, reg):
                print(f"Mock read: addr={hex(addr)}, reg={hex(reg)}")
                return 0
                
            def read_i2c_block_data(self, addr, reg, length):
                print(f"Mock block read: addr={hex(addr)}, reg={hex(reg)}, length={length}")
                return [0] * length
                
            def close(self):
                print("Mock SMBus closed")
                
        smbus2 = type('smbus2', (), {'SMBus': MockSMBus})
    else:
        print("Error: smbus2 module not found. Install with: pip install smbus2")
        sys.exit(1)

def get_default_bus():
    """
    Get the default I2C bus number based on platform.
    
    Returns:
        int: I2C bus number (1 for Raspberry Pi, 0 for mock when not on RPi)
    """
    system = platform.system()
    if system == 'Linux':
        return 1  # Default I2C bus on Raspberry Pi
    else:
        return 0  # Mock bus for non-Raspberry Pi platforms 