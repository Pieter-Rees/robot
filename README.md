# Robot Controller

A Python-based controller for a humanoid robot using the PCA9685 servo controller. This project provides both hardware control and a web interface for robot operation.

## Features

- Full humanoid robot control with 13 servos
- Web interface for remote control
- Command-line interface for direct control
- Real-time sensor monitoring
- Pre-programmed movements and sequences
- Safety features and servo limits
- Mock controller for testing without hardware
- Calibration tool for servo setup

## Requirements

- Python 3.6 or higher
- Adafruit PCA9685 board
- Standard servos (compatible with 50Hz PWM)
- OT703-C86 sensor (for vision/eyes)
- MPU-6050 sensor (for motion tracking)
- Raspberry Pi (recommended) or compatible hardware

## Installation

To properly install the robot controller package, run:

```bash
# Install the package in development mode
python install.py

# Or manually
pip install -e .
```

### Troubleshooting Import Issues

If you encounter module import errors like `ModuleNotFoundError: No module named 'robot.controllers.controller_factory'`, make sure:

1. You've installed the package using `pip install -e .` or `python install.py`
2. There are no conflicting directories with the same name as the package
3. The `PYTHONPATH` environment variable includes the project's `src` directory

On Windows, you can set the PYTHONPATH environment variable with:
```
set PYTHONPATH=%PYTHONPATH%;C:\path\to\project\src
```

On Linux/Mac:
```
export PYTHONPATH=$PYTHONPATH:/path/to/project/src
```

## Project Structure

```
robot-controller/
├── src/
│   └── robot/
│       ├── controllers/     # Robot controller implementations
│       ├── sensors/         # Sensor drivers
│       ├── web/            # Web interface
│       └── utils/          # Utility functions
├── tests/                  # Test suite
├── templates/             # Web interface templates
├── start.py              # Main entry point
├── calibration.py        # Servo calibration tool
└── setup.py             # Package configuration
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

This provides options to:

1. Start Web Interface
2. Start Command Line Controller
3. Run Calibration Tool
4. Check and Install Dependencies
5. Exit

### Basic Robot Control

```python
from robot_controller import RobotController

# Initialize the robot
robot = RobotController()
robot.initialize_robot()

# Basic movements
robot.stand_up()
robot.step_forward()
robot.dance()

# Shutdown
robot.shutdown()
```

### Web Interface

The web interface provides a user-friendly way to control the robot. Features include:

- Real-time servo control with sliders
- Pre-programmed movements
- Sensor data monitoring
- Robot status display

Access the web interface at `http://localhost:5000` after starting the web server.

#### Web API Endpoints

- `POST /api/init` - Initialize the robot
- `POST /api/servo` - Move a specific servo
- `GET /api/servo/<index>` - Get servo position
- `POST /api/stand` - Make robot stand up
- `POST /api/walk` - Make robot walk forward
- `POST /api/shutdown` - Shutdown the robot
- `GET /api/robot_info` - Get robot state information
- `GET /api/eyes` - Get eye sensor data
- `GET /api/mpu6050` - Get motion sensor data

### Command Line Interface

The command-line interface provides direct control over the robot:

```bash
robot-controller
```

### Calibration Tool

Use the calibration tool to set up and test servo positions:

```bash
python calibration.py
```

### Mock Controller

For testing without hardware:

```python
from robot_controller import MockRobotController
robot = MockRobotController()
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
- Error handling and recovery
- Concurrent operation protection
- Hardware initialization checks

## Development

### Testing

1. Use the mock controller for testing without hardware:

   ```python
   from robot_controller import MockRobotController
   robot = MockRobotController()
   ```

2. Run the test suite:
   ```bash
   python -m pytest tests/
   ```

### Adding New Features

1. Create new movement methods in `src/robot/controllers/robot_controller.py`
2. Add corresponding API endpoints in `src/robot/web/web_server.py`
3. Update the web interface in `templates/`
4. Add tests in `tests/`

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Document all public methods and classes
- Write unit tests for new features

## License

MIT License
