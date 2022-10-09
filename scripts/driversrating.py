import pendulum
from django.db.models import Sum, F

from app.models import UberPaymentsOrder, BoltPaymentsOrder, UklonPaymentsOrder


class DriversRatingMixin:

    def get_rating(self):
        start_of_week = pendulum.now().start_of('week').subtract(days=3).start_of('week')
        end_of_week = pendulum.now().start_of('week').subtract(days=3).end_of('week')

        fleets = [
            UberDriversRating(start_of_week, end_of_week),
            BoltDriversRating(start_of_week, end_of_week),
            UklonDriversRating(start_of_week, end_of_week),
        ]
        return [{'fleet': item.fleet_name, 'rating': item.get_rating()} for item in fleets]


class DriversRating:

    fleet_name = ''
    model = None
    grop_by_fields = []
    total_fields = []

    def __init__(self, start_of_week, end_of_week):
        self.start_of_week = start_of_week
        self.end_of_week = end_of_week

    def get_rating(self):
        rating = []
        for i, item in enumerate(self.get_queryset()):
            rating.append(
                {
                    'num': i+1,
                    'driver': self.get_driver(item),
                    'trips': self.get_trips(item),
                    'amount': self.get_amount(item)
                }
            )
        return rating

    def get_driver(self, item): return ''

    def get_trips(self, item): return ''

    def get_amount(self, item):
        return item['total_amount__sum']

    def start_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).start_of('week')

    def end_of_week(self):
        return pendulum.now().start_of('week').subtract(days=3).end_of('week')

    def get_queryset(self):
        qset = self.model.objects\
            .filter(report_from__lte=self.end_of_week, report_to__gte=self.start_of_week)\
            .values(*self.grop_by_fields)\
            .annotate(*self.total_fields)\
            .order_by('-total_amount__sum')
        return qset


class UberDriversRating(DriversRating):

    fleet_name = 'Uber'
    model = UberPaymentsOrder
    grop_by_fields = ['driver_uuid', 'first_name', 'last_name']
    total_fields = [Sum(F('total_amount'))]

    def get_driver(self, item):
        return f"{item['first_name']} {item['last_name']}"


class BoltDriversRating(DriversRating):

    fleet_name = 'Bolt'
    model = BoltPaymentsOrder
    grop_by_fields = ['mobile_number', 'driver_full_name']
    total_fields = [Sum(F('total_amount'))]

    def get_driver(self, item):
        return item['driver_full_name']


class UklonDriversRating(DriversRating):

    fleet_name = 'Uklon'
    model = UklonPaymentsOrder
    grop_by_fields = ['signal', 'licence_plate']
    total_fields = [Sum(F('total_rides')), Sum(F('total_amount'))]

    def get_driver(self, item):
        return item['licence_plate']

    def get_trips(self, item):
        return item['total_rides__sum']

