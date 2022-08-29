from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import datetime
import pendulum
import sys
import os
import itertools
from app.models import UklonPaymentsOrder
from app.models import UberPaymentsOrder
from app.models import BoltPaymentsOrder
import redis

class SeleniumTools():
    def __init__(self, session):
       self.session_file_name = session

    def remove_session(self):
        os.remove(self.session_file_name)
    
    def retry(self, fun, headless=False):
        print(self.session_file_name)
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
    def __init__(self, driver=True, sleep=3, headless=False):
        super().__init__('uber')
        self.sleep = sleep
        if driver:
            self.driver = self.retry(self.build_driver, headless)

    def quit(self):
        self.driver.quit()
    def login_v2(self):
        self.driver.get("https://drivers.uber.com/")
        element = self.driver.find_element(By.ID, 'PHONE_NUMBER_or_EMAIL_ADDRESS')
        element.send_keys(os.environ["UBER_NAME"])
        self.driver.find_element(By.ID, "forward-button").click() 
        self.driver.get_screenshot_as_file('UBER_NAME.png')   

        # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'password')))
        # self.driver.find_element(By.ID, 'password').send_keys(os.environ["UBER_PASSWORD"])
        # self.driver.find_element(By.CLASS_NAME, "next-button-wrapper").click()
        # self.driver.get_screenshot_as_file('UBER_PASSWORD.png')

        while True:
            #try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'PHONE_SMS_OTP-0')))
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-0')
            self.driver.get_screenshot_as_file('verificationCode.png')
            r = redis.Redis.from_url(os.environ["REDIS_URL"])
            p = r.pubsub()
            p.subscribe('code')
            while True:
                try:
                    otp = p.get_message()
                    print(otp)
                    if otp:
                        print(otp["data"])
                        otpa = list(f'{otp["data"]}')
                        print(otpa)
                        otpa = list(filter(lambda d: d.isdigit() , otpa))
                        digits = [s.isdigit() for s in otpa]
                        if not(digits) or (not all(digits)) or len(digits)!=4:
                            continue
                        break 
                except redis.ConnectionError:
                    p = r.pubsub()
                    p.subscribe(channel)
                time.sleep(1)   
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-0').send_keys(otpa[0])
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-1').send_keys(otpa[1])
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-2').send_keys(otpa[2])
            self.driver.find_element(By.ID, 'PHONE_SMS_OTP-3').send_keys(otpa[3])
            self.driver.find_element(By.ID, "forward-button").click() 
            break
            #except Exception:
            #    self.driver.get_screenshot_as_file('verificationCode_error.png')
            #    break
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'PASSWORD')))
            el = self.driver.find_element(By.ID, 'PASSWORD').send_keys(os.environ["UBER_PASSWORD"])
        except Exception:
            pass

        if self.sleep:
          time.sleep(self.sleep)
    def login(self):
        self.driver.get("https://auth.uber.com/login/")
        element = self.driver.find_element(By.ID, 'useridInput')
        element.send_keys(os.environ["UBER_NAME"])
        self.driver.find_element(By.CLASS_NAME, "next-button-wrapper").click() 
        self.driver.get_screenshot_as_file('UBER_NAME.png')   

        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'password')))
        self.driver.find_element(By.ID, 'password').send_keys(os.environ["UBER_PASSWORD"])
        self.driver.find_element(By.CLASS_NAME, "next-button-wrapper").click()
        self.driver.get_screenshot_as_file('UBER_PASSWORD.png')

        while True:
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'verificationCode')))
                self.driver.find_element(By.ID, 'verificationCode')
                self.driver.get_screenshot_as_file('verificationCode.png')
                r = redis.Redis.from_url(os.environ["REDIS_URL"])
                p = r.pubsub()
                p.subscribe('code')
                while True:
                    try:
                        otp = p.get_message()
                        print(otp)
                        if otp:
                            print(otp["data"])
                            otpa = list(otp)
                            print(otpa)
                            digits = [s.isdigit() for s in otpa]
                            if not(digits) or (not all(digits)) or len(digits)!=4:
                                continue
                            break 
                    except redis.ConnectionError:
                        p = r.pubsub()
                        p.subscribe(channel)
                    time.sleep(1)   
                self.driver.find_element(By.ID, 'verificationCode').send_keys(otp)
                self.driver.find_element(By.CLASS_NAME,"next-button-wrapper").click()
            except Exception:
                self.driver.get_screenshot_as_file('verificationCode_error.png')
                break
            try:
                error_id = 'error-caption'
                self.driver.get_screenshot_as_file('error-caption.png')
                WebDriverWait(self.driver, 2).until_not(EC.presence_of_element_located((By.ID, error_id)))
                break
            except Exception:
                continue

        if self.sleep:
          time.sleep(1000)
    

    def generate_payments_order(self):
        self.driver.get("https://supplier.uber.com/orgs/49dffc54-e8d9-47bd-a1e5-52ce16241cb6/reports")
        if self.sleep:
          time.sleep(self.sleep)
        
        self.driver.get_screenshot_as_file('menu.png')
        
        menu = '//div[@data-testid="report-type-dropdown"]/div/div'
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, menu)))
        self.driver.find_element(By.XPATH, menu).click()   
        
        xpath = '//ul/li/div[text()[contains(.,"Payments Driver")]]'
        try:
          WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
          self.driver.find_element(By.XPATH, xpath).click()
        except Exception:
            xpath = '//ul/li/div[text()[contains(.,"Payments driver")]]'
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        
        
        start = self.driver.find_element(By.XPATH, '//div[@data-testid="start-date-picker"]/div/div/div/input')
        start.send_keys(Keys.NULL)
        self.driver.find_element(By.XPATH, f'//div[@aria-roledescription="button"]/div[text()={self.start_of_week().strftime("%d")}]').click()
        end = self.driver.find_element(By.XPATH, '//div[@data-testid="end-date-picker"]/div/div/div/input')
        end.send_keys(Keys.NULL)
        self.driver.find_element(By.XPATH, f'//div[@aria-roledescription="button"]/div[text()="{self.end_of_week().strftime("%d")}"]').click()
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
        except Exception:
            pass 
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.XPATH, download_button))

    def start_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).start_of('week')

    def end_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).end_of('week')

    def payments_order_file_name(self):
        start =  self.start_of_week()
        end   =  self.end_of_week()
        sd, sy, sm  = start.strftime("%d"), start.strftime("%Y"), start.strftime("%m")
        ed, ey, em  = end.strftime("%d"), end.strftime("%Y"), end.strftime("%m")
        return f'{sy}{sm}{sd}-{ey}{em}{ed}-payments_driver-___.csv'


    def save_report(self):
        #self.download_payments_order()
        if self.sleep:
          time.sleep(self.sleep)
        items = []
        with open(self.payments_order_file_name()) as file:
            reader = csv.reader(file)
            next(reader)  # Advance past the header
            for row in reader:
                print(row)
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
                    tips = row[9] or 0)

                order.save()
                items.append(order)
        return items

