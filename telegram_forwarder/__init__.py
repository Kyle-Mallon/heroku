import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
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

    # Create application
    application = Application.builder().token(token).build()

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

def run_bot() -> None:
    """Run the bot."""
    try:
        # Create application
        application = create_application()

        # Start the bot
        logger.info("Starting bot...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        raise 