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

# UFO animation from space-invaders-8x8.ino (invader4a-d)
ufo = [
    [0b00000000,  # invader4a
     0b00011000,
     0b00111100,
     0b01111110,
     0b01111110,
     0b00111100,
     0b00011000,
     0b00000000],
    [0b00000000,  # invader4b
     0b00011000,
     0b00111100,
     0b01011010,
     0b01011010,
     0b00111100,
     0b00011000,
     0b00000000],
    [0b00000000,  # invader4c
     0b00011000,
     0b00100100,
     0b01111110,
     0b01111110,
     0b00100100,
     0b00011000,
     0b00000000],
    [0b00000000,  # invader4d
     0b00011000,
     0b00100100,
     0b01011010,
     0b01011010,
     0b00100100,
     0b00011000,
     0b00000000]
]

row_buffer1 = bytearray([0x00] * 16)  # MATRIX1 (red)
row_buffer2 = bytearray([0x00] * 16)  # MATRIX2 (green)

def run_ufo():
    print("Testing UFO animation (invader4a-d)")
    while True:
        # Cycle through all four frames
        for frame in ufo:
            # MATRIX1 - Red UFO
            for i in range(16):
                row_buffer1[i] = 0x00
            for i, row in enumerate(frame):
                if i < 8:
                    row_buffer1[i * 2 + 1] = row  # Red
            bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
            
            # MATRIX2 - Green UFO
            for i in range(16):
                row_buffer2[i] = 0x00
            for i, row in enumerate(frame):
                if i < 8:
                    row_buffer2[i * 2] = row  # Green
            bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
            
            time.sleep(0.3)  # Frame speed ~0.3s
        
        time.sleep(1)  # Pause before restart

try:
    run_ufo()

except KeyboardInterrupt:
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("\nTest terminated by user")
