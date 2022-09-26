import logging
from telegram import *
from telegram.ext import *
from requests import *
import os
import time
import csv
import datetime
import pendulum
import sys
import redis

sys.path.append('app/libs')
from selenium_tools import get_report
PORT = int(os.environ.get('PORT', '8443'))

DEVELOPER_CHAT_ID = 803129892

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    # print(update.effective_message.username)
    # print(update.effective_message.text)
    get_number_button = [[KeyboardButton("Надайте ваш номер телефону")]]
    context.bot.send_message(chat_id=update.effective_chat_id, text='Hlo!',
                             reply_markup=ReplyKeyboardMarkup(get_number_button))


# def contact_callback(bot, update):
#     contact = update.effective_message.contact
#     phone = contact.phone_number
#     print(contact)
#     print(phone)
#     update.message.reply_text('Thanks your data is accepted', start(), reply_keyboard=True)


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
    

def main():
    updater = Updater(os.environ["TELEGRAM_TOKEN"], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("report", report, run_async=True))
    # dp.add_handler(MessageHandler(Filters.contact,
    #                               contact_callback, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, code))
    # dp.add_handler(MessageHandler(Filters.contact, contact_callback))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

def run():
    main()
