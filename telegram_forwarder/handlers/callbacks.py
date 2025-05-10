"""
Callback query handler for the Telegram bot.
Handles button presses and channel configuration confirmations.
"""

import logging
from typing import Optional, Tuple
from telegram import Update, Chat
from telegram.ext import ContextTypes
from ..utils.config import config, save_config
from .commands import status, help_command

logger = logging.getLogger(__name__)

async def handle_channel_setting(
    query: Update.callback_query,
    context: ContextTypes.DEFAULT_TYPE,
    channel_type: str
) -> None:
    """
    Handle channel setting confirmation.
    
    Args:
        query: The callback query
        context: The context object
        channel_type: Either 'source' or 'dest'
    """
    try:
        chat_id = int(query.data.split('_')[2])
        chat = await context.bot.get_chat(chat_id)
        config[f'{channel_type}_channel'] = chat_id
        save_config(config)
        await query.message.edit_text(
            f"✅ {channel_type.title()} channel set successfully to {chat.title}!"
        )
    except Exception as e:
        logger.error(f"Error setting {channel_type} channel: {str(e)}")
        await query.message.edit_text(
            f"❌ Error setting {channel_type} channel: {str(e)}"
        )

async def handle_channel_removal(
    query: Update.callback_query,
    channel_type: str
) -> None:
    """
    Handle channel removal.
    
    Args:
        query: The callback query
        channel_type: Either 'source' or 'dest'
    """
    if config.get(f'{channel_type}_channel'):
        config[f'{channel_type}_channel'] = None
        save_config(config)
        await query.message.edit_text(
            f"✅ {channel_type.title()} channel removed successfully!"
        )
    else:
        await query.message.edit_text(
            f"❌ No {channel_type} channel set to remove."
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle button presses and channel configuration.
    
    Args:
        update: The update object
        context: The context object
    """
    query = update.callback_query
    await query.answer()

    # Map callback data to handler functions
    handlers = {
        'set_source': lambda: query.message.reply_text(
            "Please provide the source channel:\n"
            "• Username (e.g., @channelname)\n"
            "• Link (e.g., t.me/channelname)\n"
            "• ID (e.g., -1001234567890)\n\n"
            "Use the command: /setsource [channel]"
        ),
        'set_dest': lambda: query.message.reply_text(
            "Please provide the destination channel:\n"
            "• Username (e.g., @channelname)\n"
            "• Link (e.g., t.me/channelname)\n"
            "• ID (e.g., -1001234567890)\n\n"
            "Use the command: /setdest [channel]"
        ),
        'status': lambda: status(update, context),
        'help': lambda: help_command(update, context),
        'cancel': lambda: query.message.edit_text("Operation cancelled.")
    }

    # Handle simple callbacks
    if query.data in handlers:
        await handlers[query.data]()
        return

    # Handle channel setting confirmations
    if query.data.startswith('confirm_source_'):
        await handle_channel_setting(query, context, 'source')
    elif query.data.startswith('confirm_dest_'):
        await handle_channel_setting(query, context, 'dest')
    # Handle channel removals
    elif query.data == 'remove_source':
        await handle_channel_removal(query, 'source')
    elif query.data == 'remove_dest':
        await handle_channel_removal(query, 'dest') 