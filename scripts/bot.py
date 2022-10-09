import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import time
import csv
import datetime
import pendulum
import sys
import redis

from scripts.driversrating import DriversRatingMixin

sys.path.append('app/libs')
from selenium_tools import get_report
PORT = int(os.environ.get('PORT', '8443'))

DEVELOPER_CHAT_ID = 803129892

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi!')

def report(update, context):
    update.message.reply_text("Enter you Uber OTP code from SMS:")
    update.message.reply_text(get_report())

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def code(update, context):
    r = redis.Redis.from_url(os.environ["REDIS_URL"])
    r.publish('code', update.message.text)
    update.message.reply_text('Wait for report...')
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    
def drivers_rating(context):
    text = 'Drivers Rating\n\n'
    for fleet in DriversRatingMixin().get_rating():
        text += fleet['fleet'] + '\n'
        text += '\n'.join([f"{item['num']} {item['driver']} {item['trips']}" for item in fleet['rating']]) + '\n\n'
    context.bot.send_message(chat_id=-828544906, text=text)

def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("report", report, run_async=True))
    dp.add_handler(MessageHandler(Filters.text, code))
    dp.add_error_handler(error)
    updater.job_queue.run_daily(drivers_rating, datetime.time(12, 0, 0), (0,))
    # updater.job_queue.run_repeating(drivers_rating, interval=120, first=10)
    updater.start_polling()
    updater.idle()

def run():
    main()