class Bolt(SeleniumTools):    
    def __init__(self, driver=True, sleep=3, headless=False):
        super().__init__('bolt')
        self.sleep = sleep
        if driver:
            self.driver = self.retry(self.build_driver, headless)
    
    def quit(self):
        self.driver.quit() 

    def login(self):
        self.driver.get("https://fleets.bolt.eu/login")
        element = self.driver.find_element(By.ID,'username')
        element.send_keys('')
        element.send_keys(os.environ["BOLT_NAME"])
        self.driver.find_element(By.ID, "password").send_keys(os.environ["BOLT_PASSWORD"])
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        if self.sleep:
          time.sleep(self.sleep)

    def download_payments_order(self):
        print(self.payments_order_file_name())
        if os.path.exists(self.payments_order_file_name()):
            return self.payments_order_file_name()
        self.driver.get(f"https://fleets.bolt.eu/company/58225/reports/weekly/2022W{self.week_number()}")
        return self.payments_order_file_name()

    def save_report(self):
        if self.sleep:
          time.sleep(self.sleep)
        items = []
        with open(self.payments_order_file_name()) as file:
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
                    report_file_name = self.payments_order_file_name(),
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
                    weekly_balance = row[15]    )
                order.save()
                items.append(order)
        return items


    def payments_order_file_name(self):
        return f'Щотижневий звіт Bolt – 2022W{self.week_number()} – Kyiv Fleet 03_232 park Universal-auto.csv'
        #return f'Bolt Wochenbericht - 2022W{self.week_number()} - Kyiv Fleet 03_232 park Universal-auto.csv'
        
    def week_number(self):
        return f'{int(self.start_of_week().strftime("%W"))}'

    def start_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).start_of('week')
    def end_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).end_of('week')

from app.models import UklonPaymentsOrder


