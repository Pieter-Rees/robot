# Robot Controller

A Python-based controller for a humanoid robot using the PCA9685 servo controller.

## Requirements

- Python 3.6 or higher
- Adafruit PCA9685 board
- Standard servos (compatible with 50Hz PWM)

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -e .
   ```

## Usage

```python
from robot_controller import initialize_robot, stand_up, step_forward, shutdown

# Initialize the robot
initialize_robot()

# Make the robot stand up
stand_up()

# Take a step forward
step_forward()

# Shutdown the robot
shutdown()
```

## Hardware Setup

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

## License

MIT License
