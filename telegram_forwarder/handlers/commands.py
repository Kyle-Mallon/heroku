import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..utils.config import config, save_config

logger = logging.getLogger(__name__)

def get_main_menu() -> InlineKeyboardMarkup:
    """Get the main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("Set Source Channel", callback_data='set_source'),
            InlineKeyboardButton("Set Destination Channel", callback_data='set_dest')
        ],
        [
            InlineKeyboardButton("Check Status", callback_data='status'),
            InlineKeyboardButton("Help", callback_data='help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_chat_info(bot, chat_id: int) -> str:
    """Get formatted chat information."""
    try:
        chat = await bot.get_chat(chat_id)
        return f"📢 {chat.title}\nID: {chat_id}"
    except Exception:
        return f"ID: {chat_id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    try:
        welcome_text = (
            "👋 Welcome to the Media Forwarder Bot!\n\n"
            "I can help you forward media from one channel to another.\n\n"
            "What would you like to do?"
        )
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error starting the bot. Please try again later."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "📚 *How to use this bot:*\n\n"
        "1. Set a source channel using `/setsource`\n"
        "2. Set a destination channel using `/setdest`\n"
        "3. The bot will automatically forward media from source to destination\n\n"
        "You can use:\n"
        "• Channel username (e.g., @channelname)\n"
        "• Channel link (e.g., t.me/channelname)\n"
        "• Channel ID (e.g., -1001234567890)\n\n"
        "Need help? Use the buttons below or type /start to see the main menu."
    )
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu()
    )

async def set_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting the source channel."""
    if not context.args:
        await update.message.reply_text(
            "Please provide the channel link, username, or ID.\n"
            "Example: /setsource @channelname or /setsource t.me/channelname or /setsource -1001234567890"
        )
        return

    channel_identifier = context.args[0].strip()
    
    try:
        # Check if it's a channel ID (starts with -100)
        if channel_identifier.startswith('-100'):
            chat = await context.bot.get_chat(int(channel_identifier))
        else:
            # Remove @ or t.me/ if present
            if channel_identifier.startswith('@'):
                channel_identifier = channel_identifier[1:]
            elif 't.me/' in channel_identifier:
                channel_identifier = channel_identifier.split('t.me/')[-1]
            chat = await context.bot.get_chat(f"@{channel_identifier}")

        if chat.type in ['channel', 'supergroup']:
            # Create confirmation keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Confirm", callback_data=f'confirm_source_{chat.id}'),
                    InlineKeyboardButton("❌ Cancel", callback_data='cancel')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Are you sure you want to set {chat.title} as the source channel?",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("Please provide a valid channel or supergroup.")
    except Exception as e:
        await update.message.reply_text(
            f"Error setting source channel: {str(e)}\n"
            "Make sure the bot is a member of the channel and has appropriate permissions."
        )

async def set_dest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting the destination channel."""
    if not context.args:
        await update.message.reply_text(
            "Please provide the channel link, username, or ID.\n"
            "Example: /setdest @channelname or /setdest t.me/channelname or /setdest -1001234567890"
        )
        return

    channel_identifier = context.args[0].strip()
    
    try:
        # Check if it's a channel ID (starts with -100)
        if channel_identifier.startswith('-100'):
            chat = await context.bot.get_chat(int(channel_identifier))
        else:
            # Remove @ or t.me/ if present
            if channel_identifier.startswith('@'):
                channel_identifier = channel_identifier[1:]
            elif 't.me/' in channel_identifier:
                channel_identifier = channel_identifier.split('t.me/')[-1]
            chat = await context.bot.get_chat(f"@{channel_identifier}")

        if chat.type in ['channel', 'supergroup']:
            # Create confirmation keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Confirm", callback_data=f'confirm_dest_{chat.id}'),
                    InlineKeyboardButton("❌ Cancel", callback_data='cancel')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Are you sure you want to set {chat.title} as the destination channel?",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("Please provide a valid channel or supergroup.")
    except Exception as e:
        await update.message.reply_text(
            f"Error setting destination channel: {str(e)}\n"
            "Make sure the bot is a member of the channel and has appropriate permissions."
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    source = config.get('source_channel')
    dest = config.get('destination_channel')
    
    status_text = "📊 *Current Configuration:*\n\n"
    
    if source:
        source_info = await get_chat_info(context.bot, source)
        status_text += f"📥 *Source Channel:*\n{source_info}\n\n"
    else:
        status_text += "📥 *Source Channel:* Not set\n\n"
    
    if dest:
        dest_info = await get_chat_info(context.bot, dest)
        status_text += f"📤 *Destination Channel:*\n{dest_info}\n\n"
    else:
        status_text += "📤 *Destination Channel:* Not set\n\n"
    
    # Add action buttons
    keyboard = [
        [
            InlineKeyboardButton("Set Source", callback_data='set_source'),
            InlineKeyboardButton("Set Destination", callback_data='set_dest')
        ],
        [
            InlineKeyboardButton("Remove Source", callback_data='remove_source'),
            InlineKeyboardButton("Remove Destination", callback_data='remove_dest')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    ) 