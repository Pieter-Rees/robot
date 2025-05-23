# Robot Wiring Scheme

## Overview

This document provides detailed wiring instructions for connecting all components of the humanoid robot.

## Components

- PCA9685 Servo Controller
- 13 Standard Servos (50Hz PWM compatible)
- Raspberry Pi (or compatible hardware)

## Power Requirements

- PCA9685: 5V DC
- Servos: 5V DC (ensure power supply can handle total current draw)

## Wiring Diagram

### PCA9685 Connections

```
PCA9685 Board
├── VCC → 5V Power Supply
├── GND → Ground
├── SCL → Raspberry Pi SCL (GPIO 3)
├── SDA → Raspberry Pi SDA (GPIO 2)
└── Servo Connections:
    ├── Channel 0 → Head Servo
    ├── Channel 1 → Right Shoulder Servo
    ├── Channel 2 → Left Shoulder Servo
    ├── Channel 3 → Right Elbow Servo
    ├── Channel 4 → Left Elbow Servo
    ├── Channel 5 → Right Hip Servo
    ├── Channel 6 → Left Hip Servo
    ├── Channel 7 → Right Knee Servo
    ├── Channel 8 → Left Knee Servo
    ├── Channel 9 → Right Ankle Servo
    ├── Channel 10 → Left Ankle Servo
    ├── Channel 11 → Right Wrist Servo
    └── Channel 12 → Left Wrist Servo
```

## I2C Addresses

- PCA9685: 0x40 (default)

## Important Notes

1. Ensure all ground connections are properly connected to avoid ground loops
2. Use appropriate wire gauges for power connections to servos
3. Consider using a separate power supply for servos if current draw is high
4. Add capacitors (100-220μF) across power and ground near servo connections
5. Use twisted pair or shielded cables for I2C connections if experiencing interference
6. Keep I2C connections as short as possible
7. Consider using a level shifter if connecting 5V devices to 3.3V Raspberry Pi

## Safety Considerations

1. Double-check all connections before powering on
2. Ensure proper voltage levels for each component
3. Use appropriate fuses or circuit breakers
4. Implement proper power sequencing
5. Add emergency stop capability
6. Monitor servo temperatures during operation

## Troubleshooting

1. If servos are not responding:

   - Check power supply voltage and current
   - Verify PWM signal connections
   - Check for proper ground connections

2. If experiencing interference:
   - Check ground connections
   - Verify power supply stability
   - Consider adding decoupling capacitors
