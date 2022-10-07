import logging
from telegram import ChatAction, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import time
import csv
import datetime
import pendulum
import sys
import redis
from app.models import User

sys.path.append('app/libs')

PHONE_NUMBER = []
# from selenium_tools import get_report

# PORT = int(os.environ.get('PORT', '8443'))

# DEVELOPER_CHAT_ID = 803129892
DEVELOPER_CHAT_ID = 616623134
API_KEY = "5615609770:AAFOqId0ARIGVsfKINMjSLOytIMQWJgPqQ4"
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi!')
    user = User.get_by_chat_id(update.message.chat.id)
    try:
        if user:
            update.message.reply_text(user.phone_number)
    except:
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Enter your phone number", request_contact=True),
                 ],
            ],
            resize_keyboard=True,
        )
    a = update.message.chat.id
    # update.message.reply_text(PHONE_NUMBER)
    update.message.reply_text(a, reply_markup=reply_markup, )
    # PHONE_NUMBER.append(update.message.contact.phone_number)
    # update.message.reply_text(PHONE_NUMBER)

def report(update, context):
    update.message.reply_text("Enter you Uber OTP code from SMS:")
    update.message.reply_text(get_report())


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def code(update: Update, context: CallbackContext):
    r = redis.Redis.from_url(os.environ["REDIS_URL"])
    r.publish('code', update.message.text)
    update.message.reply_text('Wait for report...')
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)


def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("report", report, run_async=True))
    dp.add_handler(MessageHandler(Filters.text, code))
    dp.add_handler(MessageHandler(Filters.contact, code))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


main()