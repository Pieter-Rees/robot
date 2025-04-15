#!/usr/bin/env python3
"""
Sensor module for the humanoid robot.
Implements various sensors including the OT703-C86 for robot vision.
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
        # Check if we're on a Raspberry Pi
        try:
            with open('/proc/device-tree/model', 'r') as f:
                if 'raspberry pi' in f.read().lower():
                    return 1  # Raspberry Pi typically uses bus 1
        except:
            pass
        return 1  # Default for Linux
    elif system == 'Windows':
        return 0  # Mock bus for Windows
    else:
        return 0  # Default for other platforms

class OT703C86:
    """
    Class to control the OT703-C86 sensor.
    This sensor is used for robot vision/eyes.
    """
    # Register addresses
    REG_DISTANCE = 0x00
    REG_LIGHT = 0x01
    REG_CONFIG = 0x02
    
    # Configuration bits
    CONFIG_MEASURE = 0x01
    CONFIG_LIGHT = 0x02
    
    def __init__(self, i2c_bus=None, address=None):
        """
        Initialize the OT703-C86 sensor.
        
        Args:
            i2c_bus (int): I2C bus number (default: from I2C_CONFIG)
            address (int): I2C address of the sensor (default: from I2C_CONFIG)
        """
        if i2c_bus is None:
            i2c_bus = I2C_CONFIG['default_bus']
            
        if address is None:
            address = I2C_CONFIG['ot703c86_address']
            
        try:
            self.bus = smbus2.SMBus(i2c_bus)
            self.address = address
            self.initialized = False
        except Exception as e:
            print(f"Warning: Could not initialize I2C bus {i2c_bus} for OT703C86: {e}")
            # Create a mock bus as fallback
            self.bus = MockSMBus() if platform.system() == 'Windows' else None
            self.address = address
            self.initialized = False
        
    def initialize(self):
        """
        Initialize the sensor and verify communication.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Write configuration to enable measurements
            self.bus.write_byte_data(self.address, self.REG_CONFIG, 
                                   self.CONFIG_MEASURE | self.CONFIG_LIGHT)
            time.sleep(0.1)  # Wait for configuration to take effect
            
            # Verify sensor is responding
            config = self.bus.read_byte_data(self.address, self.REG_CONFIG)
            if config & (self.CONFIG_MEASURE | self.CONFIG_LIGHT):
                self.initialized = True
                return True
            return False
        except Exception as e:
            print(f"Error initializing OT703-C86 sensor: {e}")
            return False
            
    def read_distance(self):
        """
        Read the distance measurement from the sensor.
        
        Returns:
            float: Distance in centimeters, or None if reading failed
        """
        if not self.initialized:
            print("Sensor not initialized")
            return None
            
        try:
            # Trigger a new measurement
            self.bus.write_byte_data(self.address, self.REG_CONFIG, 
                                   self.CONFIG_MEASURE)
            time.sleep(0.05)  # Wait for measurement
            
            # Read 2 bytes for distance measurement
            data = self.bus.read_i2c_block_data(self.address, self.REG_DISTANCE, 2)
            distance = (data[0] << 8) | data[1]
            
            # Convert to centimeters (assuming 1 unit = 0.1 cm)
            return distance / 10.0
        except Exception as e:
            print(f"Error reading distance: {e}")
            return None
            
    def read_ambient_light(self):
        """
        Read the ambient light level.
        
        Returns:
            int: Light level (0-255), or None if reading failed
        """
        if not self.initialized:
            print("Sensor not initialized")
            return None
            
        try:
            # Trigger a new light measurement
            self.bus.write_byte_data(self.address, self.REG_CONFIG, 
                                   self.CONFIG_LIGHT)
            time.sleep(0.05)  # Wait for measurement
            
            return self.bus.read_byte_data(self.address, self.REG_LIGHT)
        except Exception as e:
            print(f"Error reading ambient light: {e}")
            return None
            
    def shutdown(self):
        """
        Shutdown the sensor and release resources.
        """
        try:
            # Disable measurements
            self.bus.write_byte_data(self.address, self.REG_CONFIG, 0x00)
            self.bus.close()
            self.initialized = False
        except Exception as e:
            print(f"Error shutting down sensor: {e}")

