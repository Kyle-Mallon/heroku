import os
import sys
from telegram_forwarder import main

if __name__ == "__main__":
    try:
        # Ensure we're in the correct directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the bot
        main()
    except KeyboardInterrupt:
        print("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Bot stopped due to error: {str(e)}")
        sys.exit(1) 