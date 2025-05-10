import subprocess
import time
import sys
import logging

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
            process = subprocess.Popen([sys.executable, "forwarder.py"])
            process.wait()
            logger.info("Worker process exited. Restarting in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error in worker process: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker() 