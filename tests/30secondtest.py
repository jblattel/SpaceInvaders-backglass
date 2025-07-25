import asyncio
import time
import sys
from datetime import datetime
import board
import busio
import adafruit_mcp230xx.mcp23017 as MCP
from adafruit_mcp230xx.digital_inout import Direction
from adafruit_ht16k33.segments import BigSeg7x4

# Setup MCP23017
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP.MCP23017(i2c, address=0x26)
for pin in range(16):
    mcp.get_pin(pin).direction = Direction.OUTPUT
mcp.gpio = 0xFFFF  # All lights off

# Setup BigSeg7x4
display_upper_right = BigSeg7x4(i2c, address=0x72, auto_write=False)

# Channel definitions
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
ALLOFF = 0xFFFF

async def display_clock(start_event):
    while True:
        try:
            now = datetime.now()
            seconds_until_trigger = 30 - (now.second % 30)
            
            display_upper_right.fill(0)
            display_upper_right.print(f"{seconds_until_trigger:02d}")
            display_upper_right.show()
            
            print(f"Debug: {seconds_until_trigger}s left, event set: {start_event.is_set()}")
            if seconds_until_trigger <= 2:
                print(f"Debug: Close to trigger - value: {seconds_until_trigger}")
            if seconds_until_trigger <= 1 and not start_event.is_set():
                print(f"\nTriggering at {now.strftime('%H:%M:%S')}")
                start_event.set()
            if now.second % 10 == 0:
                print(f"\nForcing trigger at {now.strftime('%H:%M:%S')}")
                start_event.set()
            
            print("Clock ticking")
            await asyncio.sleep(1)
        except IOError as e:
            print(f"\nAn error occurred trying to course correct {e}")
            print(f"\nTrying to continue running..")
        except asyncio.CancelledError:
            print("\nClock stopped")
            raise
        except Exception as e:
            print(f"\nClock exception: {e}")

async def io_controller(start_event, operation_counter):
    print(f"\nTime to do some I/O")
    
    while True:
        try:
            print("Debug: Waiting for event")
            await start_event.wait()
            print("Debug: Event triggered!")
            start_time = time.time()
            end_time = start_time + 60
            operation_counter[0] += 1
            print(f"\nI/O Operation #{operation_counter[0]} at {datetime.now().strftime('%H:%M:%S')}")
            
            for i in range(600):
                remaining_time = max(60 - (i * 0.1), 0)
                frame = i % 4
                if frame == 0:
                    mcp.gpio = channel_14 & channel_10 & channel_8 & channel_12
                elif frame == 1:
                    mcp.gpio = channel_13 & channel_9 & channel_11 & channel_15
                elif frame == 2:
                    mcp.gpio = channel_1 & channel_3 & channel_7 & channel_2
                elif frame == 3:
                    mcp.gpio = channel_4 & channel_0 & channel_6 & channel_5
                sys.stdout.write(f"\r {remaining_time:.1f} seconds remaining...")
                sys.stdout.flush()
                await asyncio.sleep(0.1)
            
            start_event.clear()
            mcp.gpio = ALLOFF
            print(f"\nI/O Operation #{operation_counter[0]} completed")
        except asyncio.CancelledError:
            print("\nI/O controller stopped")
            raise
        except Exception as e:
            print(f"\nIO exception: {e}")
            start_event.clear()

async def main():
    operation_counter = [0]
    io_start_event = asyncio.Event()
    clock_task = asyncio.create_task(display_clock(io_start_event))
    io_task = asyncio.create_task(io_controller(io_start_event, operation_counter))
    try:
        await asyncio.gather(clock_task, io_task)
    except KeyboardInterrupt:
        clock_task.cancel()
        io_task.cancel()
        display_upper_right.fill(0)
        display_upper_right.show()
        mcp.gpio = ALLOFF
        print("\nProgram terminated by the user")

if __name__ == '__main__':
    asyncio.run(main())
