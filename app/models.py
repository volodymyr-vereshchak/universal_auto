import csv
import datetime
import glob
import os
from django.db import models, IntegrityError
import django


class PaymentsOrder(models.Model):
    transaction_uuid = models.UUIDField()
    driver_uuid = models.UUIDField()
    driver_name = models.CharField(max_length=30)
    driver_second_name = models.CharField(max_length=30)
    trip_uuid = models.CharField(max_length=255)
    trip_description = models.CharField(max_length=50)
    organization_name = models.CharField(max_length=50)
    organization_nickname = models.CharField(max_length=50)
    transaction_time = models.DateTimeField()
    paid_to_you = models.DecimalField(decimal_places=2, max_digits=10)
    your_earnings = models.DecimalField(decimal_places=2, max_digits=10)
    cash = models.DecimalField(decimal_places=2, max_digits=10)
    fare = models.DecimalField(decimal_places=2, max_digits=10)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    fare2 = models.DecimalField(decimal_places=2, max_digits=10)
    service_tax = models.DecimalField(decimal_places=2, max_digits=10)
    wait_time = models.DecimalField(decimal_places=2, max_digits=10)
    out_of_city = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    transfered_to_bank = models.DecimalField(decimal_places=2, max_digits=10)
    ajustment_payment = models.DecimalField(decimal_places=2, max_digits=10)
    cancel_payment = models.DecimalField(decimal_places=2, max_digits=10)


class UklonPaymentsOrder(models.Model):
    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    signal = models.CharField(max_length=8)
    licence_plate = models.CharField(max_length=8)
    total_rides = models.PositiveIntegerField()
    total_distance = models.PositiveIntegerField()
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_cach_less = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_without_comission = models.DecimalField(decimal_places=2, max_digits=10)
    bonuses = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def report_text(self, name = None, rate = 0.35):
        return f'Uklon {name} {self.signal}: Касса({"%.2f" % self.kassa()}) * {"%.0f" % (rate*100)}% = {"%.2f" % (self.kassa() * rate)} - Наличные(-{"%.2f" % float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate = 0.35):
        return -(self.kassa()) * rate

    def vendor(self):
        return 'uklon'

    def total_owner_amount(self, rate=0.35):
        return -self.total_drivers_amount(rate)

    def kassa(self):
        return float(self.total_amount) * 0.81


class BoltPaymentsOrder(models.Model):
    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    driver_full_name = models.CharField(max_length=24)
    mobile_number = models.CharField(max_length=24)
    range_string =  models.CharField(max_length=50)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    cancels_amount = models.DecimalField(decimal_places=2, max_digits=10)
    autorization_payment = models.DecimalField(decimal_places=2, max_digits=10)
    autorization_deduction = models.DecimalField(decimal_places=2, max_digits=10)
    additional_fee = models.DecimalField(decimal_places=2, max_digits=10)
    fee = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)
    discount_cash_trips = models.DecimalField(decimal_places=2, max_digits=10)
    driver_bonus = models.DecimalField(decimal_places=2, max_digits=10)
    compensation = models.DecimalField(decimal_places=2, max_digits=10)
    refunds = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    weekly_balance = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def report_text(self, name=None, rate=0.65):
        name = name or self.driver_full_name
        return f'Bolt {name}: Касса({"%.2f" % self.kassa()}) * {"%.0f" % (rate*100)}% = {"%.2f" % (self.kassa() * rate)} - Наличные({"%.2f" % float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate = 0.65):
        res = self.total_cach_less_drivers_amount() * rate  + float(self.total_amount_cach)
        return res

    def total_cach_less_drivers_amount(self):
        return float(self.total_amount) + float(self.fee) + float(self.cancels_amount) + float(self.driver_bonus)

    def vendor(self):
        return 'bolt'
    
    def kassa(self):
        return (self.total_cach_less_drivers_amount())

    def total_owner_amount(self, rate=0.65):
        return self.total_cach_less_drivers_amount() * (1 - rate) - self.total_drivers_amount(rate)


