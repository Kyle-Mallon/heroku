import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..utils.config import config, save_config

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and forward them if conditions are met."""
    try:
        # Check if bot was mentioned in the message
        bot_mentioned = False
        
        # Check message entities for mentions
        if update.message and update.message.entities:
            for entity in update.message.entities:
                if entity.type == 'mention' and entity.user and entity.user.id == context.bot.id:
                    bot_mentioned = True
                    break
        
        # Check message text for bot username
        if not bot_mentioned and update.message and update.message.text:
            bot_username = context.bot.username
            if bot_username and f"@{bot_username}" in update.message.text:
                bot_mentioned = True
        
        if bot_mentioned:
            # Bot was mentioned, set this chat as destination
            chat = update.effective_chat
            if chat.type in ['channel', 'supergroup', 'group']:
                config['destination_channel'] = chat.id
                save_config(config)
                await update.message.reply_text(
                    f"✅ This {chat.type} has been set as the destination channel!\n\n"
                    "Now you can set a source channel using:\n"
                    "• /setsource @channelname\n"
                    "• /setsource t.me/channelname\n"
                    "• /setsource -1001234567890"
                )
                return

        # Handle message forwarding
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
        logger.error(f"Error handling message: {str(e)}")
        # Try to notify the user about the error
        try:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n"
                "Please check if the bot has proper permissions in both channels."
            )
        except Exception as notify_error:
            logger.error(f"Error notifying user: {str(notify_error)}") 