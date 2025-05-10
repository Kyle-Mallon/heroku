import os
import logging
import sys
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
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

# Telegram API credentials
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE')

# Validate required environment variables
if not all([API_ID, API_HASH, PHONE]):
    logger.error("Missing required environment variables. Please set API_ID, API_HASH, and PHONE.")
    sys.exit(1)

# Initialize the client
client = TelegramClient('forwarder_session', API_ID, API_HASH)

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

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle the /start command."""
    await event.respond(
        "Welcome to the Media Forwarder Bot!\n\n"
        "Available commands:\n"
        "/setsource - Set the source channel\n"
        "/setdest - Set the destination channel\n"
        "/status - Check current configuration\n"
        "/help - Show this help message"
    )

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    """Handle the /help command."""
    await event.respond(
        "Available commands:\n"
        "/setsource - Set the source channel\n"
        "/setdest - Set the destination channel\n"
        "/status - Check current configuration\n"
        "/help - Show this help message"
    )

@client.on(events.NewMessage(pattern='/setsource'))
async def set_source_handler(event):
    """Handle setting the source channel."""
    if event.is_reply:
        try:
            # Get the channel from the replied message
            source_channel = await event.get_reply_message()
            config['source_channel'] = source_channel.chat_id
            save_config(config)
            await event.respond(f"Source channel set successfully!")
        except Exception as e:
            await event.respond(f"Error setting source channel: {str(e)}")
    else:
        await event.respond(
            "Please reply to a message from the source channel with /setsource"
        )

@client.on(events.NewMessage(pattern='/setdest'))
async def set_dest_handler(event):
    """Handle setting the destination channel."""
    if event.is_reply:
        try:
            # Get the channel from the replied message
            dest_channel = await event.get_reply_message()
            config['destination_channel'] = dest_channel.chat_id
            save_config(config)
            await event.respond(f"Destination channel set successfully!")
        except Exception as e:
            await event.respond(f"Error setting destination channel: {str(e)}")
    else:
        await event.respond(
            "Please reply to a message from the destination channel with /setdest"
        )

@client.on(events.NewMessage(pattern='/status'))
async def status_handler(event):
    """Handle the /status command."""
    source = config.get('source_channel', 'Not set')
    dest = config.get('destination_channel', 'Not set')
    
    await event.respond(
        f"Current configuration:\n"
        f"Source channel: {source}\n"
        f"Destination channel: {dest}"
    )

@client.on(events.NewMessage(chats=config.get('source_channel')))
async def forward_media(event):
    """Forward media messages from source to destination channel."""
    if not config.get('source_channel') or not config.get('destination_channel'):
        return
        
    try:
        # Check if the message contains media
        if event.media:
            # Forward the message to the destination channel
            await client.forward_messages(
                config['destination_channel'],
                event.message
            )
            logger.info(f"Forwarded message ID: {event.message.id}")
    except Exception as e:
        logger.error(f"Error forwarding message: {str(e)}")

async def main():
    """Main function to start the userbot."""
    logger.info("Starting the forwarder bot...")
    
    # Keep the script running
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        # Start the client
        client.start()
        
        # Run the main function
        client.loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1) 