class Uklon(SeleniumTools):    
    def __init__(self, driver=True, sleep=3, headless=False):
        super().__init__('uklon')
        self.sleep = sleep
        if driver:
            self.driver = self.retry(self.build_driver, headless)
    def quit(self):
        self.driver.quit()

    def login(self):
        self.driver.get("https://partner.uklon.com.ua/")
        element = self.driver.find_element("name",'login').send_keys(os.environ["UKLON_NAME"])
        element = self.driver.find_element("name", "loginPassword").send_keys(os.environ["UKLON_PASSWORD"])
        self.driver.find_element("name", "Login").click()
        if self.sleep:
          time.sleep(self.sleep)

    def download_payments_order(self):
        if os.path.exists(self.payments_order_file_name()):
            return self.payments_order_file_name()
        url = f"https://partner.uklon.com.ua/partner/export/fares?page=1&pageSize=20&startDate={self.start_of_week_timestamp()}&endDate={self.end_of_week_timestamp()}&format=csv"
        print(url)
        print(self.driver.get(url))
        return self.payments_order_file_name()

    def save_report(self):
        if self.sleep:
          time.sleep(self.sleep)
        items = []
        with open(self.payments_order_file_name()) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                row = row[0].split('||')
                order = UklonPaymentsOrder(
                                           report_from = self.start_of_week(),
                                           report_to = self.end_of_week(),
                                           report_file_name = self.payments_order_file_name(),
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
    def start_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).start_of('week')
    def end_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).end_of('week')

    def payments_order_file_name(self):
        start =  self.start_of_week()
        end   =  self.end_of_week().end_of('day').add(hours=4)
        sd, sy, sm  = start.strftime("%d"), start.strftime("%Y"), start.strftime("%-m")
        ed, ey, em  = end.strftime("%d"), end.strftime("%Y"), end.strftime("%-m")
        #Куцко - Income_22.08.2022 3_00_00-29.08.2022 3_00_00.csv
        return f'Куцко - Income_{sm}_{sd}_{sy} 3_00_00 AM-{em}_{ed}_{ey} 3_00_00 AM.csv'

def get_report():
    drivers_maps = {
      "uber": {
        "key": "driver_uuid",
         "values": ['775f8943-b0ca-4079-90d3-c81d6563d0f1', '9a182345-fd18-490f-a908-94f520a9d2d1', 'cd725b41-9e47-4fd0-8a1f-3514ddf6238a']
      },
      "bolt": {
        "key": "mobile_number",
        "values": ['+380661891408', '+380936503350', '+380668914200']
      },
      "uklon": {
        "key": "signal",
        "values": ['324460', '362612']
      },
      "drivers": {
        'Олександр Холін': ['775f8943-b0ca-4079-90d3-c81d6563d0f1', '324460', '+380661891408'],
        'Анатолій Мухін':  ['9a182345-fd18-490f-a908-94f520a9d2d1', '362612', '+380936503350'],
        'Сергій Желамський': ['cd725b41-9e47-4fd0-8a1f-3514ddf6238a', '368808','+380668914200']
      }
    }
    
    
    u = Uber(driver=True, sleep=6, headless=True)
    u.login()
    u.download_payments_order()
    ubr = u.save_report()
 
    ub = Uklon(driver=True, sleep=3, headless=True)
    ub.login()
    ub.download_payments_order()
    ur =  ub.save_report()  

    b = Bolt(driver=True, sleep=6, headless=True)
    b.login()
    b.download_payments_order()
    br = b.save_report()
  
    holin = list(itertools.chain(
        *[list(filter(lambda p: p.driver_uuid in drivers_maps['drivers']['Олександр Холін'], ubr)),
        list(filter(lambda p: p.mobile_number in drivers_maps['drivers']['Олександр Холін'], br)),
        list(filter(lambda p: p.signal in drivers_maps['drivers']['Олександр Холін'], ur))]
        ))
    muxin = list(itertools.chain(
        *[list(filter(lambda p: p.driver_uuid in drivers_maps['drivers']['Анатолій Мухін'], ubr)),
        list(filter(lambda p: p.mobile_number in drivers_maps['drivers']['Анатолій Мухін'], br)),
        list(filter(lambda p: p.signal in drivers_maps['drivers']['Анатолій Мухін'], ur))]
        ))
    zelam = list(itertools.chain(
        *[list(filter(lambda p: p.driver_uuid in drivers_maps['drivers']['Сергій Желамський'], ubr)),
        list(filter(lambda p: p.mobile_number in drivers_maps['drivers']['Сергій Желамський'], br)),
        list(filter(lambda p: p.signal in drivers_maps['drivers']['Сергій Желамський'], ur))]
        ))
    th = '%.2f' % sum(c.total_drivers_amount() for c in holin)
    tm = '%.2f' % sum(c.total_drivers_amount() for c in muxin)
    tz = '%.2f' % sum(c.total_drivers_amount() for c in zelam)

    return """
{hu}
{hb}
{huk}
Зарплата Олександр Холін: {h}
-----------------------------------------
{mu}
{mb}
{muk}
Зарплата Анатолій Мухін: {m}
-----------------------------------------
{zu}
{zb}
{zuk}
Зарплата Сергій Желамський: {z} """.format(
    h=th, m=tm, z=tz, 
    hu=holin[0].report_text(), hb=holin[1].report_text(), huk=holin[2].report_text(),
    mu=muxin[0].report_text(), mb=muxin[1].report_text(), muk=muxin[2].report_text(),
    zu=zelam[0].report_text(), zb=zelam[1].report_text(), zuk=zelam[2].report_text())
