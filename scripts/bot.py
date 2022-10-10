from app.models import UberPaymentsOrder, BoltPaymentsOrder, UklonPaymentsOrder, FileNameProcessed
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import time
import csv
import datetime
import pendulum
import sys
import redis

sys.path.append('app/libs')
from selenium_tools import get_report, Uber, Uklon, Bolt
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


processed_files = []


def update_db(update, context):
    """Pushing data to database from weekly_csv files"""
    # getting and opening files
    directory = '../app'
    files = os.listdir(directory)

    UberPaymentsOrder.download_uber_weekly_file(files=files)
    UklonPaymentsOrder.download_uklon_weekly_file(files=files)
    BoltPaymentsOrder.download_bolt_weekly_file(files=files)

    files = os.listdir(directory)
    files_csv = filter(lambda x: x.endswith('.csv'), files)
    list_new_files = list(set(files_csv)-set(processed_files))

    if len(list_new_files) == 0:
        update.message.reply_text('No new updates yet')
    else:
        update.message.reply_text('Please wait')
        for name_file in list_new_files:
            processed_files.append(name_file)
            with open(f'{directory}/{name_file}', encoding='utf8') as file:
                if 'Куцко - Income_' in name_file:
                    UklonPaymentsOrder.save_uklon_weekly_report_to_database(file=file)
                elif '-payments_driver-___.csv' in name_file:
                    UberPaymentsOrder.save_uber_weekly_report_to_database(file=file)
                elif 'Kyiv Fleet 03_232 park Universal-auto.csv' in name_file:
                    BoltPaymentsOrder.save_bolt_weekly_report_to_database(file=file)

        FileNameProcessed.save_filename_to_db(processed_files)
        list_new_files.clear()
        update.message.reply_text('Database updated')


def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler('update_db', update_db))
    dp.add_handler(CommandHandler("report", report, run_async=True))
    dp.add_handler(MessageHandler(Filters.text, code))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


def run():
    main()
