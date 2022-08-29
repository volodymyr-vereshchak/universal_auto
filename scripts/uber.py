import sys
sys.path.append('app/libs')
from selenium_tools import Uber

def run():
    ub = Uber(driver=True, sleep=5, headless=False)
    ub.login()
    ub.download_payments_order()
    ubr = ub.save_report()
    ub.quit()





    # p = r.pubsub()
    # p.subscribe(channel)
    # while True:
    #     try:
    #         otp = p.get_message()
    #     except redis.ConnectionError:
    #         p = r.pubsub()
    #         p.subscribe(channel)
    #     time.sleep(0.01)  

 