import csv
from datetime import datetime
import glob
import os
from django.db import models
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

    @staticmethod
    def save_uklon_weekly_report_to_database(file):
        """This function reads the weekly file and packs the data into a database."""
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            row.split('||')
            # date format update
            get_first_date = name_file[15:-25].split(' ')
            first_date = f"{get_first_date[0].replace('_', '-')} {get_first_date[1].replace('_', ':')}"
            report_from = datetime.datetime.strptime(first_date, "%m-%d-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            second_date = name_file[-25:].split('-')[-1][:-7]
            report_to = datetime.datetime.strptime(second_date, "%m_%d_%Y %H_%M_%S").strftime("%Y-%m-%d %H:%M:%S")
            order = UklonPaymentsOrder(
                report_from=f'{report_from}+03:00',
                report_to=f'{report_to}+03:00',
                report_file_name=name_file,
                signal=row[0],
                licence_plate=row[1],
                total_rides=int(row[2]),
                total_distance=int(row[3]),
                total_amount_cach=float(row[4]),
                total_amount_cach_less=float(row[5]),
                total_amount=float(row[6]),
                total_amount_without_comission=float(row[7]),
                bonuses=float(row[8]))

            order.save()

    @staticmethod
    def download_uklon_weekly_file(files: list):
        """ The function checks if the file exists in the directory, if not, it downloads it """
        u = Uklon(week_number=None, driver=True, sleep=3, headless=True)
        name_file_1, name_file_2 = u.payments_order_file_name(), u.payments_order_file_name2()
        if (name_file_1 and name_file_2) not in files:
            u.login()
            u.download_payments_order()


class BoltPaymentsOrder(models.Model):
    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    driver_full_name = models.CharField(max_length=24)
    mobile_number = models.CharField(max_length=13)
    range_string = models.CharField(max_length=50)
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

    def total_drivers_amount(self, rate=0.65):
        res = self.total_cach_less_drivers_amount() * rate + float(self.total_amount_cach)
        return res

    def total_cach_less_drivers_amount(self):
        return float(self.total_amount) + float(self.fee) + float(self.cancels_amount) + float(self.driver_bonus)

    def vendor(self):
        return 'bolt'

    def kassa(self):
        return (self.total_cach_less_drivers_amount())

    def total_owner_amount(self, rate=0.65):
       return self.total_cach_less_drivers_amount() * (1 - rate) - self.total_drivers_amount(rate)

    @staticmethod
    def save_bolt_weekly_report_to_database(file):
        """This function reads the weekly file and packs the data into a database."""
        reader = csv.reader(file, delimiter=',')
        next(reader)
        next(reader)
        for row in reader:
            if row[0] == "":
                break
            if row[0] is None:
                break
            get_date = row[2].split(' ')
            first_datetime = f'{get_date[1]} {datetime.datetime.now().time()}+03:00'
            second_datetime = f'{get_date[-1]} {datetime.datetime.now().time()}+03:00'
            order = BoltPaymentsOrder(
                report_from=first_datetime,
                report_to=second_datetime,
                report_file_name=name_file,
                driver_full_name=row[0],
                mobile_number=row[1][1:],
                range_string=row[2],
                total_amount=float(row[3]),
                cancels_amount=float(row[4]),
                autorization_payment=float(row[5]),
                autorization_deduction=float(row[6]),
                additional_fee=float(row[7]),
                fee=float(row[8]),
                total_amount_cach=float(row[9]),
                discount_cash_trips=float(row[10]),
                driver_bonus=float(row[11]),
                compensation=float(row[12] or 0),
                refunds=float(row[13]),
                tips=float(row[14]),
                weekly_balance=float(row[15]))

            order.save()

    @staticmethod
    def download_bolt_weekly_file(files: list):
        """ The function checks if the file exists in the directory, if not, it downloads it """
        b = Bolt(week_number=None, driver=True, sleep=3, headless=True)
        name_file_1, name_file_2 = b.payments_order_file_name(), b.payments_order_file_name2()
        name_file_3 = b.payments_order_file_name3()
        if (name_file_1 and name_file_2 and name_file_3) not in files:
            b.login()
            b.download_payments_order()


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

    def total_drivers_amount(self, rate=0.65):
       return float(self.total_amount) * rate + float(self.total_amount_cach)

    def vendor(self):
        return 'uber'

    def total_owner_amount(self, rate=0.65):
        return float(self.total_amount) * (1 - rate) - self.total_drivers_amount(rate)

    def kassa(self):
        return float(self.total_amount)

    @staticmethod
    def save_uber_weekly_report_to_database(file):
        """This function reads the weekly file and packs the data into a database."""
        reader = csv.reader(file, delimiter=',')
        next(reader)
        for row in reader:
            get_date = name_file.split('-')
            update_first_date = datetime.datetime.strptime(get_date[0], '%Y%m%d').strftime("%Y-%m-%d")
            update_second_date = datetime.datetime.strptime(get_date[1], '%Y%m%d').strftime("%Y-%m-%d")
            first_datetime = f'{update_first_date} {datetime.datetime.now().time()}+03:00'
            second_datetime = f'{update_second_date} {datetime.datetime.now().time()}+03:00'
            order = UberPaymentsOrder(
                report_from=first_datetime,
                report_to=second_datetime,
                report_file_name=name_file,
                driver_uuid=row[0],
                first_name=row[1],
                last_name=row[2],
                total_amount=float(row[3] or 0),
                total_clean_amout=float(row[4] or 0),
                returns=float(row[5] or 0),
                total_amount_cach=float(row[6] or 0),
                transfered_to_bank=float(row[7] or 0),
                tips=float(row[9] or 0))

            order.save()

    @staticmethod
    def download_uber_weekly_file(files: list):
        """ The function checks if the file exists in the directory, if not, it downloads it """
        u = Uber(week_number=None, driver=True, sleep=5, headless=False)
        name_file = u.payments_order_file_name()
        if name_file not in files:
            u.login_v2()
            u.download_payments_order()
            u.quit()


class FileNameProcessed(models.Model):
    filename_weekly = models.CharField(max_length=70, unique=True)

    @staticmethod
    def save_filename_to_db(processed_files: list):
        for name in processed_files:

            order = FileNameProcessed(
                filename_weekly=name)

            order.save()


def save_uber_report_to_db(file_name):
    with open(file_name) as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        for row in reader:
            order = PaymentsOrder(transaction_uuid=row[0],
                                  driver_uuid=row[1],
                                  driver_name=row[2],
                                  driver_second_name=row[3],
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