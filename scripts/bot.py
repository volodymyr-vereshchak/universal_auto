from app.models import UberPaymentsOrder, BoltPaymentsOrder, UklonPaymentsOrder
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


processed_files = []


def update_db(update, context):
    """Pushing data to database from csv files"""
    # getting and opening files
    directory = '../app'
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
                    reader = csv.reader(file, delimiter='|')
                    next(reader)
                    for row in reader:
                        # date format update
                        get_first_date = name_file[15:-25].split(' ')
                        first_date = f"{get_first_date[0].replace('_', '-')} {get_first_date[1].replace('_', ':')}"
                        report_from = datetime.datetime.strptime(first_date, "%m-%d-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                        second_date = name_file[-25:].split('-')[-1][:-7]
                        report_to = datetime.datetime.strptime(second_date, "%m_%d_%Y %H_%M_%S").strftime("%Y-%m-%d %H:%M:%S")
                        order = UklonPaymentsOrder(
                                                report_from=f'{report_from}+03:00',
                                                report_to=f'{report_to}+03:00',
                                                report_file_name=name_file,
                                                signal=row[0],
                                                licence_plate=row[2],
                                                total_rides=int(row[4]),
                                                total_distance=int(row[6]),
                                                total_amount_cach=float(row[8]),
                                                total_amount_cach_less=float(row[10]),
                                                total_amount=float(row[12]),
                                                total_amount_without_comission=float(row[14]),
                                                bonuses=float(row[16]))

                        order.save()
                elif '-payments_driver-___.csv' in name_file:
                    reader = csv.reader(file, delimiter=',')
                    next(reader)
                    for row in reader:
                        get_date = name_file.split('-')
                        update_first_date = datetime.datetime.strptime(get_date[0], '%Y%m%d').strftime("%Y-%m-%d")
                        update_second_date = datetime.datetime.strptime(get_date[1], '%Y%m%d').strftime("%Y-%m-%d")
                        first_datetime = f'{update_first_date} {datetime.datetime.now().time()}+03:00'
                        second_datetime = f'{update_second_date} {datetime.datetime.now().time()}+03:00'
                        order = UberPaymentsOrder(
                            report_from=first_datetime,
                            report_to=second_datetime,
                            report_file_name=name_file,
                            driver_uuid=row[0],
                            first_name=row[1],
                            last_name=row[2],
                            total_amount=float(row[3] or 0),
                            total_clean_amout=float(row[4] or 0),
                            returns=float(row[5] or 0),
                            total_amount_cach=float(row[6] or 0),
                            transfered_to_bank=float(row[7] or 0),
                            tips=float(row[9] or 0))

                        order.save()
                elif 'Kyiv Fleet 03_232 park Universal-auto.csv' in name_file:
                    reader = csv.reader(file, delimiter=',')
                    next(reader)
                    next(reader)
                    for row in reader:
                        if row[0] == "":
                            break
                        if row[0] is None:
                            break
                        get_date = row[2].split(' ')
                        first_datetime = f'{get_date[1]} {datetime.datetime.now().time()}+03:00'
                        second_datetime = f'{get_date[-1]} {datetime.datetime.now().time()}+03:00'
                        order = BoltPaymentsOrder(
                            report_from=first_datetime,
                            report_to=second_datetime,
                            report_file_name=name_file,
                            driver_full_name=row[0],
                            mobile_number=row[1][1:],
                            range_string=row[2],
                            total_amount=float(row[3]),
                            cancels_amount=float(row[4]),
                            autorization_payment=float(row[5]),
                            autorization_deduction=float(row[6]),
                            additional_fee=float(row[7]),
                            fee=float(row[8]),
                            total_amount_cach=float(row[9]),
                            discount_cash_trips=float(row[10]),
                            driver_bonus=float(row[11]),
                            compensation=float(row[12] or 0),
                            refunds=float(row[13]),
                            tips=float(row[14]),
                            weekly_balance=float(row[15]))

                        order.save()

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
