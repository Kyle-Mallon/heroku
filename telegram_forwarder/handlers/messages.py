"""
Message handler for the Telegram bot.
Handles message processing, bot mentions, and message forwarding.
"""

import logging
from typing import Optional, List
from telegram import Update, Message, User
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from ..utils.config import config, save_config

logger = logging.getLogger(__name__)

def is_bot_mentioned(message: Message, bot: User) -> bool:
    """
    Check if the bot was mentioned in the message.
    
    Args:
        message: The message to check
        bot: The bot user object
        
    Returns:
        bool: True if bot was mentioned, False otherwise
    """
    if not message or not message.entities:
        return False
        
    for entity in message.entities:
        # Check for direct user mention
        if entity.type == 'text_mention' and entity.user and entity.user.id == bot.id:
            return True
            
        # Check for username mention
        if entity.type == 'mention' and message.text and bot.username:
            mention = message.text[entity.offset:entity.offset + entity.length]
            if mention == f"@{bot.username}":
                return True
                
    return False

async def handle_destination_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handle setting the destination channel when bot is mentioned.
    
    Args:
        update: The update object
        context: The context object
        
    Returns:
        bool: True if destination was set, False otherwise
    """
    chat = update.effective_chat
    if not chat or chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP]:
        return False
        
    config['destination_channel'] = chat.id
    save_config(config)
    
    await update.message.reply_text(
        f"✅ This {chat.type} has been set as the destination channel!\n\n"
        "Now you can set a source channel using:\n"
        "• /setsource @channelname\n"
        "• /setsource t.me/channelname\n"
        "• /setsource -1001234567890"
    )
    return True

def has_media(message: Message) -> bool:
    """
    Check if the message contains media.
    
    Args:
        message: The message to check
        
    Returns:
        bool: True if message contains media, False otherwise
    """
    return bool(
        message.photo or 
        message.video or 
        message.document or 
        message.audio
    )

async def forward_message(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Forward a message to the destination channel.
    
    Args:
        message: The message to forward
        context: The context object
    """
    try:
        await context.bot.copy_message(
            chat_id=config['destination_channel'],
            from_chat_id=message.chat_id,
            message_id=message.message_id
        )
        logger.info(f"Message {message.message_id} forwarded successfully")
    except Exception as e:
        logger.error(f"Error forwarding message: {str(e)}")
        raise

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages and forward them if conditions are met.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        # Handle bot mention
        if update.message and is_bot_mentioned(update.message, context.bot):
            if await handle_destination_setting(update, context):
                return

        # Check if message is from source channel
        if update.effective_chat.id != config.get('source_channel'):
            return

        # Verify destination channel is set
        if not config.get('destination_channel'):
            logger.warning("No destination channel set")
            return

        # Forward media messages
        if update.message and has_media(update.message):
            await forward_message(update.message, context)
        else:
            logger.info(f"Message {update.message.message_id} skipped (no media)")
            
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        try:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n"
                "Please check if the bot has proper permissions in both channels."
            )
        except Exception as notify_error:
            logger.error(f"Error notifying user: {str(notify_error)}") 