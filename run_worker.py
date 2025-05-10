import os
import sys
import asyncio
from telegram_forwarder import run_bot

if __name__ == "__main__":
    try:
        # Ensure we're in the correct directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the bot
        run_bot()
    except KeyboardInterrupt:
        print("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Bot stopped due to error: {str(e)}")
        sys.exit(1) 