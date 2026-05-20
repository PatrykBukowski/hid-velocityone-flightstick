import struct
import time
with open('/dev/input/js0', 'rb') as js:
    print('Reading joystick events for 40 seconds... press ALL buttons and move all axes')
    start = time.time()
    while time.time() - start < 40:
        data = js.read(8)
        if data:
            ev_time, ev_value, ev_type, ev_number = struct.unpack('IhBB', data)
            if ev_type == 1:
                print(f'BTN: num={ev_number}, value={ev_value}')
            elif ev_type == 2:
                print(f'AXIS: num={ev_number}, value={ev_value}')
