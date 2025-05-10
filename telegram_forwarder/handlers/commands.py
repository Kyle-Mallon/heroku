"""
Command handlers for the Telegram bot.
Handles user commands and channel configuration.
"""

import logging
from typing import Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from ..utils.config import config, save_config

logger = logging.getLogger(__name__)

def create_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard with the given buttons.
    
    Args:
        buttons: List of button rows, where each row is a list of (text, callback_data) tuples
        
    Returns:
        InlineKeyboardMarkup: The created keyboard
    """
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in buttons
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu() -> InlineKeyboardMarkup:
    """Get the main menu keyboard."""
    buttons = [
        [
            ("Set Source Channel", 'set_source'),
            ("Set Destination Channel", 'set_dest')
        ],
        [
            ("Check Status", 'status'),
            ("Help", 'help')
        ]
    ]
    return create_keyboard(buttons)

async def get_chat_info(bot, chat_id: int) -> str:
    """
    Get formatted chat information.
    
    Args:
        bot: The bot instance
        chat_id: The chat ID to get info for
        
    Returns:
        str: Formatted chat information
    """
    try:
        chat = await bot.get_chat(chat_id)
        return f"📢 {chat.title}\nID: {chat_id}"
    except Exception as e:
        logger.error(f"Error getting chat info: {str(e)}")
        return f"ID: {chat_id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    try:
        welcome_text = (
            "👋 Welcome to the Media Forwarder Bot!\n\n"
            "I can help you forward media from one channel to another.\n\n"
            "To get started:\n"
            "1. Add me to your destination channel\n"
            "2. Mention me in that channel\n"
            "3. Set a source channel using /setsource\n\n"
            "What would you like to do?"
        )
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error starting the bot. Please try again later."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "📚 How to use this bot:\n\n"
        "1. Set a destination channel by mentioning the bot in that channel\n"
        "2. Set a source channel using /setsource\n"
        "3. The bot will automatically forward media from source to destination\n\n"
        "You can also set channels using:\n"
        "• Channel username (e.g., @channelname)\n"
        "• Channel link (e.g., t.me/channelname)\n"
        "• Channel ID (e.g., -1001234567890)\n\n"
        "Need help? Use the buttons below or type /start to see the main menu."
    )
    await update.message.reply_text(
        help_text,
        reply_markup=get_main_menu()
    )

async def parse_channel_identifier(identifier: str, bot) -> Optional[Chat]:
    """
    Parse a channel identifier and get the chat object.
    
    Args:
        identifier: The channel identifier (username, link, or ID)
        bot: The bot instance
        
    Returns:
        Optional[Chat]: The chat object if found, None otherwise
    """
    try:
        # Handle channel ID
        if identifier.startswith('-100'):
            return await bot.get_chat(int(identifier))
            
        # Handle username or link
        if identifier.startswith('@'):
            identifier = identifier[1:]
        elif 't.me/' in identifier:
            identifier = identifier.split('t.me/')[-1]
            
        return await bot.get_chat(f"@{identifier}")
    except Exception as e:
        logger.error(f"Error parsing channel identifier: {str(e)}")
        return None

async def set_channel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    channel_type: str
) -> None:
    """
    Handle setting a channel (source or destination).
    
    Args:
        update: The update object
        context: The context object
        channel_type: Either 'source' or 'dest'
    """
    if not context.args:
        await update.message.reply_text(
            f"Please provide the channel link, username, or ID.\n"
            f"Example: /set{channel_type} @channelname or /set{channel_type} t.me/channelname"
        )
        return

    channel_identifier = context.args[0].strip()
    chat = await parse_channel_identifier(channel_identifier, context.bot)
    
    if not chat:
        await update.message.reply_text(
            f"Error setting {channel_type} channel.\n"
            "Make sure the bot is a member of the channel and has appropriate permissions."
        )
        return
        
    if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
        await update.message.reply_text("Please provide a valid channel or supergroup.")
        return
        
    # Create confirmation keyboard
    buttons = [
        [
            ("✅ Confirm", f'confirm_{channel_type}_{chat.id}'),
            ("❌ Cancel", 'cancel')
        ]
    ]
    reply_markup = create_keyboard(buttons)
    
    await update.message.reply_text(
        f"Are you sure you want to set {chat.title} as the {channel_type} channel?",
        reply_markup=reply_markup
    )

async def set_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting the source channel."""
    await set_channel(update, context, 'source')

async def set_dest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting the destination channel."""
    await set_channel(update, context, 'dest')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    source = config.get('source_channel')
    dest = config.get('destination_channel')
    
    status_text = "📊 Current Configuration:\n\n"
    
    # Add source channel info
    if source:
        source_info = await get_chat_info(context.bot, source)
        status_text += f"📥 Source Channel:\n{source_info}\n\n"
    else:
        status_text += "📥 Source Channel: Not set\n\n"
    
    # Add destination channel info
    if dest:
        dest_info = await get_chat_info(context.bot, dest)
        status_text += f"📤 Destination Channel:\n{dest_info}\n\n"
    else:
        status_text += "📤 Destination Channel: Not set\n\n"
    
    # Create status keyboard
    buttons = [
        [
            ("Set Source", 'set_source'),
            ("Set Destination", 'set_dest')
        ],
        [
            ("Remove Source", 'remove_source'),
            ("Remove Destination", 'remove_dest')
        ]
    ]
    reply_markup = create_keyboard(buttons)
    
    await update.message.reply_text(
        status_text,
        reply_markup=reply_markup
    ) 