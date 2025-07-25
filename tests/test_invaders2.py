import time
import random
import board
import busio
import smbus2

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
bus = smbus2.SMBus(1)

# Matrix addresses
MATRIX1_ADDR = 0x76  # Left 8x8 (Red + Green)
MATRIX2_ADDR = 0x77  # Right 8x8 (Red + Green)

# Clear 8x8 matrices
for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)

# Defender game (16x8 playfield)
defender_ship = 0b00011000  # Red ship: ...XX...
defender_enemy = 0b00100100  # Green enemy: ..X..X..
defender_shot = 0b00001000  # Yellow shot: ....X...

# Rocket animation (both 8x8s, 3 frames)
rocket = [
    # Frame 1: Rocket low
    [0b00000000,  # Red body
     0b00011000,
     0b00011000,
     0b00111100,
     0b00111100,
     0b01111110,
     0b01111110,
     0b00000000],
    [0b00000000,  # Green flame + Yellow sparks
     0b00000000,
     0b00000000,
     0b00000000,
     0b00000000,
     0b00011000,
     0b00100100,
     0b00011000],
    # Frame 2: Rocket mid
    [0b00011000,  # Red body
     0b00011000,
     0b00111100,
     0b00111100,
     0b01111110,
     0b01111110,
     0b00000000,
     0b00000000],
    [0b00000000,  # Green flame + Yellow sparks
     0b00000000,
     0b00000000,
     0b00000000,
     0b00011000,
     0b00100100,
     0b00011000,
     0b00100100],
    # Frame 3: Rocket high
    [0b00111100,  # Red body
     0b00111100,
     0b01111110,
     0b01111110,
     0b00000000,
     0b00000000,
     0b00000000,
     0b00000000],
    [0b00000000,  # Green flame + Yellow sparks
     0b00011000,
     0b00100100,
     0b00011000,
     0b00100100,
     0b00011000,
     0b00000000,
     0b00000000]
]

row_buffer1 = bytearray([0x00] * 16)  # MATRIX1 (left 8x8)
row_buffer2 = bytearray([0x00] * 16)  # MATRIX2 (right 8x8)

def run_defender():
    print("Testing Defender game (16x8)")
    ship_x = 4  # Start ship mid-left (0-15 across 16x8)
    enemies = [(15, random.randint(2, 6)), (12, random.randint(2, 6))]  # Two enemies: (x, y)
    shot_x, shot_y = -1, -1  # Shot starts off-screen
    
    for _ in range(50):  # ~15s test (50 * 0.3s)
        # Clear buffers
        for i in range(16):
            row_buffer1[i] = row_buffer2[i] = 0x00
        
        # Ship (red) - MATRIX1 or MATRIX2 based on x
        ship_y = 1  # Fixed low row
        if ship_x < 8:
            row_buffer1[ship_y * 2 + 1] = defender_ship >> (ship_x % 8)
        else:
            row_buffer2[ship_y * 2 + 1] = defender_ship >> ((ship_x - 8) % 8)
        
        # Enemies (green) - Scroll left
        for i, (ex, ey) in enumerate(enemies):
            if ex < 8:
                row_buffer1[ey * 2] |= defender_enemy >> (ex % 8)
            else:
                row_buffer2[ey * 2] |= defender_enemy >> ((ex - 8) % 8)
            enemies[i] = (ex - 1, ey)  # Move left
            if enemies[i][0] < 0:  # Respawn
                enemies[i] = (15, random.randint(2, 6))
        
        # Shot (yellow) - Move right
        if shot_x >= 0 and shot_y >= 0:
            if shot_x < 8:
                row_buffer1[shot_y * 2] |= defender_shot >> (shot_x % 8)
                row_buffer1[shot_y * 2 + 1] |= defender_shot >> (shot_x % 8)  # Yellow
            else:
                row_buffer2[shot_y * 2] |= defender_shot >> ((shot_x - 8) % 8)
                row_buffer2[shot_y * 2 + 1] |= defender_shot >> ((shot_x - 8) % 8)
            shot_x += 1
            if shot_x > 15:  # Reset shot
                shot_x, shot_y = -1, -1
        
        # Random shot trigger
        if shot_x < 0 and random.random() < 0.2:
            shot_x, shot_y = ship_x + 1, ship_y
        
        # Move ship (random for test)
        ship_x = max(0, min(15, ship_x + random.choice([-1, 0, 1])))
        
        # Write to matrices
        bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
        bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
        time.sleep(0.3)

def run_rocket():
    print("Testing Rocket blast-off")
    for _ in range(5):  # ~5 cycles (~4s each)
        for i in range(0, len(rocket), 2):
            red_frame = rocket[i]
            green_frame = rocket[i + 1]
            
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

try:
    print("Starting Defender test...")
    run_defender()
    time.sleep(2)  # Break between tests
    print("Starting Rocket test...")
    run_rocket()

except KeyboardInterrupt:
    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
        bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
    print("\nTest terminated by user")
