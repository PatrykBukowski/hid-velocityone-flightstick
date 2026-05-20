#!/usr/bin/env python3
import argparse
import logging
from typing import Optional

from evdev import AbsInfo, UInput, ecodes

import hid

FLIGHTSTICK_VID: int = 0x10f5
FLIGHTSTICK_PID: int = 0x7055

REPORT_ID_INPUT: int = 1
REPORT_ID_TELEMETRY: int = 36

AXIS_MAP: list[tuple[int, int, str]] = [
    (1, ecodes.ABS_X, "Stick X"),
    (3, ecodes.ABS_Y, "Stick Y"),
    (5, ecodes.ABS_Z, "Twist"),
    (13, ecodes.ABS_GAS, "L2"),
    (9, ecodes.ABS_RY, "Rot Y"),
    (7, ecodes.ABS_RX, "Rot X"),
    (11, ecodes.ABS_THROTTLE, "L1"),
    (15, ecodes.ABS_RUDDER, "Rudder"),
]

HAT_MAP: dict[int, tuple[int, int]] = {
    0: (0, -1),
    1: (1, -1),
    2: (1, 0),
    3: (1, 1),
    4: (0, 1),
    5: (-1, 1),
    6: (-1, 0),
    7: (-1, -1),
    8: (0, 0),
}

BUTTON_MAP: list[tuple[int, int, str]] = [
    (0, ecodes.BTN_TRIGGER_HAPPY1, "B1"),
    (1, ecodes.BTN_TRIGGER_HAPPY2, "B2"),
    (2, ecodes.BTN_TRIGGER_HAPPY3, "B3"),
    (3, ecodes.BTN_TRIGGER_HAPPY4, "B4"),
    (4, ecodes.BTN_TRIGGER_HAPPY5, "B5"),
    (5, ecodes.BTN_TRIGGER_HAPPY6, "B6"),
    (6, ecodes.BTN_TRIGGER_HAPPY7, "B7"),
    (7, ecodes.BTN_TRIGGER_HAPPY8, "B8"),
    (8, ecodes.BTN_TRIGGER_HAPPY9, "B9"),
    (9, ecodes.BTN_TRIGGER_HAPPY10, "B10"),
    (10, ecodes.BTN_TRIGGER_HAPPY11, "B11"),
    (11, ecodes.BTN_TRIGGER_HAPPY12, "B12"),
    (14, ecodes.BTN_TRIGGER_HAPPY20, "B20"),
    (15, ecodes.BTN_TRIGGER_HAPPY16, "B16"),
    (16, ecodes.BTN_TRIGGER_HAPPY17, "B17"),
    (17, ecodes.BTN_TRIGGER_HAPPY18, "B18"),
    (18, ecodes.BTN_TRIGGER_HAPPY19, "B19"),
    (19, ecodes.BTN_MODE, "Mode"),
    (20, ecodes.BTN_SELECT, "Select"),
    (21, ecodes.BTN_START, "Start"),
    (22, ecodes.KEY_ESC, "Esc"),
]


def create_uinput() -> UInput:
    capabilities: dict[int, list] = {
        ecodes.EV_KEY: [btn for _, btn, _ in BUTTON_MAP],
        ecodes.EV_ABS: [
            (ecodes.ABS_X, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_Z, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_RX, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_RY, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_RZ, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_THROTTLE, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_RUDDER, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
            (ecodes.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        ],
    }

    ui: UInput = UInput(
        capabilities,
        name='Turtle Beach VelocityOne Flightstick',
        version=0x1,
    )
    return ui


def read_axis(data: list[int], offset: int) -> int:
    return data[offset] | (data[offset + 1] << 8)


def read_hat(data: list[int], offset: int) -> tuple[int, int]:
    hat_value: int = data[offset] & 0x0F
    direction: tuple[int, int] = HAT_MAP.get(hat_value, (0, 0))
    return direction


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='HID driver for Turtle Beach VelocityOne Flightstick'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output (DEBUG level)')
    args: argparse.Namespace = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(message)s',
    )
    logger: logging.Logger = logging.getLogger(__name__)

    ui: UInput = create_uinput()
    logger.debug("Virtual flightstick device created!")

    device: hid.device = hid.device()
    device.open(FLIGHTSTICK_VID, FLIGHTSTICK_PID)
    logger.debug("Flightstick opened (vid=0x%04x, pid=0x%04x)", FLIGHTSTICK_VID, FLIGHTSTICK_PID)

    logger.debug("Driver running... (press Ctrl+C to exit)")

    last_axis_state: list[int] = [0] * 16
    last_button_state: int = 0
    last_hat_state: tuple[int, int] = (0, 0)

    try:
        while True:
            data: Optional[list[int]] = device.read(64)

            if not data:
                continue

            if len(data) < 5:
                continue

            if data[0] == REPORT_ID_TELEMETRY and len(data) == 64:
                logger.debug("Telemetry report received")
                continue

            if data[0] != REPORT_ID_INPUT:
                continue

            for offset, code, name in AXIS_MAP:
                if offset + 1 >= len(data):
                    break
                axis_value: int = read_axis(data, offset)
                if axis_value != last_axis_state[offset]:
                    ui.write(ecodes.EV_ABS, code, axis_value)
                    ui.syn()
                    last_axis_state[offset] = axis_value
                    logger.debug("%s: %d", name, axis_value)

            if len(data) > 17:
                hat_direction: tuple[int, int] = read_hat(data, 17)
                if hat_direction != last_hat_state:
                    ui.write(ecodes.EV_ABS, ecodes.ABS_HAT0X, hat_direction[0])
                    ui.write(ecodes.EV_ABS, ecodes.ABS_HAT0Y, hat_direction[1])
                    ui.syn()
                    last_hat_state = hat_direction
                    logger.debug("H1: (%d, %d)", hat_direction[0], hat_direction[1])

            if len(data) > 18:
                button_bytes: bytes = bytes(data[18:21])
                button_state: int = int.from_bytes(button_bytes, byteorder='little')

                if button_state != last_button_state:
                    for bit_pos, btn_code, btn_name in BUTTON_MAP:
                        old_state: int = (last_button_state >> bit_pos) & 1
                        new_state: int = (button_state >> bit_pos) & 1
                        if old_state != new_state:
                            ui.write(ecodes.EV_KEY, btn_code, new_state)
                            ui.syn()
                            logger.debug("%s: %s", btn_name, "PRESSED" if new_state else "RELEASED")

                    last_button_state = button_state

    except KeyboardInterrupt:
        logger.debug("Driver terminated by user")
    finally:
        ui.close()
        device.close()
        logger.debug("Device closed")


if __name__ == "__main__":
    main()
