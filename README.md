# Telegram Media Forwarder Bot

A Telegram bot that forwards media messages from one channel to another. Built with python-telegram-bot and designed for easy deployment on Heroku.

## Features

- Forward media messages between channels
- Support for photos, videos, documents, and audio
- Easy channel configuration through commands
- Interactive menu with buttons
- Robust error handling and logging
- Automatic retry on network issues

## Prerequisites

- Python 3.8 or higher
- A Telegram bot token (get it from [@BotFather](https://t.me/BotFather))
- Heroku account (for deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram_forwarder.git
cd telegram_forwarder
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:
```
BOT_TOKEN=your_bot_token_here
```

2. Set up your Heroku environment variables:
```bash
heroku config:set BOT_TOKEN=your_bot_token_here
```

## Usage

1. Start the bot:
```bash
python run_worker.py
```

2. Add the bot to your channels with admin privileges

3. Configure the channels:
   - Mention the bot in the destination channel
   - Use `/setsource` to set the source channel
   - Use `/setdest` to set the destination channel
   - Use `/status` to check current configuration
   - Use `/help` for more information

## Deployment

1. Create a new Heroku app:
```bash
heroku create your-app-name
```

2. Deploy to Heroku:
```bash
git push heroku main
```

3. Start the worker:
```bash
heroku ps:scale worker=1
```

## Development

- The project uses Python 3.8+ features
- Follows PEP 8 style guide
- Uses type hints for better code quality
- Includes comprehensive error handling
- Uses logging for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [nest-asyncio](https://github.com/erdewit/nest_asyncio) 