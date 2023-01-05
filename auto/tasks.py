import time
import zoneinfo
from contextlib import contextmanager
from datetime import datetime

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache

from app.models import RawGPS, Vehicle, VehicleGPS, Fleet, Bolt, Driver, NewUklon, Uber
from auto.celery import app
from auto.fleet_synchronizer import BoltSynchronizer, UklonSynchronizer, UberSynchronizer

BOLT_CHROME_DRIVER = None
UKLON_CHROME_DRIVER = None
UBER_CHROME_DRIVER = None

UPDATE_DRIVER_DATA_FREQUENCY = 60*60*3
UPDATE_DRIVER_STATUS_FREQUENCY = 60*5
MEMCASH_LOCK_EXPIRE = 60 * 10
MEMCASH_LOCK_AFTER_FINISHING = 10

logger = get_task_logger(__name__)


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


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + MEMCASH_LOCK_EXPIRE - 3
    status = cache.add(lock_id, oid, MEMCASH_LOCK_EXPIRE)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.set(lock_id, oid, MEMCASH_LOCK_AFTER_FINISHING)


@app.task(bind=True)
def update_driver_status(self):
    with memcache_lock(self.name, self.app.oid) as acquired:
        if acquired:
            bolt_status = BOLT_CHROME_DRIVER.get_driver_status()
            logger.info(f'Bolt {bolt_status}')
            uklon_status = UKLON_CHROME_DRIVER.get_driver_status()
            logger.info(f'Uklon {uklon_status}')
            status_online = set()
            status_width_client = set()
            if bolt_status is not None:
                status_online = status_online.union(set(bolt_status['online']))
                status_width_client = status_width_client.union(set(bolt_status['width_client']))
            if uklon_status is not None:
                status_online = status_online.union(set(uklon_status['online']))
                status_width_client = status_width_client.union(set(uklon_status['width_client']))
            drivers = Driver.objects.filter(deleted_at=None)
            for driver in drivers:
                current_status = Driver.OFFLINE
                if (driver.name, driver.second_name) in status_online:
                    current_status = Driver.ACTIVE
                if (driver.name, driver.second_name) in status_width_client:
                    current_status = Driver.WITH_CLIENT
                # if (driver.name, driver.second_name) in status['wait']:
                #     current_status = Driver.ACTIVE
                driver.driver_status = current_status
                if current_status != Driver.OFFLINE:
                    logger.info(f'{driver}: {current_status}')
                try:
                    driver.save(update_fields=['driver_status'])
                except Exception:
                    pass
        else:
            logger.info('passed')


@app.task(bind=True)
def update_driver_data(self):
    with memcache_lock(self.name, self.app.oid) as acquired:
        if acquired:
            BoltSynchronizer(BOLT_CHROME_DRIVER.driver).synchronize()
            UklonSynchronizer(UKLON_CHROME_DRIVER.driver).synchronize()
            UberSynchronizer(UBER_CHROME_DRIVER.driver).synchronize()

        else:
            logger.info('passed')


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    global BOLT_CHROME_DRIVER
    global UKLON_CHROME_DRIVER
    global UBER_CHROME_DRIVER
    BOLT_CHROME_DRIVER = Bolt(driver=True, sleep=3, headless=True)
    UKLON_CHROME_DRIVER = NewUklon(driver=True, sleep=3, headless=True)
    UBER_CHROME_DRIVER = Uber(driver=True, sleep=3, headless=True)
    sender.add_periodic_task(UPDATE_DRIVER_STATUS_FREQUENCY, update_driver_status.s())
    sender.add_periodic_task(UPDATE_DRIVER_DATA_FREQUENCY, update_driver_data.s())

