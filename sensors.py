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