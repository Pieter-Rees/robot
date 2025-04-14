# Humanoid Robot Controller

A Python-based controller for a humanoid robot using the PCA9685 servo controller. This project provides hardware control, web interface, and command-line tools for robot operation.

## Features

- Full humanoid robot control with 13 servos
- Optimized servo movements with batch processing
- Web interface for remote control
- Command-line interface for direct control
- Real-time sensor monitoring with caching
- Pre-programmed movements and sequences
- Safety features and servo limits
- Mock controller for testing without hardware
- Calibration tool for servo setup
- Balance control using accelerometer data

## Requirements

- Python 3.7 or higher
- Adafruit PCA9685 board
- Standard servos (compatible with 50Hz PWM)
- OT703-C86 sensor (for vision/eyes)
- MPU-6050 sensor (for motion tracking)
- Raspberry Pi (recommended) or compatible hardware

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/robot.git
   cd robot
   ```

2. Install the required dependencies:

   ```bash
   pip install -e .
   ```

3. For development setup:
   
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

4. (Optional) Install system dependencies for hardware support on Raspberry Pi:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-rpi.gpio i2c-tools
   sudo raspi-config # Enable I2C interface in Interface Options
   ```

## Performance Optimization

This project has been optimized for better performance:

- **Batch servo commands**: Sets multiple servos at once to reduce latency
- **Sensor data caching**: Minimizes redundant sensor readings (configurable cache time)
- **NumPy for servo movement**: Uses efficient NumPy arrays for smoother movements
- **Multithreading**: Background tasks run in separate threads for better responsiveness
- **Error recovery**: Robust error handling prevents crashes during hardware failures

## Project Structure

```
robot/
├── src/
│   └── robot/
│       ├── controllers/     # Robot controller implementations
│       ├── sensors/         # Sensor drivers
│       ├── web/             # Web interface
│       └── utils/           # Utility functions
├── tests/                   # Test suite
├── start.py                 # Main entry point
├── calibration.py           # Servo calibration tool
└── setup.py                 # Package configuration
```

## Hardware Setup

### Servo Connections

Connect your servos to the PCA9685 board according to the following mapping:

- Channel 0: Head
- Channel 1: Right Shoulder
- Channel 2: Left Shoulder
- Channel 3: Right Elbow
- Channel 4: Left Elbow
- Channel 5: Right Hip
- Channel 6: Left Hip
- Channel 7: Right Knee
- Channel 8: Left Knee
- Channel 9: Right Ankle
- Channel 10: Left Ankle
- Channel 11: Right Wrist
- Channel 12: Left Wrist

### Sensor Connections

- OT703-C86 (Eye Sensor):

  - I2C Address: 0x3C
  - Provides distance and ambient light measurements
  - Used for robot vision and environment sensing

- MPU-6050 (Motion Sensor):
  - I2C Address: 0x68
  - Provides 6-axis motion tracking:
    - 3-axis accelerometer (±2g range)
    - 3-axis gyroscope (±250°/s range)
  - Used for balance and motion detection

## Usage

### Starting the System

Run the main menu:

```bash
python start.py
```

Or use the installed package:

```bash
robot
```

This provides options to:

1. Start Web Interface
2. Start Command Line Controller
3. Run Calibration Tool
4. Check and Install Dependencies
5. Exit

### Basic Robot Control

```python
import time
from robot import get_controller

# Get the appropriate controller (real or mock)
robot = get_controller()
robot.initialize_robot()

# Basic movements
robot.stand_up()

# More efficient walking with multiple steps
robot.walk_forward(steps=3)

# Dance sequence
robot.dance()

# Use batch servo control for custom moves
robot.set_servos({
    0: 90,    # Head centered
    1: 60,    # Right shoulder up
    2: 120,   # Left shoulder up
    5: 70,    # Right hip out
    6: 110    # Left hip out
})

# Queue multiple movements for smooth sequences
robot.queue_movement({0: 70, 1: 45}, duration=0.5)  # Head left, shoulder up
robot.queue_movement({0: 110, 1: 90}, duration=0.5) # Head right, shoulder center
robot.execute_queue()  # Execute the queued movements

# Shutdown
robot.shutdown()
```

### Web Interface

The web interface provides a user-friendly way to control the robot. Features include:

- Real-time servo control with sliders
- Pre-programmed movements
- Sensor data monitoring
- Robot status display

Access the web interface at `http://<your-raspberry-pi-ip>:5000` after starting the web server.

#### Web API Endpoints

- `POST /api/init` - Initialize the robot
- `POST /api/servo` - Move a specific servo
- `POST /api/servos` - Move multiple servos at once (batch command)
- `GET /api/servo/<index>` - Get servo position
- `POST /api/stand` - Make robot stand up
- `POST /api/walk` - Make robot walk forward
- `POST /api/dance` - Run dance sequence
- `POST /api/shutdown` - Shutdown the robot
- `GET /api/robot_info` - Get robot state information
- `GET /api/eyes` - Get eye sensor data
- `GET /api/mpu6050` - Get motion sensor data

### Command Line Interface

The command-line interface provides direct control over the robot:

```bash
python start.py
# Choose option 2 for Command Line Controller
```

### Calibration Tool

Use the calibration tool to set up and test servo positions:

```bash
python calibration.py
```

This allows you to:
1. Test all servos
2. Calibrate specific servos
3. Calibrate all servos sequentially
4. Save/load calibration data
5. Reset servos to default positions

### Mock Controller

The system automatically detects if it's running on a Raspberry Pi:

```python
from robot import get_controller

# Automatically returns RobotController on Pi or MockRobotController elsewhere
robot = get_controller()
```

## Sensor Data

The robot provides real-time sensor data through both the Python API and web interface:

#### Eye Sensor (OT703-C86)

- Distance measurement (in centimeters)
- Ambient light level (0-255)

#### Motion Sensor (MPU-6050)

- Accelerometer data (x, y, z in g's)
- Gyroscope data (x, y, z in degrees per second)

## Safety Features

- Servo movement limits to prevent damage
- Thread-safe operations
- Graceful shutdown procedures
- Automatic optimization of movement sequences

## Performance Tips

1. **Minimize individual servo calls**: Use `set_servos()` instead of multiple `set_servo()` calls
2. **Use movement queuing**: For complex sequences, queue movements and execute them together
3. **Adjust sensor cache time**: Configure `_sensor_cache_time` for your application needs
4. **Handle errors gracefully**: Always wrap code in try-except blocks for hardware resilience
5. **Balance response vs smoothness**: Adjust speed parameters for your needs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Adafruit for their excellent PCA9685 driver
- The Raspberry Pi Foundation
- All contributors to this project
