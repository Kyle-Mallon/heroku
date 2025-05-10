"""
Worker script for running the Telegram bot.
Handles bot process management and error handling.
"""

import os
import sys
import logging
import tracemalloc
from pathlib import Path
from telegram_forwarder import main

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """Set up the working environment."""
    # Ensure we're in the correct directory
    os.chdir(Path(__file__).parent)
    
    # Start tracemalloc with a limit of 25 frames
    tracemalloc.start(25)

def cleanup_environment() -> None:
    """Clean up resources."""
    if tracemalloc.is_tracing():
        tracemalloc.stop()

def main() -> None:
    """Main entry point for the worker."""
    try:
        setup_environment()
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Bot stopped due to error: {str(e)}")
        # Only take snapshot if tracemalloc is tracing
        if tracemalloc.is_tracing():
            try:
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')
                logger.info("\nTop 10 memory allocations:")
                for stat in top_stats[:10]:
                    logger.info(stat)
            except Exception as snapshot_error:
                logger.error(f"Error taking memory snapshot: {str(snapshot_error)}")
        sys.exit(1)
    finally:
        cleanup_environment()

if __name__ == "__main__":
    main() 