import logging
from app.models import WeeklyReportFile
from telegram import * 
from telegram.ext import *
import os
import time
import csv
import datetime
import pendulum
import sys
import redis
import html
import json
import logging
import traceback
from app.models import *
from . import bolt, uklon, uber

sys.path.append('app/libs')
from app.libs.selenium_tools import get_report
PORT = int(os.environ.get('PORT', '8443'))

DEVELOPER_CHAT_ID = 803129892

username = ''  # <- Global username take argument from foo authorization
managers_list = []  # <- List of users to take all statistic day 
uber_drivers_list = []# <- List of users who can request only self stat from Uber table
uklon_drivers_list = []# <- List of users who can request only self stat from Uklon table
bolt_drivers_list = []# <- List of users who can request only self stat from Bolt table
owners_list = []

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def report(update, context):
    update.message.reply_text("Enter you Uber OTP code from SMS:")
    update.message.reply_text(get_report())

def save_reports(update, context):
    wrf = WeeklyReportFile()
    wrf.save_weekly_reports_to_db()
    update.message.reply_text("Reports have been saved")
    
def code(update, context):
    r = redis.Redis.from_url(os.environ["REDIS_URL"])
    r.publish('code', update.message.text)
    update.message.reply_text('Generating a report...')

def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
def get_owner_today_report(update, context) -> str:
    pass

def aut_handler(update, context) -> list:
    global username
    username = update.message.chat.username
    if 'Get autorizate' in update.message.text:
        if username in managers_list:
            get_stat_for_manager(update, context)
        elif username in owners_list:
            get_owner_today_report(update, context)
        elif username in uber_drivers_list or uklon_drivers_list or bolt_drivers_list:
            choice_driver_option(update, context)
        else:
            error_handler()

def get_driver_week_report(update, context) -> str:
    pass

def get_update_report(update, context):
    global username
    if username in uklon_drivers_list:
        update.message.reply_text("Enter you Uklon OTP code from SMS:")
        uklon.run()
        aut_handler()
    elif username in bolt_drivers_list:
        update.message.reply_text("Enter you Bolt OTP code from SMS:")
        bolt.run()
        aut_handler()
    elif username in uber_drivers_list:
        update.message.reply_text("Enter you Uber OTP code from SMS:")
        uber.run()
        aut_handler()

def get_driver_today_report(update, context) -> str:
    global username
    driver_first_name = Users.objects.filter(user_id = {update.message.chat.id})
    driver_ident = PaymentsOrder.objects.filter(driver_uuid='')
    if username in uklon_drivers_list:
        data = PaymentsOrder.objects.filter(transaction_time = date.today(), driver_uuid = {driver_ident} )
        update.message.reply_text(f'Hi {update.message.chat.username} uklon driver')
        update.message.reply_text(text = data)
    elif username in bolt_drivers_list:
        data = PaymentsOrder.objects.filter(transaction_time = date.today(), driver_uuid = {driver_ident} )
        update.message.reply_text(f'Hi {update.message.chat.username} bolt driver')
        update.message.reply_text(text = data)
    elif username in uber_drivers_list:
        data = PaymentsOrder.objects.filter(transaction_time = date.today(), driver_uuid = {driver_ident})
        update.message.reply_text(f'Hi {update.message.chat.username} uber driver')
        update.message.reply_text(text = data)

def get_manager_today_report(update, context) -> str:
    global username
    if username in managers_list:
        data = PaymentsOrder.objects.filter(transaction_time = date.today())
        update.message.reply_text(text = data)
    else:
        error_handler()
 
def reg_handler(update,context) -> object:
    pass

def choice_driver_option(update, context) -> list:
        update.message.reply_text(f'Hi {update.message.chat.username} driver')
        buttons = [[KeyboardButton('Get today statistic')], [KeyboardButton('Choice week number')],[KeyboardButton('Update report')]]
        context.bot.send_message(chat_id=update.effective_chat.id, text='choice option',
        reply_markup=ReplyKeyboardMarkup(buttons))

def get_stat_for_manager(update, context) -> list:
        update.message.reply_text(f'Hi {update.message.chat.username} manager')
        buttons = [[KeyboardButton('Get all today statistic')]]
        context.bot.send_message(chat_id=update.effective_chat.id, text='choice option',
        reply_markup=ReplyKeyboardMarkup(buttons))

def authorization(update, context) -> list: 
    buttons = [[KeyboardButton('Get autorizate')],[KeyboardButton('Get registration')]]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'hi {update.message.chat.username}',
    reply_markup=ReplyKeyboardMarkup(buttons))

def get_help(update, context)-> str:
    update.message.reply_text('''For first step make registration by, or autorizate by /start command, if already registered.
    after all you can update your report, or pull statistic for choice''')

def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start",  authorization))
    dp.add_handler(CommandHandler("help", get_help))
    dp.add_handler(CommandHandler("report", report, run_async=True))
    dp.add_handler(CommandHandler("save_reports", save_reports))
    dp.add_handler(MessageHandler(Filters.text('code'), code))
    dp.add_handler(MessageHandler(Filters.text('Get registration'), reg_handler ))
    dp.add_handler(MessageHandler(Filters.text('Get all today statistic'),get_manager_today_report  ))
    dp.add_handler(MessageHandler(Filters.text('Get today statistic'), get_driver_today_report ))
    dp.add_handler(MessageHandler(Filters.text('Choice week number'), get_driver_week_report))
    dp.add_handler(MessageHandler(Filters.text('Update report'), get_update_report))
    dp.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()

def run():
    main()
