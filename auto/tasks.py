import zoneinfo
from datetime import datetime

from django.conf import settings

from app.models import RawGPS, Vehicle, VehicleGPS, Fleet, Bolt, Driver
from auto.celery import app

BOLT_CHROME_DRIVER = Bolt(driver=True, sleep=3, headless=True)


@app.task
def raw_gps_handler(id):
    try:
        raw = RawGPS.objects.get(id=id)
    except RawGPS.DoesNotExist:
        return f'{RawGPS.DoesNotExist}: id={id}'
    data = raw.data.split(';')
    try:
        vehicle = Vehicle.objects.get(gps_imei=raw.imei)
    except Vehicle.DoesNotExist:
        return f'{Vehicle.DoesNotExist}: gps_imei={raw.imei}'
    try:
        date_time = datetime.strptime(data[0] + data[1], '%d%m%y%H%M%S')
        date_time = date_time.replace(tzinfo=zoneinfo.ZoneInfo(settings.TIME_ZONE))
    except ValueError as err:
        return f'{ValueError} {err}'
    try:
        kwa = {
            'date_time': date_time,
            'vehicle': vehicle,
            'lat': float(data[2]),
            'lat_zone': data[3],
            'lon': float(data[4]),
            'lon_zone': data[5],
            'speed': float(data[6]),
            'course': float(data[7]),
            'height': float(data[8]),
            'raw_data': raw,
        }
    except ValueError as err:
        return f'{ValueError} {err}'
    obj = VehicleGPS.objects.create(**kwa)
    return True


@app.task
def download_weekly_report(fleet_name, missing_weeks):
    weeks = missing_weeks.split(';')
    fleets = Fleet.objects.filter(name=fleet_name, deleted_at=None)
    for fleet in fleets:
        for week_number in weeks:
            fleet.download_weekly_report(week_number=week_number, driver=True, sleep=5, headless=True)


@app.task
def update_driver_status():
    bolt_status = BOLT_CHROME_DRIVER.get_driver_status()
    if bolt_status is not None:
        print(f'Bolt {bolt_status}')
        drivers = Driver.objects.filter(deleted_at=None)

        for driver in drivers:

            current_status = Driver.OFFLINE
            if (driver.name, driver.second_name) in bolt_status['online']:
                current_status = Driver.ACTIVE
            if (driver.name, driver.second_name) in bolt_status['width_client']:
                current_status = Driver.WITH_CLIENT
            if (driver.name, driver.second_name) in bolt_status['wait']:
                current_status = Driver.ACTIVE

            driver.driver_status = current_status

            try:
                driver.save(update_fields=['driver_status'])
            except Exception:
                pass


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, update_driver_status.s())
