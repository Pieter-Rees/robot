#!/usr/bin/env python3
"""
Robot Controller module for humanoid robot.
Provides classes and functions to control servo motors for robot movements.
"""
import time
import platform
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import Dict, Tuple, List, Optional, Set
from dataclasses import dataclass
from contextlib import contextmanager
import os
import numpy as np
from functools import lru_cache

# Handle platform-specific imports
try:
    from Adafruit_PCA9685 import PCA9685
except ImportError:
    if platform.system() == 'Windows':
        print("Warning: Running on Windows - using mock PCA9685 implementation")
        # Mock PCA9685 implementation for Windows
        class MockPCA9685:
            def __init__(self, address=0x40, busnum=None):
                self.address = address
                self.busnum = busnum
                print(f"Initialized Mock PCA9685 on bus {busnum}, address {hex(address)}")
                
            def set_pwm_freq(self, freq):
                print(f"Mock set PWM frequency to {freq}Hz")
                
            def set_pwm(self, channel, on, off):
                print(f"Mock set PWM: channel={channel}, on={on}, off={off}")
                
        PCA9685 = MockPCA9685
    else:
        print("Error: Adafruit_PCA9685 module not found. Install with: pip install adafruit-pca9685")
        sys.exit(1)

from robot.base_controller import BaseRobotController
from ..config import config, Servos

@dataclass
class ServoState:
    """Represents the current state of a servo motor."""
    position: int
    moving: bool = False
    target_position: Optional[int] = None
    last_update: float = 0.0

class RobotControllerError(Exception):
    """Base exception class for robot controller errors."""
    pass

class ServoError(RobotControllerError):
    """Exception raised for servo-related errors."""
    pass