class MPU6050:
    """
    Class to control the MPU-6050 sensor.
    This sensor provides 6-axis motion tracking (3-axis gyroscope and 3-axis accelerometer).
    """
    # Register addresses
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    INT_ENABLE = 0x38
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47

    def __init__(self, i2c_bus=None, address=None):
        """
        Initialize the MPU-6050 sensor.
        
        Args:
            i2c_bus (int): I2C bus number (default: from I2C_CONFIG)
            address (int): I2C address of the sensor (default: from I2C_CONFIG)
        """
        if i2c_bus is None:
            i2c_bus = I2C_CONFIG['default_bus']
            
        if address is None:
            address = I2C_CONFIG['mpu6050_address']
            
        try:
            self.bus = smbus2.SMBus(i2c_bus)
            self.address = address
            self.initialized = False
        except Exception as e:
            print(f"Warning: Could not initialize I2C bus {i2c_bus} for MPU6050: {e}")
            # Create a mock bus as fallback
            self.bus = MockSMBus() if platform.system() == 'Windows' else None
            self.address = address
            self.initialized = False
        
    def initialize(self):
        """
        Initialize the sensor and verify communication.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Wake up the sensor
            self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
            time.sleep(0.1)
            
            # Set sample rate to 1kHz
            self.bus.write_byte_data(self.address, self.SMPLRT_DIV, 0x07)
            
            # Set DLPF bandwidth to 44Hz
            self.bus.write_byte_data(self.address, self.CONFIG, 0x00)
            
            # Set gyro range to ±250°/s
            self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)
            
            # Set accelerometer range to ±2g
            self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)
            
            # Enable interrupts
            self.bus.write_byte_data(self.address, self.INT_ENABLE, 0x01)
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Error initializing MPU-6050 sensor: {e}")
            return False
            
    def read_raw_data(self, addr):
        """
        Read raw data from the sensor.
        
        Args:
            addr (int): Register address to read from
            
        Returns:
            int: Raw sensor data
        """
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        value = (high << 8) | low
        
        if value > 32768:
            value = value - 65536
        return value
        
    def read_accelerometer(self):
        """
        Read accelerometer data.
        
        Returns:
            tuple: (x, y, z) acceleration in g's, or None if reading failed
        """
        if not self.initialized:
            print("Sensor not initialized")
            return None
            
        try:
            x = self.read_raw_data(self.ACCEL_XOUT_H) / 16384.0
            y = self.read_raw_data(self.ACCEL_YOUT_H) / 16384.0
            z = self.read_raw_data(self.ACCEL_ZOUT_H) / 16384.0
            return (x, y, z)
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
            return None
            
    def read_gyroscope(self):
        """
        Read gyroscope data.
        
        Returns:
            tuple: (x, y, z) angular velocity in degrees per second, or None if reading failed
        """
        if not self.initialized:
            print("Sensor not initialized")
            return None
            
        try:
            x = self.read_raw_data(self.GYRO_XOUT_H) / 131.0
            y = self.read_raw_data(self.GYRO_YOUT_H) / 131.0
            z = self.read_raw_data(self.GYRO_ZOUT_H) / 131.0
            return (x, y, z)
        except Exception as e:
            print(f"Error reading gyroscope: {e}")
            return None
            
    def shutdown(self):
        """
        Shutdown the sensor and release resources.
        """
        try:
            # Put the sensor in sleep mode
            self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x40)
            self.bus.close()
            self.initialized = False
        except Exception as e:
            print(f"Error shutting down sensor: {e}") 