import sys

sys.path.append('app/libs')
from selenium_tools import get_report

def run():
	print(get_report(driver=False, sleep=0 , headless=True))


 