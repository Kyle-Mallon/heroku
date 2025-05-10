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
    
    # Enable tracemalloc for debugging
    tracemalloc.start()

def cleanup_environment() -> None:
    """Clean up resources."""
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
        # Print tracemalloc statistics
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        logger.info("\nTop 10 memory allocations:")
        for stat in top_stats[:10]:
            logger.info(stat)
        sys.exit(1)
    finally:
        cleanup_environment()

if __name__ == "__main__":
    main() 