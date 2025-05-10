import os
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        "Welcome to the Media Forwarder Bot!\n\n"
        "Available commands:\n"
        "/setsource @channelname - Set the source channel\n"
        "/setdest @channelname - Set the destination channel\n"
        "You can also use channel IDs (e.g., -1001234567890) for private channels\n"
        "/status - Check current configuration\n"
        "/help - Show this help message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    await update.message.reply_text(
        "Available commands:\n"
        "/setsource @channelname - Set the source channel\n"
        "/setdest @channelname - Set the destination channel\n"
        "You can also use channel IDs (e.g., -1001234567890) for private channels\n"
        "/status - Check current configuration\n"
        "/help - Show this help message"
    )

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
            config['source_channel'] = chat.id
            save_config(config)
            await update.message.reply_text(f"Source channel set successfully to {chat.title}!")
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
            config['destination_channel'] = chat.id
            save_config(config)
            await update.message.reply_text(f"Destination channel set successfully to {chat.title}!")
        else:
            await update.message.reply_text("Please provide a valid channel or supergroup.")
    except Exception as e:
        await update.message.reply_text(
            f"Error setting destination channel: {str(e)}\n"
            "Make sure the bot is a member of the channel and has appropriate permissions."
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command."""
    source = config.get('source_channel', 'Not set')
    dest = config.get('destination_channel', 'Not set')
    
    await update.message.reply_text(
        f"Current configuration:\n"
        f"Source channel: {source}\n"
        f"Destination channel: {dest}"
    )

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

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("setsource", set_source))
        application.add_handler(CommandHandler("setdest", set_dest))
        application.add_handler(CommandHandler("status", status))
        
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