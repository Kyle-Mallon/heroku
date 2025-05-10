import os
import sys
import tracemalloc
from telegram_forwarder import main

if __name__ == "__main__":
    try:
        # Enable tracemalloc for debugging
        tracemalloc.start()
        
        # Ensure we're in the correct directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the bot
        main()
    except KeyboardInterrupt:
        print("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Bot stopped due to error: {str(e)}")
        # Print tracemalloc statistics
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        print("\nTop 10 memory allocations:")
        for stat in top_stats[:10]:
            print(stat)
        sys.exit(1)
    finally:
        tracemalloc.stop() 