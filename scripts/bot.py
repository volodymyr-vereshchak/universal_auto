import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import time
import csv
import datetime
import pendulum
import sys

sys.path.append('app/libs')
from selenium_tools import get_report
PORT = int(os.environ.get('PORT', '8443'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = os.environ['TELEGRAM_TOKEN']

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def report(update, context):
    """Echo the user message."""
    update.message.reply_text(get_report())

def code(update, context):
    """Echo the user message."""
    update.message.reply_text(get_report())

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", report))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("report", report))
    dp.add_handler(CommandHandler("code", code))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    # updater.start_webhook(
    #     listen="0.0.0.0",
    #     port=int(PORT),
    #     url_path=TOKEN,
    #     webhook_url='https://snowy-wood-371.fly.dev/' + TOKEN
    # )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_polling()
    updater.idle()
    logger.warning('APPAAA')

def run():
    main()