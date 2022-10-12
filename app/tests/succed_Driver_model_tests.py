# from django.test import TestCase
import pytest
from app.models import Driver, Fleet, Vehicle, Fleets_drivers_vehicles_rate


# Check write data to Driver model
@pytest.mark.django_db
@pytest.mark.parametrize('full_name', ['Олександр Холін', 'Анатолій Мухін',
                              'Сергій Желамський', 'Олег Філіппов',
                              'Юрій Філіппов', 'Володимир Золотніков'])
def test_drivers_create(full_name):

    driver = Driver.objects.create(full_name=full_name)
    assert driver.full_name == full_name
    assert Driver.objects.count() == 1

# Check write data to Fleet model
@pytest.mark.django_db
@pytest.mark.parametrize('fleet_name, fees',[("Uber", 0.50),
                                             ("Bolt", 0.50),
                                             ("Uklon", 0.50)])
def test_fleets_create(fleet_name, fees):
    fleet = Fleet.objects.create(name=fleet_name, fees=fees)
    assert fleet.name == fleet_name
    assert fleet.fees == fees
    assert Fleet.objects.count() == 1

# Check write data to Vehicle model
@pytest.mark.django_db
@pytest.mark.parametrize('name, licence_plate, vin_code',
                         [('Lamborgini', 'АА 0880 ВР', 'JH4DA9340LS003571'),
                          ('Acura', 'АА 1881 ВР', 'JH4CC2642RC001364'),
                          ('Chevrolet', 'АА 2882 ВР', '1GNDS13S132266223'),
                          ('Cadillac', 'АА 3883 ВР', '1G6CD6988G4334344'),
                          ('Audi', 'АА 4885 ВР', 'WAULFAFR3DA006959'),
                          ('Chrysler', 'АА 5885 ВР', '3C8FY68B72T322831')])
def test_vehicles_create(name, licence_plate, vin_code):
    vehicle = Vehicle.objects.create(name=name,
                                     licence_plate=licence_plate,
                                     vin_code=vin_code)
    assert vehicle.name == name
    assert vehicle.licence_plate == licence_plate
    assert vehicle.vin_code == vin_code
    assert Vehicle.objects.count() == 1

# Check write data to Fleets_drivers_vehicles_rate model
@pytest.mark.django_db
@pytest.mark.parametrize('fleet_name, full_name, vehicle, driver_external_id, rate',
                [('Uber', 'Олександр Холін', 'Lamborgini', '775f8943-b0ca-4079-90d3-c81d6563d0f1', '0.50'),
                 ('Bolt', 'Олександр Холін', 'Lamborgini', '+380661891408', '0.50'),
                 ('Uklon', 'Олександр Холін', 'Lamborgini', '372353', '0.50'),
                 ('Uber', 'Анатолій Мухін', 'Lamborgini', '9a182345-fd18-490f-a908-94f520a9d2d1', '0.65'),
                 ('Bolt', 'Анатолій Мухін', 'Lamborgini', '+380936503350', '0.65'),
                 ('Uklon', 'Анатолій Мухін', 'Lamborgini', '362612', '0.35')])
def test_fleets_drivers_vehicles_rate_create(fleet_name, full_name, vehicle, driver_external_id, rate):
    if Fleet.objects.filter(name=fleet_name, fees='0.50').exists():
        fleet=Fleet.objects.get(name=fleet_name, fees='0.50')
    else:
        fleet=Fleet.objects.create(name=fleet_name, fees='0.50')
    if Driver.objects.filter(full_name=full_name).exists():
        driver=Driver.objects.get(full_name=full_name)
    else:
        driver=Driver.objects.create(full_name=full_name)
    if Vehicle.objects.filter(name=vehicle).exists():
        vehicle=Vehicle.objects.get(
            name=vehicle,
            licence_plate='АА 0880 ВР',
            vin_code='JH4DA9340LS003571')
    else:
        vehicle=Vehicle.objects.create(
            name=vehicle,
            licence_plate='АА 0880 ВР',
            vin_code='JH4DA9340LS003571')

    fleets_drivers_vehicles = Fleets_drivers_vehicles_rate.objects.create(
        fleet=fleet,
        driver=driver,
        vehicle=vehicle,
        driver_external_id=driver_external_id,
        rate=rate)

    assert fleets_drivers_vehicles.fleet == fleet
    assert fleets_drivers_vehicles.driver == driver
    assert fleets_drivers_vehicles.vehicle == vehicle
    assert fleets_drivers_vehicles.driver_external_id == driver_external_id
    assert fleets_drivers_vehicles.rate == rate
    assert Fleets_drivers_vehicles_rate.objects.count() == 1

# Checks get_driver_external_id() from Driver model:
@pytest.mark.django_db
@pytest.mark.parametrize("full_name, vendor, id",
                         [('Олександр Холін', 'Uber', '775f8943-b0ca-4079-90d3-c81d6563d0f1'), 
                          ('Олександр Холін', 'Bolt', '+380661891408'),
                          ('Олександр Холін', 'Uklon', '372353')])
def test_get_driver_external_id(full_name, vendor, id):
    if Driver.objects.filter(full_name=full_name).exists():
        driver=Driver.objects.get(full_name=full_name)
        driver.get_driver_external_id(vendor) == id

# Checks get_rate() from Driver model:
@pytest.mark.django_db
@pytest.mark.parametrize("full_name, vendor, rate",
                         [('Олександр Холін', 'Uber', '0.50'), 
                          ('Олександр Холін', 'Bolt', '0.50'),
                          ('Олександр Холін', 'Uklon', '0.50')])
def test_get_rate(full_name, vendor, rate):
    if Driver.objects.filter(full_name=full_name).exists():
        driver=Driver.objects.get(full_name=full_name)
        driver.get_rate(vendor) == rate
