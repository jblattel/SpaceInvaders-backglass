import asyncio
from datetime import datetime

async def io_controller(run_event, operation_counter, io_interval):
    """
    Asynchronous function to control I/O operations
    run_event: Event to signal when to start/stop I/O
    operation_counter: Counter for tracking I/O operations
    io_interval: Interval in seconds between I/O operations
    """
    while True:
        # Wait for the signal to start/stop
        await run_event.wait()
        
        # Perform I/O operation if event is set
        if run_event.is_set():
            operation_counter[0] += 1
            print(f"\nI/O Operation #{operation_counter[0]} at {datetime.now().strftime('%H:%M:%S')}")
            await asyncio.sleep(io_interval)
        else:
            # If event is cleared, wait for it to be set again
            continue

async def display_clock(io_run_event, operation_counter, io_interval, run_duration):
    """
    Asynchronous function to display clock and control I/O duration
    io_run_event: Event to trigger I/O operations
    operation_counter: Counter for tracking I/O operations
    io_interval: Interval in seconds between I/O operations
    run_duration: Total duration in seconds to run I/O operations
    """
    try:
        seconds = 0
        io_running = False
        
        while True:
            try:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\rCurrent Time: {current_time} (IO operations: {operation_counter[0]})", end='', flush=True)
                
                await asyncio.sleep(1)  # Update every second
                seconds += 1
                
                # Start I/O at the beginning
                if seconds == 1 and not io_running:
                    io_run_event.set()
                    io_running = True
                    print(f"\nPOOP: {seconds} ... Starting I/O operations for {run_duration} seconds")
                
                # Stop I/O after run_duration
                if io_running and seconds >= run_duration:
                    io_run_event.clear()
                    io_running = False
                    print(f"\nI/O operations stopped after {run_duration} seconds")
                    
            except Exception as e:
                print(f"\nException in display_clock: {e}")
                print("Continuing clock operation...")
                await asyncio.sleep(1)  # Brief pause before continuing
                
    except asyncio.CancelledError:
        print("\nClock stopped")

async def main(io_interval=5, run_duration=15):
    """
    Main function to run the clock and I/O controller
    io_interval: Interval in seconds between I/O operations (default: 5)
    run_duration: Total duration in seconds to run I/O operations (default: 15)
    """
    # Validate inputs
    if not isinstance(io_interval, int) or io_interval < 1:
        raise ValueError("IO interval must be a positive integer")
    if not isinstance(run_duration, int) or run_duration < 1:
        raise ValueError("Run duration must be a positive integer")
    
    # Create an event to trigger I/O operations
    io_run_event = asyncio.Event()
    
    # Use a list as a mutable counter that can be shared between tasks
    operation_counter = [0]
    
    # Create tasks for both clock and I/O controller
    clock_task = asyncio.create_task(display_clock(io_run_event, operation_counter, io_interval, run_duration))
    io_task = asyncio.create_task(io_controller(io_run_event, operation_counter, io_interval))
    
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
        # You can change the interval and duration here
        asyncio.run(main(io_interval=3, run_duration=10))  # Runs I/O every 3s for 10s
    except KeyboardInterrupt:
        print("\nExiting...")
    except ValueError as e:
        print(f"Error: {e}")
