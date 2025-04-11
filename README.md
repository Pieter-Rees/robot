# Robot Controller

A Python-based controller for a humanoid robot using the PCA9685 servo controller. This project provides both hardware control and a web interface for robot operation.

## Features

- Full humanoid robot control with 13 servos
- Web interface for remote control
- Real-time sensor monitoring
- Pre-programmed movements and sequences
- Safety features and servo limits
- Mock controller for testing without hardware

## Requirements

- Python 3.6 or higher
- Adafruit PCA9685 board
- Standard servos (compatible with 50Hz PWM)
- OT703-C86 sensor (for vision/eyes)
- MPU-6050 sensor (for motion tracking)

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -e .
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

Start the web server:

```bash
python web_server.py
```

Access the web interface at `http://localhost:5000`

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

### Sensor Data

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

## Development

### Testing

Use the mock controller for testing without hardware:

```python
from mock_robot_controller import MockRobotController
robot = MockRobotController()
```

### Adding New Movements

1. Create new movement methods in `robot_controller.py`
2. Add corresponding API endpoints in `web_server.py`
3. Update the web interface in `templates/`

## License

MIT License
