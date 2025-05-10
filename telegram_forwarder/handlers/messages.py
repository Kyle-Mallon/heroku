import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.config import config

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and forward them if conditions are met."""
    try:
        # Check if message is from source channel
        if update.effective_chat.id != config.get('source_channel'):
            return

        # Check if destination channel is set
        if not config.get('destination_channel'):
            logger.warning("No destination channel set")
            return

        # Forward the message
        await context.bot.copy_message(
            chat_id=config['destination_channel'],
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
        logger.info(f"Message {update.message.message_id} forwarded successfully")
    except Exception as e:
        logger.error(f"Error forwarding message: {str(e)}")
        # Try to notify the user about the error
        try:
            await update.message.reply_text(
                f"❌ Error forwarding message: {str(e)}\n"
                "Please check if the bot has proper permissions in both channels."
            )
        except Exception as notify_error:
            logger.error(f"Error notifying user: {str(notify_error)}") 