class UberPaymentsOrder(models.Model):
    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    driver_uuid = models.UUIDField()
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    total_clean_amout = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)
    transfered_to_bank = models.DecimalField(decimal_places=2, max_digits=10)
    returns = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def report_text(self, name=None, rate=0.65):
        name = name or f'{self.first_name} {self.last_name}'
        return f'Uber {name}: Касса({"%.2f" % self.kassa()}) * {"%.0f" % (rate*100)}% = {"%.2f" % (self.kassa() * rate)} - Наличные({float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate = 0.65):
       return float(self.total_amount) * rate + float(self.total_amount_cach)

    def vendor(self):
        return 'uber'

    def total_owner_amount(self, rate=0.65):
        return float(self.total_amount) * (1 - rate) - self.total_drivers_amount(rate)

    def kassa(self):
        return float(self.total_amount)


def save_uber_report_to_db(file_name):
    with open(file_name) as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        for row in reader:
            order = PaymentsOrder(transaction_uuid=row[0],
                                  driver_uuid=row[1],
                                  drievr_name=row[2],
                                  drievr_second_name=row[3],
                                  trip_uuid=row[4],
                                  trip_description=row[5],
                                  organization_name=row[6],
                                  organization_nickname=row[7],
                                  transaction_time=datetime.datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S.%f %z EEST"),
                                  paid_to_you=row[9],
                                  your_earnings=row[10],
                                  cash=row[11],
                                  fare=row[12],
                                  tax=row[13],
                                  fare2=row[14],
                                  service_tax=row[15],
                                  wait_time=row[16],
                                  out_of_city=row[17],
                                  tips=row[18],
                                  transfered_to_bank=row[19],
                                  ajustment_payment=row[20],
                                  cancel_payment=row[21])
            order.save()


TYPE_CHOICES = (
    (0, "driver"),
    (1, "manager"),
    (2, "owner"),
)


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(blank=True, max_length=254)
    phone_number = models.CharField(blank=True, max_length=13)
    chat_id = models.CharField(blank=True, max_length=9)
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    created_at = models.DateTimeField(editable=False, auto_now=datetime.datetime.now())
    deleted_at = models.DateTimeField(blank=True, null=True, editable=True)

    @staticmethod
    def get_by_chat_id(chat_id):
        """
        Returns user by chat_id
        :param chat_id: chat_id by which we need to find the user
        :type chat_id: str
        :return: user object or None if a user with such ID does not exist
        """
        try:
            user = User.objects.get(chat_id=chat_id)
            return user
        except User.DoesNotExist:
            pass


    @staticmethod
    def fill_deleted_at_by_number(number):
        """
        :param number: a number of a user to fill deleted_at
        :type number: str
        """
        user = User.objects.filter(phone_number=number).first()
        user.deleted_at = datetime.datetime.now()
        user.save()
        return user
        
        
class Driver(models.Model):
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def get_driver_external_id(self, vendor:str) -> str:
        if Fleets_drivers_vehicles_rate.objects.filter(fleet__name=vendor, driver=self, deleted_at=None).exists():
            driver_external_id = Fleets_drivers_vehicles_rate.objects.get(fleet__name=vendor, driver=self, deleted_at=None).driver_external_id
        return driver_external_id
    
    def get_rate(self, verndor_rate:str) -> float:
        vendor = verndor_rate.vendor().capitalize()
        if Fleets_drivers_vehicles_rate.objects.filter(fleet__name=vendor, driver=self, deleted_at=None).exists():
            rate = float(Fleets_drivers_vehicles_rate.objects.get(fleet__name=vendor, driver=self, deleted_at=None).rate)
        return rate

    def __str__(self) -> str:
        return f'{self.full_name}'

class Fleet(models.Model):
    name = models.CharField(unique=True, max_length=255)
    fees = models.DecimalField(decimal_places=2, max_digits=3, default=0)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name}'

class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    licence_plate = models.CharField(max_length=24)
    vin_code = models.CharField(max_length=17)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name}'

class Fleets_drivers_vehicles_rate(models.Model):
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver_external_id = models.CharField(max_length=255)
    rate = models.DecimalField(decimal_places=2, max_digits=3, default=0)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.driver_external_id}'

