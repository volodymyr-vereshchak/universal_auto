import time
import csv
import datetime
import sys
import os
import re
import itertools
import logging

import redis
import pendulum
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.models import UklonPaymentsOrder
from app.models import UberPaymentsOrder
from app.models import BoltPaymentsOrder
from app.models import Driver, Fleets_drivers_vehicles_rate

class SeleniumTools():
    def __init__(self, session, week_number=None):
        self.session_file_name = session
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        if(week_number):
            self.current_date = pendulum.parse(week_number, tz="Europe/Kiev")
        else:
            self.current_date = pendulum.now().start_of('week').subtract(days=3)
    
    def report_file_name(self, patern):
        filenames = os.listdir(os.curdir)
        for file in filenames:
            if re.search(patern, file):
                return file 

    def week_number(self):
        return f'{int(self.start_of_week().strftime("%W"))}'

    def start_of_week(self):
        return self.current_date.start_of('week')
    def end_of_week(self):
        return self.current_date.end_of('week')

    def remove_session(self):
        os.remove(self.session_file_name)
    
    def retry(self, fun, headless=False):
        for i in range(2):
            try:
               time.sleep(0.3)
               return fun(headless)
            except Exception:
                try:
                    self.remove_session()
                    return fun(headless)
                except FileNotFoundError:
                    return fun(headless)
                continue

    def build_driver(self, headless=False):
        options = Options()
        options = webdriver.ChromeOptions();
        options.add_experimental_option("prefs", {
            "download.default_directory": os.getcwd(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        options.add_argument("--disable-infobars")
        options.add_argument("--enable-file-cookies")
        options.add_argument('--disable-blink-features=AutomationControlled')

        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument("--no-sandbox")
            options.add_argument("--screen-size=1920,1080")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-extensions")
            options.add_argument('--disable-dev-shm-usage')    
            options.add_argument('--disable-software-rasterizer')
            options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
            options.add_argument("--disable-notifications")

        driver = webdriver.Chrome(options=options, port=9514)
        return driver

class Uber(SeleniumTools):    
    def __init__(self, week_number=None, driver=True, sleep=3, headless=False, base_url="https://supplier.uber.com"):
        super().__init__('uber', week_number=week_number)
        self.sleep = sleep
        if driver:
            self.driver = self.retry(self.build_driver, headless)
            self.base_url = base_url

    def quit(self):
        self.driver.quit()

    def login_v2(self, link = "https://drivers.uber.com/"):
        self.driver.get(link)
        self.login_form('PHONE_NUMBER_or_EMAIL_ADDRESS', 'forward-button', By.ID)  
        self.force_opt_form()
        self.otp_code_v2()
        self.otp_code_v1()
        self.password_form('PASSWORD', 'forward-button', By.ID)
        if self.sleep:
            time.sleep(self.sleep)

    def login(self, link = "https://auth.uber.com/login/"):
        self.driver.get(link)
        self.login_form('userInput', 'next-button-wrapper', By.CLASS_NAME)
        self.otp_code_v1()
        self.password_form('password', 'next-button-wrapper', By.CLASS_NAME)
        if self.sleep:
            time.sleep(self.sleep)
    
    def generate_payments_order(self):
        self.driver.get(f"{self.base_url}/orgs/49dffc54-e8d9-47bd-a1e5-52ce16241cb6/reports")
        if self.sleep:
            time.sleep(self.sleep)
        self.driver.get_screenshot_as_file('generate_payments_order.png')
        menu = '//div[@data-testid="report-type-dropdown"]/div/div'
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, menu)))
        self.driver.find_element(By.XPATH, menu).click()   
        try:
            xpath = '//ul/li/div[text()[contains(.,"Payments Driver")]]'
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        except Exception:
            xpath = '//ul/li/div[text()[contains(.,"Payments driver")]]'
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        start = self.driver.find_element(By.XPATH, '//div[@data-testid="start-date-picker"]/div/div/div/input')
        start.send_keys(Keys.NULL)
        self.driver.find_element(By.XPATH, f'//div[@aria-roledescription="button"]/div[text()={self.start_of_week().strftime("%-d")}]').click()
        end = self.driver.find_element(By.XPATH, '//div[@data-testid="end-date-picker"]/div/div/div/input')
        end.send_keys(Keys.NULL)
        self.driver.find_element(By.XPATH, f'//div[@aria-roledescription="button"]/div[text()="{self.end_of_week().strftime("%-d")}"]').click()
        self.driver.find_element(By.XPATH, '//button[@data-testid="generate-report-button"]').click()

        return f'{self.payments_order_file_name()}'

    def download_payments_order(self):
        if os.path.exists(f'{self.payments_order_file_name()}'):
            print('Report already downloaded')
            return 
        self.generate_payments_order()
        download_button = '//div[1][@data-testid="payment-reporting-table-row"]/div/div/div/div/button'
        try:
            in_progress_text = '//div[1][@data-testid="payment-reporting-table-row"]/div/div/div/div[text()[contains(.,"In progress")]]'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, in_progress_text)))
            WebDriverWait(self.driver, 300).until_not(EC.presence_of_element_located((By.XPATH, in_progress_text)))
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, download_button)))
        except Exception as e:
            self.logger.error(str(e))
            pass 
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.XPATH, download_button))


    def payments_order_file_name(self):
        start =  self.start_of_week()
        end   =  self.end_of_week()
        sd, sy, sm  = start.strftime("%d"), start.strftime("%Y"), start.strftime("%m")
        ed, ey, em  = end.strftime("%d"), end.strftime("%Y"), end.strftime("%m")
        return f'{sy}{sm}{sd}-{ey}{em}{ed}-payments_driver-___.csv'


    def save_report(self):
        if self.sleep:
            time.sleep(self.sleep)
        items = []
        with open(self.payments_order_file_name()) as file:
            reader = csv.reader(file)
            next(reader)  # Advance past the header
            for row in reader:
                if row[3] == "":
                    continue
                if row[3] == None:
                    continue    
                order = UberPaymentsOrder(
                    report_from = self.start_of_week(),
                    report_to = self.end_of_week(),
                    report_file_name = self.payments_order_file_name(),
                    driver_uuid = row[0],
                    first_name = row[1],
                    last_name = row[2],
                    total_amount = row[3],
                    total_clean_amout = row[4] or 0,
                    returns = row[5] or 0,
                    total_amount_cach = row[6] or 0,
                    transfered_to_bank = row[7] or 0,
                    tips = row[8] or 0)

                order.save()
                items.append(order)
        return items

    def wait_opt_code(self):
        r = redis.Redis.from_url(os.environ["REDIS_URL"])
        p = r.pubsub()
        p.subscribe('code')
        p.ping()
        otpa = []
        while True:
            try:
                otp = p.get_message()
                if otp:
                    otpa = list(f'{otp["data"]}')
                    otpa = list(filter(lambda d: d.isdigit() , otpa))
                    digits = [s.isdigit() for s in otpa]
                    if not(digits) or (not all(digits)) or len(digits)!=4:
                        continue
                    break 
            except redis.ConnectionError as e:
                self.logger.error(str(e))
                p = r.pubsub()
                p.subscribe('code')
            time.sleep(1)  
        return otpa 

    def otp_code_v2(self):
        while True:
            if not self.wait_code_form('PHONE_SMS_OTP-0'):
                break
            otp = self.wait_opt_code()
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-0').send_keys(otp[0])
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-1').send_keys(otp[1])
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-2').send_keys(otp[2])
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-3').send_keys(otp[3])
            self.driver.find_element(By.ID, "forward-button").click() 
            break
    
    def wait_code_form(self, id):
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, id)))
            self.driver.find_element(By.ID, id)
            self.driver.get_screenshot_as_file(f'{id}.png')
            return True
        except Exception as e:
            self.logger.error(str(e))
            self.driver.get_screenshot_as_file(f'{id}_error.png')
            return False

    def otp_code_v1(self):
        while True:
            if not self.wait_code_form('verificationCode'):
                break
            otp = self.wait_opt_code()
            self.driver.find_element(By.ID, 'verificationCode').send_keys(otp)
            self.driver.find_element(By.CLASS_NAME,"next-button-wrapper").click()
            break
    
    def force_opt_form(self):
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'alt-PHONE-OTP')))
            el = self.driver.find_element(By.ID, 'alt-PHONE-OTP').click()
        except Exception as e:
            self.logger.error(str(e))
            pass
    
    def password_form(self, id, button, selector):
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, id)))
            el = self.driver.find_element(By.ID, id).send_keys(os.environ["UBER_PASSWORD"])
            self.driver.find_element(selector, button).click()
            self.driver.get_screenshot_as_file('UBER_PASSWORD.png')
        except Exception as e:
            self.logger.error(str(e))

    def login_form(self, id, button, selector):
        element = self.driver.find_element(By.ID, id)
        element.send_keys(os.environ["UBER_NAME"])
        self.driver.find_element(selector, button).click() 
        self.driver.get_screenshot_as_file('UBER_NAME.png')

