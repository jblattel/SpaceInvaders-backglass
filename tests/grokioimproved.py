import asyncio
from datetime import datetime

async def io_controller(run_event, operation_counter):
    """
    Asynchronous function to control I/O operations
    run_event: Event to signal when to perform I/O
    operation_counter: Counter for tracking I/O operations
    """
    while True:
        # Wait for the signal to perform I/O
        await run_event.wait()
        
        # Perform I/O operation when event is set
        operation_counter[0] += 1
        print(f"\nI/O Operation #{operation_counter[0]} at {datetime.now().strftime('%H:%M:%S')}")
        
        # Clear the event after operation and wait for next signal
        run_event.clear()

async def display_clock(io_run_event, operation_counter):
    """
    Asynchronous function to display clock and control I/O timing
    io_run_event: Event to trigger I/O operations
    operation_counter: Counter for tracking I/O operations
    """
    try:
        seconds = 0
        while True:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\rCurrent Time: {current_time} (IO operations: {operation_counter[0]})", end='', flush=True)
            
            await asyncio.sleep(1)  # Update every second
            seconds += 1
            
            # Trigger I/O every 5 seconds (configurable)
            if seconds % 5 == 0:
                io_run_event.set()
                
    except asyncio.CancelledError:
        print("\nClock stopped")

async def main():
    # Create an event to trigger I/O operations
    io_run_event = asyncio.Event()
    
    # Use a list as a mutable counter that can be shared between tasks
    operation_counter = [0]
    
    # Create tasks for both clock and I/O controller
    clock_task = asyncio.create_task(display_clock(io_run_event, operation_counter))
    io_task = asyncio.create_task(io_controller(io_run_event, operation_counter))
    
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
