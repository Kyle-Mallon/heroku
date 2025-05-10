# Telegram Media Forwarder

A Telegram bot that forwards media from one channel to another.

## Quick Setup

1. **Get Telegram API Credentials**
   - Go to https://my.telegram.org/auth
   - Log in with your phone number
   - Click on 'API development tools'
   - Create a new application
   - Save your `API_ID` and `API_HASH`

2. **Deploy to Heroku**
   ```bash
   # Install Heroku CLI and login
   heroku login

   # Create new Heroku app
   heroku create your-app-name

   # Set your Telegram credentials
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set PHONE=your_phone_number

   # Deploy the bot
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main

   # Start the bot
   heroku ps:scale worker=1
   ```

3. **Set Up Channels**
   - Start a chat with your bot
   - Forward a message from the source channel to the bot
   - Reply with `/setsource`
   - Forward a message from the destination channel to the bot
   - Reply with `/setdest`

## Available Commands

- `/start` - Show welcome message
- `/help` - Show help message
- `/setsource` - Set source channel
- `/setdest` - Set destination channel
- `/status` - Check current settings

## Important Notes

- The bot will forward all media (photos, videos, documents)
- You need to be a member of both channels
- You need posting permissions in the destination channel
- The bot will need to re-authenticate if Heroku restarts 