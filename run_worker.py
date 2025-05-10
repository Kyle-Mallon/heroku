import subprocess
import time
import sys
import logging
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def run_worker():
    while True:
        try:
            logger.info("Starting worker process...")
            # Create a new event loop for each attempt
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the forwarder script
            process = subprocess.Popen([sys.executable, "forwarder.py"])
            process.wait()
            
            logger.info("Worker process exited. Restarting in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error in worker process: {str(e)}")
            time.sleep(5)
        finally:
            # Clean up the event loop
            try:
                loop.close()
            except:
                pass

if __name__ == "__main__":
    run_worker() 