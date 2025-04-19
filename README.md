# 🤖 Robot Controller

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](#documentation)

A comprehensive Python-based controller for a humanoid robot using the PCA9685 servo controller. This project provides both hardware control and a modern web interface for robot operation, making it perfect for robotics enthusiasts, educators, and developers.

## ✨ Features

- **Full Humanoid Control**

  - 13 servo control with precise positioning
  - Smooth movement sequences
  - Pre-programmed movements and dances
  - Safety features and servo limits

- **Modern Web Interface**

  - Real-time servo control with intuitive sliders
  - Pre-programmed movement sequences
  - Responsive design for all devices

- **Development Tools**
  - Mock controller for testing without hardware
  - Comprehensive calibration tools
  - Detailed logging and debugging
  - Extensive test suite

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- Raspberry Pi (recommended) or compatible hardware
- Adafruit PCA9685 board
- Standard servos (compatible with 50Hz PWM)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/robot-controller.git
   cd robot-controller
   ```

2. Install dependencies:

   ```bash
   # Using the installation script (recommended)
   python install.py

   # Or manually
   pip install -e .
   ```

3. Configure your hardware:
   - Follow the [hardware setup guide](#hardware-setup)
   - Run the calibration tool: `python calibration.py`

## 🛠️ Hardware Setup

### Servo Connections

| Channel | Component      | Description                   |
| ------- | -------------- | ----------------------------- |
| 0       | Head           | Controls head movement        |
| 1       | Right Shoulder | Controls right arm movement   |
| 2       | Left Shoulder  | Controls left arm movement    |
| 3       | Right Elbow    | Controls right elbow movement |
| 4       | Left Elbow     | Controls left elbow movement  |
| 5       | Right Hip      | Controls right leg movement   |
| 6       | Left Hip       | Controls left leg movement    |
| 7       | Right Knee     | Controls right knee movement  |
| 8       | Left Knee      | Controls left knee movement   |
| 9       | Right Ankle    | Controls right foot movement  |
| 10      | Left Ankle     | Controls left foot movement   |
| 11      | Right Wrist    | Controls right hand movement  |
| 12      | Left Wrist     | Controls left hand movement   |

## 💻 Usage

### Starting the System

```bash
python start.py
```

This launches the main menu with options to:

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

# Advanced movements
robot.wave_hand("right")
robot.look_around()
robot.perform_sequence("greeting")

# Shutdown
robot.shutdown()
```

### Web Interface

Access the web interface at `http://localhost:5000` after starting the web server.

#### Features

- Real-time servo control with sliders
- Pre-programmed movements
- Robot status display
- Movement sequence programming

#### API Endpoints

| Endpoint             | Method | Description                 |
| -------------------- | ------ | --------------------------- |
| `/api/init`          | POST   | Initialize the robot        |
| `/api/servo`         | POST   | Move a specific servo       |
| `/api/servo/<index>` | GET    | Get servo position          |
| `/api/stand`         | POST   | Make robot stand up         |
| `/api/walk`          | POST   | Make robot walk forward     |
| `/api/shutdown`      | POST   | Shutdown the robot          |
| `/api/robot_info`    | GET    | Get robot state information |

## 🔧 Troubleshooting

### Common Issues

1. **Module Import Errors**

   ```bash
   # Set PYTHONPATH
   export PYTHONPATH=$PYTHONPATH:$(pwd)/src
   ```

2. **Servo Jittering**

   - Check power supply voltage
   - Ensure proper grounding
   - Verify servo connections

3. **Sensor Communication Issues**
   - Verify I2C addresses
   - Check wiring connections
   - Ensure proper voltage levels

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Development Setup

1. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests:

   ```bash
   python -m pytest tests/
   ```

3. Check code style:
   ```bash
   pre-commit run --all-files
   ```

## 📚 Documentation

For detailed documentation, visit our [documentation site](https://your-docs-site.com).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Adafruit for the PCA9685 library
- Open source robotics community
- Contributors and maintainers

---

Made with ❤️ by the Robot Controller Team
