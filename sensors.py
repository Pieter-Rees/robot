#!/usr/bin/env python3
"""
Sensor module for the humanoid robot.
Implements various sensors including the OT703-C86 for robot vision.
"""
import time
import smbus2

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
    
    def __init__(self, i2c_bus=1, address=0x3C):
        """
        Initialize the OT703-C86 sensor.
        
        Args:
            i2c_bus (int): I2C bus number (default: 1)
            address (int): I2C address of the sensor (default: 0x3C)
        """
        self.bus = smbus2.SMBus(i2c_bus)
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

    def __init__(self, i2c_bus=1, address=0x68):
        """
        Initialize the MPU-6050 sensor.
        
        Args:
            i2c_bus (int): I2C bus number (default: 1)
            address (int): I2C address of the sensor (default: 0x68)
        """
        self.bus = smbus2.SMBus(i2c_bus)
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