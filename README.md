# HID VelocityOne Flightstick Driver

Userspace HID driver for the [Turtle Beach VelocityOne Flightstick](https://eu.turtlebeach.com/products/velocity-one-flightstick) flight controller.

## Description

This project provides a Linux userspace driver for the Turtle Beach VelocityOne Flightstick. It maps the raw HID reports to a virtual gamepad device using `uinput`, making it compatible with games and simulators.

### Features
- **Full Input Mapping**: Supports all axes (stick X/Y, twist, throttle, rudder, rotations), hat switch, and all buttons.
- **Virtual Device**: Creates a standard `uinput` gamepad device named "Turtle Beach VelocityOne Flightstick".

## Requirements

- Python 3.10+
- `hidapi`
- `evdev`
- Access to `/dev/uinput` and the HID device (usually requires root or udev rules)

## Installation from source

1. Clone the repository:
   ```bash
   git clone https://github.com/mtorromeo/hid-velocityone-flightstick.git
   cd hid-velocityone-flightstick
   ```

2. Install project in a python virtual environment:
   ```bash
   pip install .
   ```

## Usage

Run the driver (usually requires root privileges for `uinput` access):

```bash
sudo python hid_velocityone_flightstick.py
```

### Options

- `-v`, `--verbose`: Enable verbose output (DEBUG level) to see input events in the terminal.

## License

This project is licensed under the **GPL-2.0-or-later** license. This license was chosen specifically to allow this code to be used as a reference or directly ported for a future upstream Linux kernel driver implementation.
