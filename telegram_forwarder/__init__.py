"""
Telegram Bot for forwarding messages between channels.
Handles bot initialization, command registration, and message processing.
"""

import logging
import os
import asyncio
import signal
import nest_asyncio
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.error import TimedOut, NetworkError
from dotenv import load_dotenv

from .handlers.commands import (
    start,
    help_command,
    set_source,
    set_dest,
    status
)
from .handlers.callbacks import button_handler
from .handlers.messages import handle_message

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Enable nested event loops
nest_asyncio.apply()

def get_bot_token() -> str:
    """Get the bot token from environment variables."""
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("No BOT_TOKEN found in environment variables")
    return token

def create_application() -> Application:
    """Create and configure the bot application with all handlers."""
    # Create application with optimized settings
    application = (
        Application.builder()
        .token(get_bot_token())
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )

    # Register command handlers
    command_handlers = {
        "start": start,
        "help": help_command,
        "setsource": set_source,
        "setdest": set_dest,
        "status": status
    }
    for command, handler in command_handlers.items():
        application.add_handler(CommandHandler(command, handler))

    # Register other handlers
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    return application

async def run_bot() -> None:
    """Run the bot with proper error handling and signal management."""
    application: Optional[Application] = None
    stop_event = asyncio.Event()

    def handle_shutdown() -> None:
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal")
        stop_event.set()

    try:
        # Initialize application
        application = create_application()
        logger.info("Starting bot...")
        
        # Start the bot
        await application.initialize()
        await application.start()

        # Set up signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, handle_shutdown)

        # Run polling
        await application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )

    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        raise
    finally:
        if application:
            try:
                await application.stop()
            except Exception as e:
                logger.error(f"Error stopping application: {str(e)}")

def main() -> None:
    """Main entry point for the bot."""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {str(e)}")
        raise 