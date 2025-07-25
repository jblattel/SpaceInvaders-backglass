import asyncio
import time
from datetime import datetime

async def io_control(device_name: str, interval: float = 1.0):
    """Asynchronous function to simulate I/O control"""
    try:
        while True:
            # Simulate I/O operation
            print(f"{datetime.now()}: Performing I/O operation on {device_name}")
            # Simulate some async work (replace with your actual I/O code)
            await asyncio.sleep(0.5)  # Simulate I/O delay
            print(f"{datetime.now()}: I/O operation completed on {device_name}")
            await asyncio.sleep(interval)  # Wait between operations
    except asyncio.CancelledError:
        print(f"{datetime.now()}: I/O control for {device_name} cancelled")
        raise
    except Exception as e:
        print(f"{datetime.now()}: Error in I/O control: {e}")

async def main():
    """Main program that runs continuously and keeps time"""
    # Start the I/O control as a background task
    io_task = asyncio.create_task(io_control("Device1", interval=2.0))
    
    start_time = time.time()
    try:
        while True:
            # Main program loop continues running
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Print current time and elapsed time
            print(f"{datetime.now()}: Main program running - Elapsed time: {elapsed_time:.2f} seconds")
            
            # Do other main program tasks here
            
            # Wait a bit before next iteration
            await asyncio.sleep(1.0)
            
    except KeyboardInterrupt:
        # Handle program termination
        print("\nShutting down...")
        io_task.cancel()
        await io_task  # Wait for I/O task to cleanly shut down

# Run the program
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user")
