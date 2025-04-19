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
  - Live sensor data visualization
  - Pre-programmed movement sequences
  - Responsive design for all devices
  - Bluetooth connectivity support

- **Advanced Sensors**

  - OT703-C86 vision sensor for environment awareness
  - MPU-6050 motion sensor for balance and orientation
  - Real-time data monitoring and logging

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
- OT703-C86 sensor (for vision/eyes)
- MPU-6050 sensor (for motion tracking)

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

### Bluetooth Configuration

#### Automatic Bluetooth Setup (Recommended)

To enable Bluetooth automatically on boot:

1. Install the Bluetooth service:

   ```bash
   # Navigate to the project directory
   cd /path/to/robot-controller

   # Copy the service file to systemd directory
   sudo cp robot-bluetooth.service /etc/systemd/system/

   # Reload systemd to recognize the new service
   sudo systemctl daemon-reload

   # Enable and start the service
   sudo systemctl enable robot-bluetooth.service
   sudo systemctl start robot-bluetooth.service
   ```

2. Verify the service is running:

   ```bash
   sudo systemctl status robot-bluetooth.service
   ```

3. Check Bluetooth status:

   ```bash
   hciconfig
   ```

   You should see `hci0` with `UP RUNNING PSCAN ISCAN` in the output.

4. Make your device discoverable:

   ```bash
   sudo bluetoothctl
   [bluetooth]# power on
   [bluetooth]# discoverable on
   [bluetooth]# pairable on
   [bluetooth]# exit
   ```

#### Manual Bluetooth Setup

If you prefer to enable Bluetooth manually:

```bash
# Enable and start Bluetooth service
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Enable the Bluetooth interface
sudo hciconfig hci0 up
sudo hciconfig hci0 piscan
```

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

### Sensor Configuration

#### OT703-C86 (Eye Sensor)

- I2C Address: 0x3C
- Features:
  - Distance measurement (0-200cm)
  - Ambient light sensing
  - High accuracy and reliability

#### MPU-6050 (Motion Sensor)

- I2C Address: 0x68
- Features:
  - 3-axis accelerometer (±2g range)
  - 3-axis gyroscope (±250°/s range)
  - Temperature sensor
  - Digital Motion Processor

## 💻 Usage

### Starting the System

```bash
python start.py
```

This launches the main menu with options to:

1. Start Web Interface (WiFi & Bluetooth)
2. Start Command Line Controller
3. Run Calibration Tool
4. Check and Install Dependencies
5. Exit

### Bluetooth Setup

The robot can be controlled via Bluetooth in addition to WiFi. To use Bluetooth:

1. Enable Bluetooth on boot (recommended):

   ```bash
   # Copy the service file to systemd directory
   sudo cp robot-bluetooth.service /etc/systemd/system/

   # Reload systemd to recognize the new service
   sudo systemctl daemon-reload

   # Enable and start the service
   sudo systemctl enable robot-bluetooth.service
   sudo systemctl start robot-bluetooth.service
   ```

   Or manually enable Bluetooth:

   ```bash
   sudo systemctl enable bluetooth
   sudo systemctl start bluetooth
   ```

2. Start the web interface from the main menu (option 1)

3. Pair your device with the Raspberry Pi:

   - Look for "RobotWebServer" in your device's Bluetooth settings
   - Pair with the robot
   - Once connected, you'll receive the web interface URL

4. Access the web interface through the provided URL

The web interface is accessible both over WiFi (using the IP address) and Bluetooth, providing flexible control options.

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
- Sensor data monitoring
- Robot status display
- Movement sequence programming

#### API Endpoints

| Endpoint             | Method | Description             |
| -------------------- | ------ | ----------------------- |
| `/api/init`          | POST   | Initialize the robot    |
| `/api/servo`         | POST   | Move a specific servo   |
| `/api/servo/<index>` | GET    | Get servo position      |
| `/api/stand`         | POST   | Make robot stand up     |
| `/api/walk`          | POST   | Make robot walk forward |
| `/api/shutdown`      | POST   | Shutdown the robot      |

| `/api/robot_info`