class WeeklyReportFile(models.Model):
    organization_name = models.CharField(max_length=20)
    report_file_name = models.CharField(max_length=255, unique=True)
    report_from = models.CharField(max_length=10)
    report_to = models.CharField(max_length=10)
    file = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def transfer_reports_to_db(self, company_name, report_name, from_date, until_date, header, rows):
        self.organization_name = company_name
        self.report_file_name = report_name
        self.report_from = from_date
        self.report_to = until_date
        self.file = (header + rows)
        self.save()

    # Calculates the number of days in the report
    def check_full_data(self, start, end, file_name):
        start = datetime.strptime(start, '%Y-%m-%d').date()
        end = datetime.strptime(end, '%Y-%m-%d').date()
        difference = end - start
        if difference.days == 7:
            return True
        else:
            print(f"{file_name} include {difference.days} days of the week")
            return False

    # Help separate the date from file name
    def convert_file_name(self, split_symbol, name_list):
        converted_list = []
        for string in name_list:
            string = string.split(split_symbol)
            for part in string:
                converted_list.append(part)
        return converted_list

    def save_weekly_reports_to_db(self):
        path_to_csv_files = '.'
        extension = 'csv'
        os.chdir(path_to_csv_files)
        csv_list = glob.glob('*.{}'.format(extension))
        for file in csv_list:
            rows = []
            try:
                with open(file, 'r') as report:
                    report_name = report.name
                    csvreader = csv.reader(report)
                    header = next(csvreader)
                    for row in csvreader:
                        rows.append(row)

                    # Checks Uber, Uklon and Bolt name in report and report dates; checks the number of days in
                    # the report. If days are less than seven, code issues a warning message and does not
                    # add file to the database.

                    if "payments_driver" in report.name:
                        company_name = "uber"
                        from_date = report.name[0:4] + '-' + report.name[4:6] + '-' + report.name[6:8]
                        until_date = report.name[9:13] + '-' + report.name[13:15] + '-' + report.name[15:17]
                        if self.check_full_data(start=from_date, end=until_date, file_name=report_name):
                            pass
                        else:
                            continue
                        WeeklyReportFile.transfer_reports_to_db(self=WeeklyReportFile(), company_name=company_name,
                                                                report_name=report_name, from_date=from_date,
                                                                until_date=until_date, header=header, rows=rows)

                    elif "Income" in report.name:
                        company_name = "uklon"
                        refactor_file_name = report.name.split(" ")
                        refactor_file_name = [refactor_file_name[2], refactor_file_name[4]]
                        refactor_file_name = self.convert_file_name('-', refactor_file_name)
                        refactor_file_name.pop(1)
                        refactor_file_name = self.convert_file_name('_', refactor_file_name)
                        refactor_file_name.pop(0)

                        # Adds a zero to a single digit
                        for date in refactor_file_name:
                            if len(date) == 1:
                                refactor_file_name[refactor_file_name.index(date)] = "0" + date

                        from_date = str(
                            refactor_file_name[2] + '-' + refactor_file_name[0] + '-' + refactor_file_name[1])
                        until_date = str(
                            refactor_file_name[-1] + '-' + refactor_file_name[-3] + '-' + refactor_file_name[-2])
                        if self.check_full_data(start=from_date, end=until_date, file_name=report_name):
                            pass
                        else:
                            continue
                        WeeklyReportFile.transfer_reports_to_db(self=WeeklyReportFile(), company_name=company_name,
                                                                report_name=report_name, from_date=from_date,
                                                                until_date=until_date, header=header, rows=rows)

                    elif "Bolt" in report.name:
                        company_name = "bolt"
                        bolt_date_report = rows[1][2]
                        from_date = bolt_date_report[8:18]
                        until_date = bolt_date_report[-10:]
                        if self.check_full_data(start=from_date, end=until_date, file_name=report_name):
                            pass
                        else:
                            continue
                        WeeklyReportFile.transfer_reports_to_db(self=WeeklyReportFile(), company_name=company_name,
                                                                report_name=report_name, from_date=from_date,
                                                                until_date=until_date, header=header, rows=rows)
                    else:
                        continue

            # Catches an error if the filename is already exist in DB
            except django.db.utils.IntegrityError as error:
                print(f"{report_name} already exists in Database")


