import pytest
from dataclasses import dataclass

from app.models import UberFleet, Driver, Vehicle, Fleets_drivers_vehicles_rate, DriverRateLevels, SeleniumTools, \
    UberPaymentsOrder


@dataclass(frozen=True)
class Seed:
    fleet: UberFleet
    driver: Driver
    vehicle: Vehicle


@pytest.fixture(scope='session')
def populate_db(django_db_setup, django_db_blocker) -> Seed:

    with django_db_blocker.unblock():
        f = UberFleet.objects.create(name='Uber', min_fee=3000)
        d = Driver.objects.create(name='DriverName', second_name='DriverSecondName')
        v = Vehicle.objects.create(licence_plate='KA4897BM', vin_code='VF1KZ140652639946', name='2015 Renault Megane'
                                   , gps_imei='357073298728193')
        Fleets_drivers_vehicles_rate.objects.create(fleet=f, driver=d, vehicle=v,
                                                    driver_external_id='775f8943-b0ca-4079-90d3-c81d6563d0f1', rate=0.5)
        DriverRateLevels.objects.create(fleet=f, threshold_value=5000, rate_delta=-0.05)
        st = SeleniumTools(session='', week_number='2022-11-18')
        UberPaymentsOrder.objects.create(report_from=st.start_of_week(), report_to=st.end_of_week(), report_file_name='',
                                         driver_uuid='775f8943-b0ca-4079-90d3-c81d6563d0f1', first_name='',
                                         last_name='', total_amount=4500, total_clean_amout=0, total_amount_cach=0,
                                         transfered_to_bank=0, returns=0, tips=0)
    return Seed(fleet=f, driver=d, vehicle=v)

