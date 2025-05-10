import logging
import os
import asyncio
import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TimedOut, NetworkError
from dotenv import load_dotenv
from .handlers.commands import start, help_command, set_source, set_dest, status
from .handlers.callbacks import button_handler
from .handlers.messages import handle_message

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_application() -> Application:
    """Create and configure the bot application."""
    # Load environment variables
    load_dotenv()
    
    # Get bot token from environment
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("No BOT_TOKEN found in environment variables")

    # Create application with custom request settings
    application = (
        Application.builder()
        .token(token)
        .connect_timeout(30.0)  # Increase connection timeout
        .read_timeout(30.0)     # Increase read timeout
        .write_timeout(30.0)    # Increase write timeout
        .pool_timeout(30.0)     # Increase pool timeout
        .build()
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setsource", set_source))
    application.add_handler(CommandHandler("setdest", set_dest))
    application.add_handler(CommandHandler("status", status))

    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))

    # Add message handler
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    return application

async def run_bot_with_retry() -> None:
    """Run the bot with retry logic."""
    application = None
    stop_event = asyncio.Event()
    
    def signal_handler():
        logger.info("Received shutdown signal")
        stop_event.set()
    
    # Set up signal handlers
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    
    while not stop_event.is_set():
        try:
            # Create application
            application = create_application()
            
            # Start the bot
            logger.info("Starting bot...")
            await application.initialize()
            await application.start()
            
            # Run polling
            await application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False
            )
            
        except (TimedOut, NetworkError) as e:
            logger.error(f"Network error occurred: {str(e)}")
            if not stop_event.is_set():
                logger.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            if not stop_event.is_set():
                logger.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)
        finally:
            if application:
                try:
                    await application.stop()
                except Exception as e:
                    logger.error(f"Error stopping application: {str(e)}")

def run_bot() -> None:
    """Run the bot."""
    try:
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the bot
        loop.run_until_complete(run_bot_with_retry())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {str(e)}")
        raise
    finally:
        try:
            loop.close()
        except Exception as e:
            logger.error(f"Error closing event loop: {str(e)}") 