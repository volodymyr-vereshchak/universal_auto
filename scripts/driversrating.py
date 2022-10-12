from app.libs.selenium_tools import SeleniumTools
from app.models import UberPaymentsOrder, BoltPaymentsOrder, UklonPaymentsOrder


class DriversRatingMixin:

    def get_rating(self, start=None, end=None):
        st = SeleniumTools(session='')
        if not start:
            start = st.start_of_week()
        if not end:
            end = st.end_of_week()

        # st = SeleniumTools(session='', week_number='2022-09-19')

        fleets = [
            UberDriversRating(start, end),
            BoltDriversRating(start, end),
            UklonDriversRating(start, end),
        ]
        r = [{'fleet': item.fleet_name, 'rating': item.get_rating()} for item in fleets]
        for x in r:
            for period in x['rating']:
                for detail in period['rating']:
                    f=1
        return [{'fleet': item.fleet_name, 'rating': item.get_rating()} for item in fleets]


class DriversRating:

    fleet_name = ''
    model = None

    def __init__(self, start_of_week, end_of_week):
        self.start_of_week = start_of_week
        self.end_of_week = end_of_week

    def get_rating(self):

        qset = self.model.objects.filter(report_from__lte=self.end_of_week, report_to__gte=self.start_of_week).order_by('report_from')
        dct = {}

        # Group by periods and drivers
        for item in qset:
            period_key = (item.report_from, item.report_to)
            period = dct.get(period_key)
            if not period:
                dct[period_key] = {}
                period = dct[period_key]
            drv = period.get(self.get_driver_identifier(item))
            if not drv:
                period[self.get_driver_identifier(item)] = {'driver': self.get_driver(item), 'trips': 0, 'amount': 0}
                drv = period[self.get_driver_identifier(item)]
            drv['trips'] = drv['trips'] + self.get_trips(item)
            drv['amount'] = drv['amount'] + item.kassa()

        # Sorting and converting to a list
        for k, period in dct.items():
            dct[k] = {'start': k[0], 'end': k[1], 'rating': sorted(list(period.values()), key=lambda item: item['amount'], reverse=True)}

        rating = list(dct.values())

        # Numerating
        for i in range(len(rating)):
            for j in range(len(rating[i]['rating'])):
                rating[i]['rating'][j]['num'] = j + 1

        return rating

    def get_driver(self, item): return ''

    def get_trips(self, item): return 0

    def get_driver_identifier(self, item): return ''


class UberDriversRating(DriversRating):

    fleet_name = 'Uber'
    model = UberPaymentsOrder

    def get_driver(self, item):
        return f"{item.first_name} {item.last_name}"

    def get_driver_identifier(self, item):
        return item.driver_uuid


class BoltDriversRating(DriversRating):

    fleet_name = 'Bolt'
    model = BoltPaymentsOrder

    def get_driver(self, item):
        return item.driver_full_name

    def get_driver_identifier(self, item):
        return item.mobile_number


class UklonDriversRating(DriversRating):

    fleet_name = 'Uklon'
    model = UklonPaymentsOrder

    def get_driver(self, item):
        return item.licence_plate

    def get_trips(self, item):
        return item.total_rides

    def get_driver_identifier(self, item):
        return item.signal
