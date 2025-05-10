# Telegram Media Forwarder

A Telegram bot that forwards media from one channel to another.

## Quick Setup

1. **Install Heroku CLI on Windows**
   ```bash
   # Install Chocolatey (if not already installed)
   # Open PowerShell as Administrator and run:
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

   # Install Heroku CLI using Chocolatey
   choco install heroku-cli
   ```

2. **Get Telegram API Credentials**
   - Go to https://my.telegram.org/auth
   - Log in with your phone number
   - Click on 'API development tools'
   - Create a new application
   - Save your `API_ID` and `API_HASH`

3. **Deploy to Heroku**
   ```bash
   # Login to Heroku
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

4. **Set Up Channels**
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