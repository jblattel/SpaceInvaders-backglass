import asyncio
import time
import random
from datetime import datetime
import board
import busio
import adafruit_mcp230xx.mcp23017 as MCP
from adafruit_mcp230xx.digital_inout import Direction
from adafruit_ht16k33.segments import BigSeg7x4
from adafruit_ht16k33 import matrix
import smbus2
import pygame.mixer

# Global settings (24-hour format)
QUIET_START = "22:55"              # Start of quiet period (10:55 PM)
QUIET_END = "07:00"                # End of quiet period (7:00 AM)
SOUND_ENABLED = True               # Toggle sound on/off (True = sound, False = no sound)
ANIMATION_INTERVAL_MINUTES = 60    # Animation interval in minutes (hourly)

# Convert quiet times to minutes
def parse_time_to_minutes(time_input):
    if isinstance(time_input, (int, float)):
        return int(time_input * 60)
    elif isinstance(time_input, str):
        hours, minutes = map(int, time_input.split(":"))
        return hours * 60 + minutes
    raise ValueError("Time must be int/float (hours) or string 'HH:MM'")

QUIET_START_MINUTES = parse_time_to_minutes(QUIET_START)
QUIET_END_MINUTES = parse_time_to_minutes(QUIET_END)

# Initialize pygame mixer
pygame.mixer.init()
pygame.mixer.set_num_channels(3)  # 2 thunder + 1 music

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
mcp2.gpio = 0x0001  # Eyes OFF by default (pin 0 high), others ON (active-low)

# BigSeg7x4 displays
display_upper_left = BigSeg7x4(i2c, address=0x73, auto_write=False)
display_upper_right = BigSeg7x4(i2c, address=0x72, auto_write=False)
display_lower_right = BigSeg7x4(i2c, address=0x70)
display_lower_left = BigSeg7x4(i2c, address=0x71)

# Matrix addresses
MATRIX1_ADDR = 0x76
MATRIX2_ADDR = 0x77

# Initialize 8x8 matrices using Adafruit library
time.sleep(1)  # Wait for I2C bus stability
try:
    matrix1 = matrix.Matrix8x8(i2c, address=MATRIX1_ADDR)
    matrix2 = matrix.Matrix8x8(i2c, address=MATRIX2_ADDR)
    matrix1.fill(0)
    matrix2.fill(0)
    matrix1.brightness = 0.5
    matrix2.brightness = 0.5
    matrix1.show()
    matrix2.show()
except Exception as e:
    print(f"Matrix initialization error: {e}")

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

# Sound paths
SOUND_DIR = "/home/pi/pycode/Space-Invaders-Clock/sounds/"
THUNDER_SOUNDS = [SOUND_DIR + "thunder1.wav", SOUND_DIR + "thunder2.wav", SOUND_DIR + "thunder3.wav"]
MUSIC_SOUND = SOUND_DIR + "invasion_music.wav"

async def flicker_lights(seconds_until_hour):
    start_time = time.time()
    max_channels = int(2 + (90 - seconds_until_hour) * (14 / 90))
    active_channels = random.sample(range(16), max_channels)

    while time.time() < start_time + 1:
        pattern = 0
        for ch in active_channels:
            if random.random() < 0.5:
                pattern |= (1 << ch)
        mcp1.gpio = ~pattern
        await asyncio.sleep(random.uniform(0.02, 0.05))
    mcp1.gpio = ALLOFF

def is_active_hour(hour, minutes=0, seconds=0):
    total_minutes = hour * 60 + minutes
    quiet_start_minutes = QUIET_START_MINUTES
    quiet_end_minutes = QUIET_END_MINUTES

    if quiet_start_minutes < quiet_end_minutes:
        return not (quiet_start_minutes <= total_minutes < quiet_end_minutes)
    else:
        return not (total_minutes >= quiet_start_minutes or total_minutes < quiet_end_minutes)

async def display_clock(start_event):
    thunder_channel = pygame.mixer.Channel(0)
    thunder_channel2 = pygame.mixer.Channel(1)
    music_channel = pygame.mixer.Channel(2)
    colon_state = True

    while True:
        try:
            now = datetime.now()
            hour = now.hour
            minutes = now.minute
            seconds = now.second
            seconds_until_hour = 3600 - (minutes * 60 + seconds)
            if seconds_until_hour < 0:
                seconds_until_hour = 0  # Clamp to 0 at hour mark
            countdown_to_interval = seconds_until_hour

            # Upper-left: Current time with blinking colon
            display_upper_left.fill(0)
            if colon_state:
                display_upper_left.print(now.strftime("%H:%M"))
            else:
                display_upper_left.print(f"{hour:02d}{minutes:02d}")
            display_upper_left.show()

            # Upper-right: Countdown to next animation
            display_upper_right.fill(0)
            display_upper_right.print(f"{countdown_to_interval:04d}")
            display_upper_right.show()

            # Other displays
            display_lower_right.print(now.strftime("%Y"))
            display_lower_left.print(now.strftime("%m%d"))

            # Enforce quiet time - all lights off
            if not is_active_hour(hour, minutes, seconds):
                mcp1.gpio = ALLOFF
                mcp2.gpio = ALLOFF

            # Thunder/flicker 90s before hour
            if (is_active_hour(hour, minutes, seconds) and
                seconds_until_hour <= 90 and
                not music_channel.get_busy()):
                thunder_chance = 0.05 + (90 - seconds_until_hour) * (0.20 / 90)
                if random.random() < thunder_chance:
                    if SOUND_ENABLED:
                        thunder_sound = pygame.mixer.Sound(random.choice(THUNDER_SOUNDS))
                        if not thunder_channel.get_busy():
                            thunder_channel.play(thunder_sound)
                            await flicker_lights(seconds_until_hour)
                        elif not thunder_channel2.get_busy():
                            thunder_channel2.play(thunder_sound)
                            await flicker_lights(seconds_until_hour)
                        else:
                            await asyncio.sleep(0.2)
                    else:
                        await flicker_lights(seconds_until_hour)

            # Trigger animation at hour
            if (is_active_hour(hour, minutes, seconds) and
                seconds_until_hour <= 2 and
                not start_event.is_set()):
                print(f"Trigger at {now.strftime('%H:%M:%S')} - Setting start_event")
                start_event.set()

            await asyncio.sleep(1)
            colon_state = not colon_state
        except Exception as e:
            print(f"Clock exception: {e}")

