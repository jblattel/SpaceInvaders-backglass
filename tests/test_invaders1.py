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

# Hypnotized eye animations (8x8, 3 frames)
hypno_eye = [
    # Frame 1: Wide red iris, green pupil, yellow flecks
    [0b00111100,  # Red iris
     0b01000010,
     0b10011001,
     0b10100101,
     0b10100101,
     0b10011001,
     0b01000010,
     0b00111100],
    [0b00000000,  # Green pupil + Yellow flecks
     0b00000000,
     0b00011000,
     0b00100100,
     0b00100100,
     0b00011000,
     0b00000000,
     0b00000000],
    # Frame 2: Iris shrinks, pupil grows
    [0b00000000,  # Red iris
     0b00111100,
     0b01000010,
     0b01011010,
     0b01011010,
     0b01000010,
     0b00111100,
     0b00000000],
    [0b00000000,  # Green pupil + Yellow flecks
     0b00000000,
     0b00100100,
     0b00111100,
     0b00111100,
     0b00100100,
     0b00000000,
     0b00000000],
    # Frame 3: Pupil shrinks, iris expands
    [0b00111100,  # Red iris
     0b01000010,
     0b10100101,
     0b10011001,
     0b10011001,
     0b10100101,
     0b01000010,
     0b00111100],
    [0b00000000,  # Green pupil + Yellow flecks
     0b00000000,
     0b00011000,
     0b00100100,
     0b00100100,
     0b00011000,
     0b00000000,
     0b00000000]
]

row_buffer1 = bytearray([0x00] * 16)  # MATRIX1 (red + green)
row_buffer2 = bytearray([0x00] * 16)  # MATRIX2 (red + green)

try:
    while True:
        print("Testing hypnotized eyes")
        
        # Cycle through frames (3 frames, 2 rows each: red, green)
        for i in range(0, len(hypno_eye), 2):
            red_frame = hypno_eye[i]
            green_frame = hypno_eye[i + 1]
            
            # MATRIX1 - Red + Green (Yellow where overlapped)
            for j in range(16):
                row_buffer1[j] = 0x00
            for j, (r, g) in enumerate(zip(red_frame, green_frame)):
                if j < 8:
                    row_buffer1[j * 2] = g    # Green
                    row_buffer1[j * 2 + 1] = r  # Red
            bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
            
            # MATRIX2 - Red + Green (Yellow where overlapped)
            for j in range(16):
                row_buffer2[j] = 0x00
            for j, (r, g) in enumerate(zip(red_frame, green_frame)):
                if j < 8:
                    row_buffer2[j * 2] = g    # Green
                    row_buffer2[j * 2 + 1] = r  # Red
            bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
            
            time.sleep(0.3)  # Frame speed ~0.3s
        
        time.sleep(1)  # Pause between cycles

except KeyboardInterrupt:
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("\nTest terminated by user")
