import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot token
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logger.error("Missing BOT_TOKEN environment variable")
    raise ValueError("Missing BOT_TOKEN environment variable")

# Configuration storage
CONFIG_FILE = 'config.json'

def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}

def save_config(config_data: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")

# Initialize config
config = load_config() 