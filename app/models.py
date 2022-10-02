from django.db import models

class PaymentsOrder(models.Model):
    transaction_uuid = models.UUIDField()
    driver_uuid = models.UUIDField()
    driver_name = models.CharField(max_length=30)
    driver_second_name = models.CharField(max_length=30)
    trip_uuid = models.CharField(max_length=255)
    trip_description = models.CharField(max_length=50)
    organization_name =  models.CharField(max_length=50)
    organization_nickname = models.CharField(max_length=50)
    transaction_time =  models.DateTimeField()
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
    total_amount =  models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_without_comission = models.DecimalField(decimal_places=2, max_digits=10)
    bonuses = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def report_text(self, name = None, rate = 0.35):
        return f'Uklon {name} {self.signal}: Аренда авто: {"%.2f" % self.total_drivers_amount(rate)}'
    def total_drivers_amount(self, rate = 0.35):
        return -(float(self.total_amount) * 0.83) * rate
    def vendor(self):
        return 'uklon'
    def total_owner_amount(self, rate = 0.35):
        return -self.total_drivers_amount(rate)
       
class BoltPaymentsOrder(models.Model):
    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    driver_full_name = models.CharField(max_length=24)
    mobile_number = models.CharField(max_length=12)
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
    def report_text(self, name = None, rate = 0.65):
        name = name or self.driver_full_name
        return f'Bolt {name}: Безналичные: {self.total_cach_less_drivers_amount()}, Наличные: {float(self.total_amount_cach)}, Зарплата: {"%.2f" % self.total_drivers_amount(rate)}'
    def total_drivers_amount(self, rate = 0.65):
        res = self.total_cach_less_drivers_amount() * rate  + float(self.total_amount_cach)
        return res

    def total_cach_less_drivers_amount(self):
        return float(self.total_amount) + float(self.fee) + float(self.cancels_amount) + float(self.driver_bonus)
    
    def vendor(self):
        return 'bolt'

    def total_owner_amount(self, rate = 0.65):
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
    def report_text(self, name = None, rate = 0.65):
        name = name or f'{self.first_name} {self.last_name}'
        return f'Uber {name}: Безналичные: {float(self.total_amount)}, Наличные: {float(self.total_amount_cach)}, Зарплата: {"%.2f" % self.total_drivers_amount(rate)}'
    def total_drivers_amount(self, rate = 0.65):
       return float(self.total_amount) * rate + float(self.total_amount_cach)

    def vendor(self):
        return 'uber'

    def total_owner_amount(self, rate = 0.65):
       return float(self.total_amount) * (1 - rate) - self.total_drivers_amount(rate)

def save_uber_report_to_db(file_name):
    with open(file_name) as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        for row in reader:
            order = PaymentsOrder(transaction_uuid = row[0],
                                 driver_uuid = row[1],
                                 drievr_name = row[2],
                                 drievr_second_name = row[3],
                                 trip_uuid = row[4],
                                 trip_description = row[5],
                                 organization_name = row[6],
                                 organization_nickname = row[7],
                                 transaction_time = datetime.datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S.%f %z EEST"),
                                 paid_to_you = row[9],
                                 your_earnings = row[10],
                                 cash = row[11],
                                 fare = row[12],
                                 tax = row[13],
                                 fare2 = row[14],
                                 service_tax = row[15],
                                 wait_time = row[16],
                                 out_of_city = row[17],
                                 tips = row[18],
                                 transfered_to_bank = row[19],
                                 ajustment_payment =row[20],
                                 cancel_payment = row[21])
            order.save()




