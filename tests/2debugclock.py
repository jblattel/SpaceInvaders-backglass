import asyncio
import time
import random
from datetime import datetime
import board
import busio
import adafruit_mcp230xx.mcp23017 as MCP
from adafruit_mcp230xx.digital_inout import Direction
from adafruit_ht16k33.segments import BigSeg7x4
import smbus2

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
bus = smbus2.SMBus(1)

# MCP23017 #1 (Perimeter)
mcp1 = MCP.MCP23017(i2c, address=0x26)
for pin in range(16):
    mcp1.get_pin(pin).direction = Direction.OUTPUT
mcp1.gpio = 0xFFFF

# MCP23017 #2 (Alien)
mcp2 = MCP.MCP23017(i2c, address=0x25)
for pin in range(16):
    mcp2.get_pin(pin).direction = Direction.OUTPUT
mcp2.gpio = 0xFFFF

# BigSeg7x4
display_upper_right = BigSeg7x4(i2c, address=0x72, auto_write=False)

# Matrix addresses
MATRIX1_ADDR = 0x76
MATRIX2_ADDR = 0x77

# Clear 8x8 matrices
for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
    bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)

# MCP1 Channels (Perimeter)
channel_0 = 0xFFFE
channel_1 = 0xFFFD
channel_2 = 0xFFFB
channel_3 = 0xFFF7
channel_4 = 0xFFEF
channel_5 = 0xFFDF
channel_6 = 0xFFBF
channel_7 = 0xFF7F
channel_8 = 0xFEFF
channel_9 = 0xFDFF
channel_10 = 0xFBFF
channel_11 = 0xF7FF
channel_12 = 0xEFFF
channel_13 = 0xDFFF
channel_14 = 0xBFFF
channel_15 = 0x7FFF

# MCP2 Channels (Alien)
alien_eyes = 0xFFFE
alien_game_over = 0xFFFD
alien_high_score = 0xFFFB
alien_shoot_again = 0xFFF7
alien_ball_in_play = 0xFFEF
alien_main_title = 0xFFDF
alien_tilt = 0xFFBF
alien_match = 0xFF7F
alien_not_connected = 0xFEFF
alien_right_shoulder = 0xFDFF
alien_left_hip = 0xFBFF
alien_head = 0xF7FF
alien_left_hand = 0xEFFF
alien_right_hand = 0xDFFF
alien_right_hip = 0xBFFF
alien_left_shoulder = 0x7FFF
ALLOFF = 0xFFFF

async def display_clock(start_event):
    while True:
        try:
            now = datetime.now()
            seconds_until_trigger = 30 - (now.second % 30)  # Trigger every 30s
            
            display_upper_right.fill(0)
            display_upper_right.print(f"{seconds_until_trigger:04d}")
            display_upper_right.show()
            
            if seconds_until_trigger <= 1 and not start_event.is_set():
                print(f"\nTrigger at {now.strftime('%H:%M:%S')}")
                start_event.set()
            
            await asyncio.sleep(1)
        except Exception as e:
            print(f"\nClock exception: {e}")

async def io_controller(start_event, operation_counter):
    print(f"\nTime to do some I/O")
    while True:
        try:
            await start_event.wait()
            print(f"\nI/O Operation #{operation_counter[0]} at {datetime.now().strftime('%H:%M:%S')}")
            operation_counter[0] += 1
            
            for i in range(1200):  # 60s @ 0.05s = 1200 frames
                frame = i % 4
                if frame == 0:
                    mcp1.gpio = channel_14 & channel_10 & channel_8 & channel_12
                elif frame == 1:
                    mcp1.gpio = channel_13 & channel_9 & channel_11 & channel_15
                elif frame == 2:
                    mcp1.gpio = channel_1 & channel_3 & channel_7 & channel_2
                elif frame == 3:
                    mcp1.gpio = channel_4 & channel_0 & channel_6 & channel_5
                await asyncio.sleep(0.05)
            
            start_event.clear()
            mcp1.gpio = ALLOFF
            print(f"I/O Operation #{operation_counter[0]} completed")
        except Exception as e:
            print(f"\nIO exception: {e}")
            start_event.clear()

async def matrix_controller(start_event):
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
    row_buffer = bytearray([0x00] * 16)

    while True:
        try:
            print("Debug: Matrix waiting for start event")
            await start_event.wait()
            print(f"Debug: Matrix running 30s invasion begins at {datetime.now().strftime('%H:%M:%S')}")
            start_time = time.time()
            end_time = start_time + 60  # 60s invasion
            
            # Randomly choose one invader for the trigger
            chosen_invader = random.choice(all_invaders)
            print(f"Debug: Chose invader with frames: {len(chosen_invader)}")
            
            while time.time() < end_time:
                for frame in chosen_invader:  # Alternate frames
                    for i in range(16):  # Clear buffer
                        row_buffer[i] = 0x00
                    start_row = 0  # Top row (row 7, 0 bottom)
                    for i, row in enumerate(frame):
                        row_idx = start_row + i
                        if row_idx < 8:
                            row_buffer[row_idx * 2] = 0x00  # Green off
                            row_buffer[row_idx * 2 + 1] = row  # Red pattern
                    for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
                        try:
                            bus.write_i2c_block_data(addr, 0x00, row_buffer)
                            print(f"Debug: Wrote to matrix {hex(addr)}")
                        except Exception as write_e:
                            print(f"Debug: Matrix write failed to {hex(addr)}: {write_e}")
                    await asyncio.sleep(0.3)  # Wiggle speed—~100 toggles in 60s
            
            # Clear matrices
            for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
                bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
            start_event.clear()
            print(f"Debug: Matrix invasion complete at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"\nMatrix exception: {e}")
            start_event.clear()

async def alien_lights():
    eye_state = False
    while True:
        now = datetime.now()
        hour = now.hour
        if 7 <= hour < 23:
            base = 0x0000
            eye_state = not eye_state
            mcp2.gpio = base if eye_state else (base | 0x0001)  # Eyes blink
        else:
            mcp2.gpio = ALLOFF  # All off outside 7-23
        await asyncio.sleep(1)

async def main():
    operation_counter = [0]
    io_start_event = asyncio.Event()
    clock_task = asyncio.create_task(display_clock(io_start_event))
    io_task = asyncio.create_task(io_controller(io_start_event, operation_counter))
    matrix_task = asyncio.create_task(matrix_controller(io_start_event))
    alien_task = asyncio.create_task(alien_lights())
    try:
        await asyncio.gather(clock_task, io_task, matrix_task, alien_task)
    except KeyboardInterrupt:
        clock_task.cancel()
        io_task.cancel()
        matrix_task.cancel()
        alien_task.cancel()
        display_upper_right.fill(0)
        display_upper_right.show()
        mcp1.gpio = mcp2.gpio = ALLOFF
        for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
            bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
        print("\nProgram terminated by user")

if __name__ == '__main__':
    asyncio.run(main())
