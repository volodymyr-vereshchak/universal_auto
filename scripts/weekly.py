from app.models import UberPaymentsOrder, BoltPaymentsOrder, UklonPaymentsOrder,
import sys
import os

sys.path.append('app/libs')
from selenium_tools import get_report, Uber, Uklon, Bolt


def run():
	directory = '../app'
	files = os.listdir(directory)

	UberPaymentsOrder.download_uber_weekly_file(files=files)
	UklonPaymentsOrder.download_uklon_weekly_file(files=files)
	BoltPaymentsOrder.download_bolt_weekly_file(files=files)

	print(get_report(driver=False, sleep=0, headless=True))