class Bolt(SeleniumTools):    
    def __init__(self, week_number=None, driver=True, sleep=3, headless=False, base_url="https://fleets.bolt.eu"):
        super().__init__('bolt', week_number=week_number)
        self.sleep = sleep
        if driver:
            self.driver = self.retry(self.build_driver, headless)
            self.base_url = base_url
    
    def quit(self):
        self.driver.quit() 

    def login(self):
        self.driver.get(f"{self.base_url}/login")
        element = self.driver.find_element(By.ID,'username')
        element.send_keys('')
        element.send_keys(os.environ["BOLT_NAME"])
        self.driver.find_element(By.ID, "password").send_keys(os.environ["BOLT_PASSWORD"])
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        if self.sleep:
            time.sleep(self.sleep)

    def download_payments_order(self):
        self.driver.get(f"{self.base_url}/company/58225/reports/weekly/{self.file_patern()}")
    
    def file_patern(self):
        return f"{self.current_date.strftime('%Y')}W{self.week_number()}"
    
    def save_report(self):
        if self.sleep:
            time.sleep(self.sleep)
        items = []
        report = open(self.report_file_name(self.file_patern()))
        
        with report as file:
            reader = csv.reader(file)
            next(reader)
            next(reader)
            for row in reader:
                if row[0] == "":
                    break
                if row[0] == None:
                    break
                order = BoltPaymentsOrder(
                    report_from = self.start_of_week(),
                    report_to = self.end_of_week(),
                    report_file_name = report.name,
                    driver_full_name = row[0],
                    mobile_number = row[1],
                    range_string =  row[2],
                    total_amount = row[3],
                    cancels_amount = row[4],
                    autorization_payment = row[5],
                    autorization_deduction = row[6],
                    additional_fee = row[7],
                    fee = row[8],
                    total_amount_cach = row[9],
                    discount_cash_trips = row[10],
                    driver_bonus = row[11],
                    compensation = row[12] or 0,
                    refunds = row[13],
                    tips =  row[14],
                    weekly_balance = row[15])
                order.save()
                items.append(order)
        return items

