import os
import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from dotenv import load_dotenv
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout  # Log to stdout for Heroku
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot token
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logger.error("Missing BOT_TOKEN environment variable")
    sys.exit(1)

# Configuration storage
CONFIG_FILE = 'channel_config.json'

def load_config():
    """Load channel configuration from file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
    return {'source_channel': None, 'destination_channel': None}

def save_config(config):
    """Save channel configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")

# Load initial configuration
config = load_config()

def get_main_menu():
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

async def get_chat_info(bot, chat_id):
    """Get formatted chat information."""
    try:
        chat = await bot.get_chat(chat_id)
        return f"📢 {chat.title}\nID: {chat_id}"
    except Exception:
        return f"ID: {chat_id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == 'set_source':
        await query.message.reply_text(
            "Please provide the source channel:\n"
            "• Username (e.g., @channelname)\n"
            "• Link (e.g., t.me/channelname)\n"
            "• ID (e.g., -1001234567890)\n\n"
            "Use the command: /setsource [channel]"
        )
    elif query.data == 'set_dest':
        await query.message.reply_text(
            "Please provide the destination channel:\n"
            "• Username (e.g., @channelname)\n"
            "• Link (e.g., t.me/channelname)\n"
            "• ID (e.g., -1001234567890)\n\n"
            "Use the command: /setdest [channel]"
        )
    elif query.data == 'status':
        await status(update, context)
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data == 'cancel':
        await query.message.edit_text("Operation cancelled.")
    elif query.data.startswith('confirm_source_'):
        chat_id = int(query.data.split('_')[2])
        try:
            chat = await context.bot.get_chat(chat_id)
            config['source_channel'] = chat_id
            save_config(config)
            await query.message.edit_text(f"✅ Source channel set successfully to {chat.title}!")
        except Exception as e:
            await query.message.edit_text(f"❌ Error setting source channel: {str(e)}")
    elif query.data.startswith('confirm_dest_'):
        chat_id = int(query.data.split('_')[2])
        try:
            chat = await context.bot.get_chat(chat_id)
            config['destination_channel'] = chat_id
            save_config(config)
            await query.message.edit_text(f"✅ Destination channel set successfully to {chat.title}!")
        except Exception as e:
            await query.message.edit_text(f"❌ Error setting destination channel: {str(e)}")
    elif query.data == 'remove_source':
        if config.get('source_channel'):
            config['source_channel'] = None
            save_config(config)
            await query.message.edit_text("✅ Source channel removed successfully!")
        else:
            await query.message.edit_text("❌ No source channel set to remove.")
    elif query.data == 'remove_dest':
        if config.get('destination_channel'):
            config['destination_channel'] = None
            save_config(config)
            await query.message.edit_text("✅ Destination channel removed successfully!")
        else:
            await query.message.edit_text("❌ No destination channel set to remove.")

async def set_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def set_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    await update.message.reply_text(status_text, parse_mode='Markdown', reply_markup=reply_markup)

async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward media messages from source to destination channel."""
    if not config.get('source_channel') or not config.get('destination_channel'):
        return
        
    try:
        # Check if the message contains media
        if update.message.photo or update.message.video or update.message.document:
            # Forward the message to the destination channel
            await update.message.forward(chat_id=config['destination_channel'])
            logger.info(f"Forwarded message ID: {update.message.message_id}")
    except Exception as e:
        logger.error(f"Error forwarding message: {str(e)}")

async def setup_commands(application: Application):
    """Setup bot commands with descriptions."""
    commands = [
        ("start", "Start the bot and see available commands"),
        ("help", "Show help message"),
        ("setsource", "Set source channel (use @channelname or -1001234567890)"),
        ("setdest", "Set destination channel (use @channelname or -1001234567890)"),
        ("status", "Check current channel configuration")
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Start the bot."""
    try:
        # Create the Application with specific settings
        application = (
            Application.builder()
            .token(TOKEN)
            .concurrent_updates(True)  # Enable concurrent updates
            .build()
        )

        # Setup commands
        application.create_task(setup_commands(application))

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("setsource", set_source))
        application.add_handler(CommandHandler("setdest", set_dest))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Add message handler for forwarding media
        application.add_handler(MessageHandler(
            filters.Chat(config.get('source_channel')) & 
            (filters.PHOTO | filters.VIDEO | filters.Document.ALL),
            forward_media
        ))

        # Start the Bot with error handling
        logger.info("Starting bot...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # Drop pending updates on startup
            close_loop=False
        )
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 