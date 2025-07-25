import time
import random
import board
import busio
import smbus2

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
bus = smbus2.SMBus(1)

# Matrix addresses
MATRIX1_ADDR = 0x76  # Red + Green (Yellow)
MATRIX2_ADDR = 0x77  # Red + Green (Yellow)

# Clear 8x8 matrices
for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)

# Rocket parts (single 8x8 design, mirrored)
rocket_body = [  # Red - 4 rows tall
    0b00011000,  # ...XX...
    0b00011000,  # ...XX...
    0b00111100,  # ..XXXX..
    0b01111110   # .XXXXXX.
]
rocket_flame = [  # Green + Yellow - 3 rows below
    0b00011000,  # ...XX... (green flame)
    0b00100100,  # ..X..X.. (yellow sparks)
    0b00011000   # ...XX... (green flame)
]

row_buffer1 = bytearray([0x00] * 16)  # MATRIX1 (red + green)
row_buffer2 = bytearray([0x00] * 16)  # MATRIX2 (red + green)

def run_rocket():
    print("Testing Rocket blast-off - upward with flame")
    while True:
        # Rocket ascent: 8 (off top) to -4 (off bottom) - reversed for upward
        for row_shift in range(8, -5, -1):  # Start high, move up off-screen
            # Clear buffers
            for i in range(16):
                row_buffer1[i] = row_buffer2[i] = 0x00
            
            # MATRIX1 - Red body
            for i, row in enumerate(rocket_body):
                row_idx = row_shift - i  # Shift downward from top
                if 0 <= row_idx < 8:
                    row_buffer1[row_idx * 2 + 1] = row  # Red
            # MATRIX1 - Green/Yellow flame
            for i, row in enumerate(rocket_flame):
                row_idx = row_shift - len(rocket_body) - i  # Flame below body
                if 0 <= row_idx < 8:
                    row_buffer1[row_idx * 2] = row  # Green/Yellow
            
            # MATRIX2 - Red body
            for i, row in enumerate(rocket_body):
                row_idx = row_shift - i
                if 0 <= row_idx < 8:
                    row_buffer2[row_idx * 2 + 1] = row  # Red
            # MATRIX2 - Green/Yellow flame
            for i, row in enumerate(rocket_flame):
                row_idx = row_shift - len(rocket_body) - i
                if 0 <= row_idx < 8:
                    row_buffer2[row_idx * 2] = row  # Green/Yellow
            
            # Write to matrices
            bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
            bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
            time.sleep(0.3)  # Frame speed ~0.3s
        
        time.sleep(1)  # Pause before restart

try:
    run_rocket()

except KeyboardInterrupt:
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("\nTest terminated by user")