from app.models import UklonPaymentsOrder


class Uklon(SeleniumTools):    
    def __init__(self, week_number=None, driver=True, sleep=3, headless=False, base_url="https://partner.uklon.com.ua"):
        super().__init__('uklon',week_number=week_number)
        self.sleep = sleep
        if driver:
            self.driver = self.retry(self.build_driver, headless)
            self.base_url = base_url
    def quit(self):
        self.driver.quit()

    def login(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element("name",'login').send_keys(os.environ["UKLON_NAME"])
        element = self.driver.find_element("name", "loginPassword").send_keys(os.environ["UKLON_PASSWORD"])
        self.driver.find_element("name", "Login").click()
        if self.sleep:
          time.sleep(self.sleep)

    def download_payments_order(self):
        url = f"{self.base_url}/partner/export/fares?page=1&pageSize=20&startDate={self.start_of_week_timestamp()}&endDate={self.end_of_week_timestamp()}&format=csv"
        self.driver.get(url)

    def save_report(self):
        if self.sleep:
            time.sleep(self.sleep)
        items = []
        report = open(self.report_file_name(self.file_patern()))

        with report as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                row = row[0].split('||')
                order = UklonPaymentsOrder(
                                           report_from = self.start_of_week(),
                                           report_to = self.end_of_week(),
                                           report_file_name = file.name,
                                           signal = row[0], 
                                           licence_plate = row[1],
                                           total_rides = row[2],
                                           total_distance = row[3],
                                           total_amount_cach = row[4],
                                           total_amount_cach_less = row[5],
                                           total_amount = row[6],
                                           total_amount_without_comission = row[7],
                                           bonuses = row[8])
                order.save()
                items.append(order)

        return items
    
    def start_of_week_timestamp(self):
        return round(self.start_of_week().timestamp())
    def end_of_week_timestamp(self):
        return round(self.end_of_week().timestamp())
    
    def file_patern(self):
        start =  self.start_of_week()
        end   =  self.end_of_week().end_of('day').add(hours=4)
        sd, sy, sm  = start.strftime("%d"), start.strftime("%Y"), start.strftime("%m")
        ed, ey, em  = end.strftime("%d"), end.strftime("%Y"), end.strftime("%m")    
        return f'{sd}.{sm}.{sy}.+{ed}.{em}.{ey}|{start.strftime("%-m")}_{start.strftime("%-d")}_{sy}.+{end.strftime("%-m")}_{end.strftime("%-d")}_{ey}'
    

def get_report(week_number = None, driver=True, sleep=5, headless=True):
    # drivers_maps = {
    #   "uber": {
    #     "key": "driver_uuid",
    #      "values": ['775f8943-b0ca-4079-90d3-c81d6563d0f1', '9a182345-fd18-490f-a908-94f520a9d2d1', 'cd725b41-9e47-4fd0-8a1f-3514ddf6238a']
    #   },
    #   "bolt": {
    #     "key": "mobile_number",
    #     "values": ['+380661891408', '+380936503350', '+380668914200', '+380502428878', '+380671887096']
    #   },
    #   "uklon": {
    #     "key": "signal",
    #     "values": ['324460', '362612', '372353', '372350', '357339']
    #   },
    #   "drivers": {
    #     'Олександр Холін':   ['775f8943-b0ca-4079-90d3-c81d6563d0f1', '372353', '+380661891408'],
    #     'Анатолій Мухін':    ['9a182345-fd18-490f-a908-94f520a9d2d1', '362612', '+380936503350'],
    #     'Сергій Желамський': ['cd725b41-9e47-4fd0-8a1f-3514ddf6238a', '372350', '+380668914200'],
    #     'Олег Філіппов':     ['d303a6c5-56f7-4ebf-a341-9cfa7c759388', '324460', '+380671887096'],
    #     'Юрій Філіппов':     ['9c7eb6cb-34e8-46a2-b55b-b41657878376', '357339', '+380502428878'],
    #     'Володимир Золотніков': ['368808', '+380669692591'] 
    #   },
    #   "rates": {
    #     'Олександр Холін':   {"uber": 0.50, "bolt": 0.50, "uklon": 0.50},
    #     'Анатолій Мухін':    {"uber": 0.65, "bolt": 0.65, "uklon": 0.35},
    #     'Сергій Желамський': {"uber": 0.50, "bolt": 0.50, "uklon": 0.50},
    #     'Олег Філіппов':     {"uber": 0.60, "bolt": 0.60, "uklon": 0.40},
    #     'Юрій Філіппов':     {"uber": 0.60, "bolt": 0.60, "uklon": 0.40},
    #     'Володимир Золотніков': {"uber": 0.60, "bolt": 0.60, "uklon": 0.40}
    #   }
    # }
    
    u = Uber(week_number=week_number, driver=driver, sleep=sleep, headless=headless)
    if driver:
        u.login_v2()
        u.download_payments_order()
    try:
        ubr = u.save_report()
    except FileNotFoundError:
        u = Uber(week_number=week_number, driver=True, sleep=5, headless=headless)
        u.login_v2()
        u.download_payments_order()
        ubr = u.save_report()

    ub = Uklon(week_number=week_number, driver=driver, sleep=sleep, headless=headless)
    if driver:
        ub.login()
        ub.download_payments_order()

    try:
        ur =  ub.save_report()  
    except TypeError:
        ub = Uklon(week_number=week_number, driver=True, sleep=5, headless=headless)
        ub.login()
        ub.download_payments_order()
        ur =  ub.save_report()  
   

    b = Bolt(week_number=week_number, driver=driver, sleep=sleep, headless=headless)
    if driver:
        b.login()
        b.download_payments_order()

    try:
        br = b.save_report() 
    except TypeError:
        b = Bolt(week_number=week_number, driver=True, sleep=5, headless=headless)
        b.login()
        b.download_payments_order()
        br = b.save_report() 
    
     
    reports = {}
    # for name, ids in drivers_maps["drivers"].items():
    #     reports[name] = itertools.chain(*[
    #         list(filter(lambda p: p.driver_uuid in ids, ubr)),
    #         list(filter(lambda p: p.mobile_number in ids, br)),
    #         list(filter(lambda p: p.signal in ids, ur))
    #      ])
    drivers = Driver.objects.filter(deleted_at=None)
        
    for driver in drivers:
        uber_id = driver.get_driver_external_id('Uber')
        bolt_id = driver.get_driver_external_id('Bolt')
        uklon_id = driver.get_driver_external_id('Uklon')

        reports[driver] = itertools.chain(*[
            [p for p in ubr if p.driver_uuid == uber_id],
            [p for p in br if p.mobile_number == bolt_id],
            [p for p in ur if p.signal == uklon_id]
        ])
    
    totals = {"Fleet Owner": 0, "Owner": ""}
    
    for driver, verndor_report in reports.items():
        verndor_report = list(verndor_report)
        totals[driver.full_name]  = f'Общаяя касса {driver.full_name}: %.2f\n' % sum(vr.kassa() for vr in verndor_report)
        totals[driver.full_name] = '\n'.join(vr.report_text(driver.full_name, driver.get_rate(vr)) for vr in verndor_report)
        totals[driver.full_name] += f'\nЗарплата за неделю {driver.full_name}: %.2f\n' % sum(vr.total_drivers_amount(driver.get_rate(vr)) for vr in verndor_report)
        totals["Fleet Owner"] += sum(vr.total_owner_amount(driver.get_rate(vr)) for vr in verndor_report)
    totals["Fleet Owner"] = f"Fleet Owner: {f'%.2f' % totals['Fleet Owner']}" + '\n\n'

    return '\n'.join(list(totals.values()))
