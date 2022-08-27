import sys

sys.path.append('app/libs')
from selenium_tools import Uber

def run():

    try:
        ub = Uber(driver=True, sleep=5, headless=True)
        ub.login()  
        ubr = ub.save_report()
        ub.quit()
    except Exception as e:
        print(e)
        ub.driver.get_screenshot_as_file('screenshot.png')
    

 