class UberTransactions(models.Model):
    transaction_uuid = models.UUIDField(unique=True)
    driver_uuid = models.UUIDField()
    driver_name = models.CharField(max_length=50)
    driver_second_name = models.CharField(max_length=50)
    trip_uuid = models.UUIDField()
    trip_description = models.CharField(max_length=50)
    organization_name = models.CharField(max_length=50)
    organization_nickname = models.CharField(max_length=50)
    transaction_time = models.CharField(max_length=50)
    paid_to_you = models.DecimalField(decimal_places=2, max_digits=10)
    your_earnings = models.DecimalField(decimal_places=2, max_digits=10)
    cash = models.DecimalField(decimal_places=2, max_digits=10)
    fare = models.DecimalField(decimal_places=2, max_digits=10)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    fare2 = models.DecimalField(decimal_places=2, max_digits=10)
    service_tax = models.DecimalField(decimal_places=2, max_digits=10)
    wait_time = models.DecimalField(decimal_places=2, max_digits=10)
    transfered_to_bank = models.DecimalField(decimal_places=2, max_digits=10)
    peak_rate = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    cancel_payment = models.DecimalField(decimal_places=2, max_digits=10)

    @staticmethod
    def save_transactions_to_db(file_name):
        with open(file_name, 'r', encoding='utf-8') as fl:
            reader = csv.reader(fl)
            next(reader)
            for row in reader:
                try:
                    transaction = UberTransactions(transaction_uuid=row[0],
                                                   driver_uuid=row[1],
                                                   driver_name=row[2],
                                                   driver_second_name=row[3],
                                                   trip_uuid=row[4],
                                                   trip_description=row[5],
                                                   organization_name=row[6],
                                                   organization_nickname=row[7],
                                                   transaction_time=row[8],
                                                   paid_to_you=row[9],
                                                   your_earnings=row[10],
                                                   cash=row[11],
                                                   fare=row[12],
                                                   tax=row[13],
                                                   fare2=row[14],
                                                   service_tax=row[15],
                                                   wait_time=row[16],
                                                   transfered_to_bank=row[17],
                                                   peak_rate=row[18],
                                                   tips=row[19],
                                                   cancel_payment=row[20])
                    transaction.save()
                except IntegrityError:
                    print(f"{row[0]} transaction is already in DB")


class BoltTransactions(models.Model):
    driver_name = models.CharField(max_length=50)
    driver_number = models.CharField(max_length=13)
    trip_date = models.CharField(max_length=50)
    payment_confirmed = models.CharField(max_length=50)
    boarding = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=30)
    requsted_time = models.CharField(max_length=5)
    fare = models.DecimalField(decimal_places=2, max_digits=10)
    payment_authorization = models.DecimalField(decimal_places=2, max_digits=10)
    service_tax = models.DecimalField(decimal_places=2, max_digits=10)
    cancel_payment = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    order_status = models.CharField(max_length=50)
    car = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=30)

    class Meta:
        unique_together = (('driver_name', 'driver_number', 'trip_date', 'payment_confirmed', 'boarding'))

    @staticmethod
    def save_transactions_to_db(file_name):
        with open(file_name, 'r', encoding='utf-8') as fl:
            reader = csv.reader(fl)
            for row in reader:
                if row[17] == "" and row[0] != "" and row[0] != "Ім'я водія":
                    try:
                        transaction = BoltTransactions(driver_name=row[0],
                                                       driver_number=row[1],
                                                       trip_date=row[2],
                                                       payment_confirmed=row[3],
                                                       boarding=row[4],
                                                       payment_method=row[5],
                                                       requsted_time=row[6],
                                                       fare=row[7],
                                                       payment_authorization=row[8],
                                                       service_tax=row[9],
                                                       cancel_payment=row[10],
                                                       tips=row[11],
                                                       order_status=row[12],
                                                       car=row[13],
                                                       license_plate=row[14])
                        transaction.save()
                    except IntegrityError:
                        print(f"Transaction is already in DB")
