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
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
TOKEN = os.environ['TELEGRAM_TOKEN']

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

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
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("report", report))
    dp.add_handler(CommandHandler("code", code))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    # log all errors
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

def run():
    main()