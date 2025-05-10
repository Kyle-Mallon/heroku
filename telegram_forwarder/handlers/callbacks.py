import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.config import config, save_config
from .commands import status, help_command

logger = logging.getLogger(__name__)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == 'set_source':
        await query.message.reply_text(
            "Please provide the source channel:\n"
            "• Username (e.g., @channelname)\n"
            "• Link (e.g., t.me/channelname)\n"
            "• ID (e.g., -1001234567890)\n\n"
            "Use the command: /setsource [channel]"
        )
    elif query.data == 'set_dest':
        await query.message.reply_text(
            "Please provide the destination channel:\n"
            "• Username (e.g., @channelname)\n"
            "• Link (e.g., t.me/channelname)\n"
            "• ID (e.g., -1001234567890)\n\n"
            "Use the command: /setdest [channel]"
        )
    elif query.data == 'status':
        await status(update, context)
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data == 'cancel':
        await query.message.edit_text("Operation cancelled.")
    elif query.data.startswith('confirm_source_'):
        chat_id = int(query.data.split('_')[2])
        try:
            chat = await context.bot.get_chat(chat_id)
            config['source_channel'] = chat_id
            save_config(config)
            await query.message.edit_text(f"✅ Source channel set successfully to {chat.title}!")
        except Exception as e:
            await query.message.edit_text(f"❌ Error setting source channel: {str(e)}")
    elif query.data.startswith('confirm_dest_'):
        chat_id = int(query.data.split('_')[2])
        try:
            chat = await context.bot.get_chat(chat_id)
            config['destination_channel'] = chat_id
            save_config(config)
            await query.message.edit_text(f"✅ Destination channel set successfully to {chat.title}!")
        except Exception as e:
            await query.message.edit_text(f"❌ Error setting destination channel: {str(e)}")
    elif query.data == 'remove_source':
        if config.get('source_channel'):
            config['source_channel'] = None
            save_config(config)
            await query.message.edit_text("✅ Source channel removed successfully!")
        else:
            await query.message.edit_text("❌ No source channel set to remove.")
    elif query.data == 'remove_dest':
        if config.get('destination_channel'):
            config['destination_channel'] = None
            save_config(config)
            await query.message.edit_text("✅ Destination channel removed successfully!")
        else:
            await query.message.edit_text("❌ No destination channel set to remove.") 