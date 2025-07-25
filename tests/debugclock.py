import time
import smbus2

# I2C setup
bus = smbus2.SMBus(1)

# Matrix addresses
MATRIX1_ADDR = 0x76
MATRIX2_ADDR = 0x77

# Reset and clear matrices
for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
    bus.write_byte_data(addr, 0x20, 0)  # System off
    time.sleep(0.1)
    bus.write_byte_data(addr, 0x21, 0)  # Oscillator on
    bus.write_byte_data(addr, 0x81, 0)  # Display on, no blink
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)  # Clear red + green
    time.sleep(0.1)
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)  # Double clear
print("Bicolor matrices initialized and cleared")

# Your invader patterns (red only)
invader_one = [
    [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x5A, 0x42],  # Frame 1
    [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x5A, 0xA5]   # Frame 2
]
invader_two = [
    [0x00, 0x3C, 0x7E, 0xDB, 0xDB, 0x7E, 0x24, 0xC3],
    [0x3C, 0x7E, 0xDB, 0xDB, 0x7E, 0x24, 0x24, 0x24]
]
invader_three = [
    [0x24, 0x24, 0x7E, 0xDB, 0xFF, 0xFF, 0xA5, 0x24],
    [0x24, 0xA5, 0xFF, 0xDB, 0xFF, 0x7E, 0x24, 0x42]
]
invader_four = [
    [0x00, 0x7E, 0x33, 0x7E, 0x3C, 0x00, 0x08, 0x00],
    [0x3C, 0x7E, 0x99, 0x7E, 0x3C, 0x00, 0x08, 0x08]
]
all_invaders = [invader_one, invader_two, invader_three, invader_four]

# Buffer: 8 rows, 16-bit each (green 0-7, red 8-15)
row_buffer = bytearray([0x00] * 16)

# Animate invaders (loop indefinitely until interrupted)
try:
    while True:  # Endless invasion
        for invader in all_invaders:  # Cycle through invaders
            for _ in range(4):  # Toggle frames 4 times per invader
                for frame in invader:  # Alternate frames
                    for i in range(16):  # Clear buffer
                        row_buffer[i] = 0x00
                    start_row = 0  # Fixed at topmost row (row 7, 0 bottom)
                    for i, row in enumerate(frame):  # Set invader rows
                        row_idx = start_row + i
                        if row_idx < 8:  # Stay within 8 rows
                            row_buffer[row_idx * 2] = 0x00  # Green off
                            row_buffer[row_idx * 2 + 1] = row  # Red pattern
                    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
                        bus.write_i2c_block_data(addr, 0x00, row_buffer)  # 16-byte write
                    time.sleep(0.3)  # Wiggle speed—adjust as you like (0.2 faster, 0.5 slower)
except KeyboardInterrupt:
    # Clear on Ctrl+C
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("Invasion interrupted - matrices cleared")

# Clear (if not interrupted)
for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
print("Invasion complete - matrices cleared")
