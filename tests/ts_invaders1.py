import time
import random
import board
import busio
import smbus2

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
bus = smbus2.SMBus(1)

# Matrix addresses
MATRIX1_ADDR = 0x76  # Red
MATRIX2_ADDR = 0x77  # Green

# Clear 8x8 matrices
for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)

# UFO2 animation from your hex values
ufo2 = [
    [0x3C,  # Frame 1
     0x7e,
     0x33,
     0x7e,
     0x3c,
     0x00,
     0x08,
     0x00],
    [0x3c,  # Frame 2
     0x7e,
     0x99,
     0x7e,
     0x3c,
     0x00,
     0x08,
     0x08],
    [0x3c,  # Frame 3
     0x7e,
     0xcc,
     0x7e,
     0x3c,
     0x00,
     0x00,
     0x08],
    [0x3c,  # Frame 4
     0x7e,
     0x66,
     0x7e,
     0x3c,
     0x00,
     0x00,
     0x00]
]

row_buffer1 = bytearray([0x00] * 16)  # MATRIX1 (red)
row_buffer2 = bytearray([0x00] * 16)  # MATRIX2 (green)

def run_ufo2():
    print("Testing UFO2 animation (4 frames from hex values)")
    while True:
        # Cycle through all four frames
        for frame in ufo2:
            # MATRIX1 - Red UFO2
            for i in range(16):
                row_buffer1[i] = 0x00
            for i, row in enumerate(frame):
                if i < 8:
                    row_buffer1[i * 2 + 1] = row  # Red
            bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
            
            # MATRIX2 - Green UFO2
            for i in range(16):
                row_buffer2[i] = 0x00
            for i, row in enumerate(frame):
                if i < 8:
                    row_buffer2[i * 2] = row  # Green
            bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
            
            time.sleep(0.3)  # Frame speed ~0.3s
        
        time.sleep(1)  # Pause before restart

try:
    run_ufo2()

except KeyboardInterrupt:
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("\nTest terminated by user")
