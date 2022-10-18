import sys
import os
sys.path.append('app/libs')
from selenium_tools import Uber, Uklon, Bolt, get_report


def run(*args):
    if args:
        week = f"2022W{args[0]}5"
    else:
        week = None
    
    Uklon.download_weekly_report(week_number=week, driver=True, sleep=5, headless=True)
    Bolt.download_weekly_report(week_number=week, driver=True, sleep=5, headless=True)
    Uber.download_weekly_report(week_number=week, driver=True, sleep=5, headless=True)
    print(get_report(week_number=week, driver=False, sleep=0, headless=True))



