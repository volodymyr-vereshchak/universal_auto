from app.models import UberPaymentsOrder, BoltPaymentsOrder, UklonPaymentsOrder
import sys
import os

sys.path.append('app/libs')
from selenium_tools import get_report, Uber, Uklon, Bolt


def run(*args):
	directory = '../app'
	files = os.listdir(directory)

	UberPaymentsOrder.download_weekly_report()
	UklonPaymentsOrder.download_weekly_report()
	BoltPaymentsOrder.download_weekly_report()

	if args:
		week = f"2022W{args[0]}5"
	else:
		week = None
	print(get_report(week_number=week, driver=False, sleep=0, headless=True))