async def io_controller(start_event, operation_counter):
    while True:
        try:
            await start_event.wait()
            now = datetime.now()
            hour = now.hour
            minutes = now.minute
            seconds = now.second
            print(f"IO triggered at {now.strftime('%H:%M:%S')}")
            if is_active_hour(hour, minutes, seconds):
                operation_counter[0] += 1
                for i in range(840):
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
                mcp1.gpio = ALLOFF
            start_event.clear()
        except Exception as e:
            print(f"IO exception: {e}")
            start_event.clear()

async def matrix_controller(start_event):
    invader_one = [
        [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x5A, 0x42],
        [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x5A, 0xA5]
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
        [0x3c, 0x7e, 0x33, 0x7e, 0x3c, 0x00, 0x08, 0x00],
        [0x3c, 0x7e, 0x99, 0x7e, 0x3c, 0x00, 0x08, 0x08],
        [0x3c, 0x7e, 0xcc, 0x7e, 0x3c, 0x00, 0x00, 0x08],
        [0x3c, 0x7e, 0x66, 0x7e, 0x3c, 0x00, 0x00, 0x00]
    ]
    all_invaders = [invader_one, invader_two, invader_three, invader_four]

    row_buffer1 = bytearray([0x00] * 16)
    row_buffer2 = bytearray([0x00] * 16)
    music_channel = pygame.mixer.Channel(2)

    while True:
        try:
            await start_event.wait()
            now = datetime.now()
            hour = now.hour
            minutes = now.minute
            seconds = now.second
            print(f"Matrix triggered at {now.strftime('%H:%M:%S')}")
            if is_active_hour(hour, minutes, seconds):
                start_time = time.time()
                end_time = start_time + 42
                mcp2.gpio = 0x0000  # All pins low (eyes on)
                if SOUND_ENABLED:
                    music_sound = pygame.mixer.Sound(MUSIC_SOUND)
                    music_channel.play(music_sound)
                chosen_invader1 = random.choice(all_invaders)
                chosen_invader2 = random.choice(all_invaders)
                while time.time() < end_time:
                    for frame_idx, (frame1, frame2) in enumerate(zip(chosen_invader1, chosen_invader2)):
                        for i in range(16):
                            row_buffer1[i] = 0x00
                        start_row = 0
                        for i, row in enumerate(frame1):
                            row_idx = start_row + i
                            if row_idx < 8:
                                row_buffer1[row_idx * 2 + 1] = row
                        bus.write_i2c_block_data(MATRIX1_ADDR, 0x00, row_buffer1)
                        for i in range(16):
                            row_buffer2[i] = 0x00
                        for i, row in enumerate(frame2):
                            row_idx = start_row + i
                            if row_idx < 8:
                                row_buffer2[row_idx * 2] = row
                        bus.write_i2c_block_data(MATRIX2_ADDR, 0x00, row_buffer2)
                        await asyncio.sleep(0.3)
                if SOUND_ENABLED:
                    music_channel.stop()
                mcp2.gpio = 0x0001  # Pin 0 high (off), others low (on)
            start_event.clear()
            mcp1.gpio = ALLOFF
            for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
                bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)
        except Exception as e:
            print(f"Matrix exception: {e}")
            start_event.clear()

async def main():
    operation_counter = [0]
    io_start_event = asyncio.Event()
    clock_task = asyncio.create_task(display_clock(io_start_event))
    io_task = asyncio.create_task(io_controller(io_start_event, operation_counter))
    matrix_task = asyncio.create_task(matrix_controller(io_start_event))
    try:
        await asyncio.gather(clock_task, io_task, matrix_task)
    except KeyboardInterrupt:
        clock_task.cancel()
        io_task.cancel()
        matrix_task.cancel()
        display_upper_right.fill(0)
        display_upper_right.show()
        display_upper_left.fill(0)
        display_lower_right.fill(0)
        display_lower_left.fill(0)
        mcp1.gpio = mcp2.gpio = ALLOFF
        for addr in [MATRIX1_ADDR, MATRIX2_ADDR]:
            bus.write_i2c_block_data(addr, 0x00, [0x00] * 16)

if __name__ == '__main__':
    asyncio.run(main())