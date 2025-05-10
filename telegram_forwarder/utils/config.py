"""
Configuration management for the Telegram bot.
Handles loading and saving of bot configuration and environment variables.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass

class ConfigManager:
    """Manages bot configuration and environment variables."""
    
    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._validate_environment()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            self._config = {}
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            raise ConfigError(f"Failed to save config: {str(e)}")
    
    def _validate_environment(self) -> None:
        """Validate required environment variables."""
        if not os.getenv('BOT_TOKEN'):
            logger.error("Missing BOT_TOKEN environment variable")
            raise ConfigError("Missing BOT_TOKEN environment variable")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save to file.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self._save_config()
    
    def delete(self, key: str) -> None:
        """
        Delete a configuration value and save to file.
        
        Args:
            key: Configuration key to delete
        """
        if key in self._config:
            del self._config[key]
            self._save_config()
    
    @property
    def token(self) -> str:
        """Get the bot token from environment variables."""
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ConfigError("BOT_TOKEN not found in environment variables")
        return token

# Create global config instance
config_manager = ConfigManager()
config = config_manager._config
save_config = config_manager._save_config 