class RobotController(BaseRobotController):
    """
    Concrete implementation of a robot controller.
    This class handles the actual robot hardware control with optimized thread management.
    
    Thread Safety:
    - All servo operations are protected by locks
    - PWM operations are thread-safe
    - State updates are atomic
    
    Error Handling:
    - Validates all servo operations before execution
    - Provides detailed error messages
    - Gracefully handles hardware failures
    """
    
    def __init__(self):
        """Initialize the robot controller with optimized thread management."""
        super().__init__()
        self.initialized = False
        self._servo_states: Dict[int, ServoState] = {}
        self._pwm_cache: Dict[int, int] = {}
        self._pwm_cache_lock = threading.Lock()
        
        # Optimized locks for thread safety
        self._state_lock = threading.RLock()
        self._pwm_lock = threading.Lock()
        
        # Initialize thread pool with optimal worker count
        cpu_count = os.cpu_count() or 4
        self._thread_pool = ThreadPoolExecutor(max_workers=min(cpu_count, 8))
        
        # Initialize servo states with pre-allocation
        self._servo_states = {
            servo_id: ServoState(position=config.get_calibrated_position(servo_id))
            for servo_id in vars(Servos).values()
            if isinstance(servo_id, int)
        }
        
        # Initialize the PCA9685 with error handling
        try:
            i2c_config = config.i2c
            self.pwm = PCA9685(
                address=i2c_config['pca9685_address'],
                busnum=i2c_config['default_bus']
            )
            self.pwm.set_pwm_freq(50)
        except Exception as e:
            if platform.system() == 'Windows':
                self.pwm = MockPCA9685(
                    address=i2c_config['pca9685_address'],
                    busnum=i2c_config['default_bus']
                )
                self.pwm.set_pwm_freq(50)
            else:
                print(f"Warning: Failed to initialize PCA9685: {str(e)}")
                self.pwm = None
    
    @contextmanager
    def _servo_operation(self, servo_id: int):
        """Context manager for safe servo operations."""
        if not self.initialized:
            raise RobotControllerError("Robot not initialized")
        
        if servo_id not in self._servo_states:
            raise ServoError(f"Invalid servo ID: {servo_id}")
        
        with self._state_lock:
            yield
    
    @lru_cache(maxsize=128)
    def _angle_to_pwm(self, angle: int) -> int:
        """Convert angle to PWM value with caching."""
        if not 0 <= angle <= 180:
            raise ValueError(f"Angle {angle} outside valid range [0, 180]")
        return int(205 + (angle / 180.0) * 205)
    
    def _validate_servo_params(self, servo_id: int, angle: float) -> int:
        """
        Validate servo parameters and return safe angle value.
        
        Args:
            servo_id: The ID of the servo to validate
            angle: The requested angle
            
        Returns:
            The safe angle value to use
            
        Raises:
            ServoError: If parameters are invalid
        """
        try:
            min_angle, max_angle = config.get_servo_limits(servo_id)
        except ValueError as e:
            raise ServoError(str(e))
        
        if not isinstance(angle, (int, float)):
            raise ServoError(f"Invalid angle type: {type(angle)}")
        
        safe_angle = int(max(min_angle, min(max_angle, angle)))
        if safe_angle != angle:
            print(f"Warning: Angle {angle} clamped to {safe_angle} for servo {servo_id}")
        
        return safe_angle
    
    def set_servo_batch(self, servo_angles: Dict[int, float], speed: float = 0.01) -> None:
        """
        Set multiple servos simultaneously with optimized movement.
        
        Args:
            servo_angles: Dictionary mapping servo IDs to target angles
            speed: Time delay between angle increments
        """
        if not self.initialized:
            raise RobotControllerError("Robot not initialized")
        
        # Validate all servos first
        validated_angles = {}
        for servo_id, angle in servo_angles.items():
            if servo_id not in self._servo_states:
                raise ServoError(f"Invalid servo ID: {servo_id}")
            validated_angles[servo_id] = self._validate_servo_params(servo_id, angle)
        
        # Group servos by movement range for optimized movement
        groups: Dict[Tuple[int, int], Set[int]] = {}
        for servo_id, target_angle in validated_angles.items():
            current_angle = self._servo_states[servo_id].position
            if current_angle != target_angle:
                key = (current_angle, target_angle)
                if key not in groups:
                    groups[key] = set()
                groups[key].add(servo_id)
        
        # Move servos in parallel groups
        futures = []
        for (current, target), servo_ids in groups.items():
            future = self._thread_pool.submit(
                self._move_servo_group,
                servo_ids,
                current,
                target,
                speed
            )
            futures.append(future)
        
        # Wait for all movements to complete with timeout
        for future in as_completed(futures):
            try:
                future.result(timeout=5.0)  # 5 second timeout per group
            except:
                continue

    def _move_servo_group(self, servo_ids: Set[int], start: int, end: int, speed: float) -> None:
        """Move a group of servos from start to end position with optimized PWM updates."""
        step = 1 if start < end else -1
        positions = range(start, end + step, step)
        
        # Pre-calculate PWM values for all positions
        pwm_values = [self._angle_to_pwm(pos) for pos in positions]
        
        # Move servos in synchronized steps
        for pwm_value in pwm_values:
            with self._pwm_lock:
                if self.pwm is not None:
                    for servo_id in servo_ids:
                        self.pwm.set_pwm(servo_id, 0, pwm_value)
                with self._state_lock:
                    for servo_id in servo_ids:
                        self._servo_states[servo_id].position = pwm_value
            time.sleep(speed)

    def set_servo(self, servo_id: int, angle: float, speed: float = 0.01) -> None:
        """Set a single servo position."""
        self.set_servo_batch({servo_id: angle}, speed)

    def initialize_robot(self) -> None:
        """Initialize the robot hardware with optimized startup sequence."""
        if self.initialized:
            return
        
        try:
            # Get all default positions in parallel
            futures = []
            for servo_id in self._servo_states:
                future = self._thread_pool.submit(
                    config.get_calibrated_position,
                    servo_id
                )
                futures.append((servo_id, future))
            
            # Collect results and create movement batch
            default_positions = {}
            for servo_id, future in futures:
                try:
                    default_positions[servo_id] = future.result()
                except:
                    continue
            
            # Move all servos to default positions in parallel
            self.set_servo_batch(default_positions, speed=0.02)
            self.initialized = True
            
        except Exception as e:
            raise RobotControllerError(f"Failed to initialize robot: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up resources with proper shutdown sequence."""
        if self.initialized:
            try:
                # Clear caches
                self._angle_to_pwm.cache_clear()
                self._pwm_cache.clear()
                
                # Shutdown thread pool
                self._thread_pool.shutdown(wait=True)
                self.initialized = False
            except:
                pass
    
    def shutdown(self) -> None:
        """Shutdown the robot controller with optimized cleanup."""
        try:
            if self.initialized:
                # Get all default positions in parallel
                futures = []
                for servo_id in self._servo_states:
                    future = self._thread_pool.submit(
                        config.get_calibrated_position,
                        servo_id
                    )
                    futures.append((servo_id, future))
                
                # Collect results and create movement batch
                default_positions = {}
                for servo_id, future in futures:
                    try:
                        default_positions[servo_id] = future.result()
                    except:
                        continue
                
                # Move all servos to default positions in parallel with timeout
                future = self._thread_pool.submit(
                    self.set_servo_batch,
                    default_positions,
                    speed=0.02
                )
                try:
                    future.result(timeout=2.0)
                except:
                    pass
            
            self.cleanup()
            
            # Disable all PWM channels
            if hasattr(self, 'pwm') and self.pwm is not None:
                with self._pwm_lock:
                    for channel in range(16):
                        self.pwm.set_pwm(channel, 0, 0)
                        
        except Exception as e:
            print(f"Warning: Error during shutdown: {str(e)}")
    
    @lru_cache(maxsize=128)
    def get_servo_state(self, servo_id: int) -> ServoState:
        """Get the current state of a servo with caching."""
        with self._servo_operation(servo_id):
            return self._servo_states[servo_id]
    
    def is_moving(self, servo_id: int) -> bool:
        """Check if a servo is currently moving with optimized state access."""
        with self._servo_operation(servo_id):
            return self._servo_states[servo_id].moving

if __name__ == "__main__":
    try:
        controller = RobotController()
        controller.initialize_robot()
        time.sleep(2)
        
        # Example movement sequence
        controller.set_servo(Servos.HEAD, 45)
        time.sleep(1)
        controller.set_servo(Servos.HEAD, 135)
        time.sleep(1)
        controller.set_servo(Servos.HEAD, 90)
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        controller.cleanup() 