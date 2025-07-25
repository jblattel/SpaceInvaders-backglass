import asyncio
import time
from datetime import datetime

async def io_controller(stop_event, interval=2):
    """
    Asynchronous function to control I/O operations
    stop_event: Event to signal when to pause/resume I/O
    interval: Time between I/O operations in seconds
    """
    io_running = True
    io_count = 0
    
    while True:
        if stop_event.is_set():
            if io_running:
                print("\nPausing I/O operations...")
                io_running = False
            await asyncio.sleep(0.5)  # Check frequently when paused
            continue
            
        if not io_running:
            print("\nResuming I/O operations...")
            io_running = True
            
        # Simulate some I/O operation
        io_count += 1
        print(f"\nI/O Operation #{io_count} at {datetime.now().strftime('%H:%M:%S')}")
        
        # Wait for specified interval or until stopped
        await asyncio.sleep(interval)

async def display_clock(stop_event):
    """
    Asynchronous function to display continuously running clock
    stop_event: Event to control I/O operations
    """
    try:
        while True:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\rCurrent Time: {current_time}", end='', flush=True)
            
            # Check for user input every 0.1 seconds
            await asyncio.sleep(0.1)
            
            # Here you could add more sophisticated input checking
            # For simplicity, we'll use a timed toggle every 10 seconds
            if int(time.time()) % 20 < 10:
                stop_event.set()
            else:
                stop_event.clear()
                
    except asyncio.CancelledError:
        print("\nClock stopped")

async def main():
    # Create an event to control I/O operations
    io_stop_event = asyncio.Event()
    
    # Create tasks for both clock and I/O controller
    clock_task = asyncio.create_task(display_clock(io_stop_event))
    io_task = asyncio.create_task(io_controller(io_stop_event))
    
    try:
        # Run both tasks concurrently
        await asyncio.gather(clock_task, io_task)
    except KeyboardInterrupt:
        # Clean up on Ctrl+C
        clock_task.cancel()
        io_task.cancel()
        print("\nProgram terminated by user")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
