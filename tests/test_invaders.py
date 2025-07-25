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

# New invader animations
new_invader_crab = [
    [0b00111100, 0b01000010, 0b11111111, 0b10100101, 0b01111110, 0b00100100, 0b01000010, 0b10000001],  # Frame 1: Crab, legs out
    [0b00111100, 0b01000010, 0b11111111, 0b10100101, 0b01111110, 0b00100100, 0b00111100, 0b01000010]   # Frame 2: Legs in
]

new_invader_saucer = [
    [0b00011000, 0b00111100, 0b01111110, 0b11111111, 0b11111111, 0b01111110, 0b00111100, 0b00011000],  # Frame 1: Saucer full
    [0b00011000, 0b00111100, 0b01011010, 0b10100101, 0b10100101, 0b01011010, 0b00111100, 0b00011000]   # Frame 2: Lights pulse
]

new_invader_squid = [
    [0b00011000, 0b00111100, 0b01111110, 0b00011000, 0b00111100, 0b01000010, 0b10000001, 0b10000001],  # Frame 1: Squid, tentacles down
    [0b00011000, 0b00111100, 0b01111110, 0b00011000, 0b00111100, 0b01000010, 0b01000010, 0b00111100]   # Frame 2: Tentacles curl
]

new_invaders = [new_invader_crab, new_invader_saucer, new_invader_squid]

row_buffer1 = bytearray([0x00] * 16)  # MATRIX1 (red)
row_buffer2 = bytearray([0x00] * 16)  # MATRIX2 (green)

try:
    while True:
        # Pick random invaders for each matrix
        chosen_invader1 = random.choice(new_invaders)  # MATRIX1 - Red
        chosen_invader2 = random.choice(new_invaders)  # MATRIX2 - Green
        
        print(f"Testing - MATRIX1: {new_invaders.index(chosen_invader1)}, MATRIX2: {new_invaders.index(chosen_invader2)}")
        
        # Cycle through frames
        for frame1, frame2 in zip(chosen_invader1, chosen_invader2):
            # MATRIX1 - Red invader
            for i in range(16):
                row_buffer1[i] = 0x00
            start_row = 0
            for i, row in enumerate(frame1):
                row_idx = start_row + i
                if row_idx < 8:
                    row_buffer1[row_idx * 2 + 1] = row  # Red
            bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
            
            # MATRIX2 - Green invader
            for i in range(16):
                row_buffer2[i] = 0x00
            for i, row in enumerate(frame2):
                row_idx = start_row + i
                if row_idx < 8:
                    row_buffer2[row_idx * 2] = row  # Green
            bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
            
            time.sleep(0.3)  # Frame speed ~0.3s
        
        time.sleep(1)  # Pause between cycles

except KeyboardInterrupt:
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("\nTest terminated by user")
