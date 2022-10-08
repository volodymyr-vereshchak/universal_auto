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
import re
from app.models import User

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
    chat_id = update.message.chat.id
    user = User.get_by_chat_id(chat_id)
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Give phone number", request_contact=True),
             ],
        ],
        resize_keyboard=True,
    )
    if user:
        update.message.reply_text("You are already started bot")
    else:
        update.message.reply_text("Please give your number to start bot", reply_markup=reply_markup, )


def get_number(update, context):
    chat_id = update.message.chat.id
    user = User.get_by_chat_id(chat_id)
    if not user:
        phone_number = update.message.contact.phone_number
        custom_user = User(email="null", phone_number=phone_number, chat_id=chat_id)
        custom_user.save()
        update.message.reply_text("Enter your email:")


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
    chat_id = update.message.chat.id
    user = User.get_by_chat_id(chat_id)
    if user.email == "null":
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = update.message.text
        if re.fullmatch(regex, email):
            user.email = email
            user.save()
        else:
            update.message.reply_text('Your email is incorrect, please write again')
    else:
        if user.type == 0:
            # write your code here if user is driver
            pass
        elif user.type == 1:
            # write your code here if user is manager
            pass
        elif user.type == 2:
            # write your code here if user is owner
            pass

def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("report", report, run_async=True))
    dp.add_handler(MessageHandler(Filters.text, code))
    dp.add_handler(MessageHandler(Filters.contact, get_number))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

def run():
    main()