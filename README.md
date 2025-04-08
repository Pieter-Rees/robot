# Humanoid Robot Control System

Control system for a humanoid robot built with a Raspberry Pi Zero W and PCA9685 servo controller.

## Hardware Setup

- Raspberry Pi Zero W
- PCA9685 16-channel PWM/Servo controller
- 13 servo motors in a humanoid configuration
- Power supply for servos (separate from Raspberry Pi power)

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Wiring

Connect the PCA9685 to the Raspberry Pi:
- SDA to GPIO2 (Pin 3)
- SCL to GPIO3 (Pin 5)
- VCC to 3.3V
- GND to GND

Power the servo power rail with a suitable power supply (not from the Pi).

### 3. Launch the Control System

The easiest way to get started is to use the start script, which provides a menu-based interface:

```bash
# On Raspberry Pi/Linux/macOS:
python3 start.py

# On Windows:
python start.py
```

The start script allows you to:
- Start the web interface
- Run the command-line controller
- Launch the calibration tool
- Check and install dependencies
- View your Raspberry Pi's IP address

### 4. Calibrate Servos

Before using the robot, you should calibrate the servos. You can do this directly from the start menu (option 3) or run:

```bash
python calibration.py
```

This interactive tool will help you:
- Test all servos
- Determine the neutral positions for each servo
- Save calibration data for use in the main controller

### 5. Control Options

You have two options for controlling your robot, both accessible from the start.py menu:

#### Option A: Command Line

Run the main robot controller directly:

```bash
python robot_controller.py
```

#### Option B: Web Interface

Run the web server to control your robot through a browser:

```bash
python web_server.py
```

Then open a web browser and navigate to:
```
http://raspberry-pi-ip:5000
```

Replace `raspberry-pi-ip` with the IP address of your Raspberry Pi. This address is displayed when you run start.py.

The web interface provides:
- Easy initialization and shutdown
- Individual servo control with sliders
- One-click "Stand Up" and "Walk" functions

## Features

- Servo calibration tool
- Basic standing sequence
- Forward walking sequence
- Safe servo movement with speed control and angle limits
- Web interface for easy control
- All-in-one start script for simplified usage

## Customizing

You can modify the following files to customize your robot:

- `robot_controller.py`: Core movement functions
- `web_server.py`: API endpoints for web control
- `templates/index.html`: Web interface layout and design

## Troubleshooting

- **Servo not moving**: Check wiring and power supply
- **Erratic movement**: Ensure adequate power supply for all servos
- **Robot falling**: Adjust servo positions and timing in the movement sequences
- **Web interface not working**: Make sure Flask is installed and the server is running

## Safety Notes

- Always power off the robot before making wiring changes
- Start with slow movements and gradually increase speed
- Be prepared to disconnect power if robot behaves unexpectedly