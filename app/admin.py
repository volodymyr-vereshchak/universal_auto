from django.contrib import admin
from .models import Fleet, UberFleet, BoltFleet, UklonFleet
from .models import Driver, Vehicle, Fleets_drivers_vehicles_rate, User, DriverStatus
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter


class FleetChildAdmin(PolymorphicChildModelAdmin):
    base_model = Fleet 
    show_in_index = False
@admin.register(UberFleet)
class UberFleetAdmin(FleetChildAdmin):
    base_model = UberFleet
    show_in_index = False
@admin.register(BoltFleet)
class BoltFleetAdmin(FleetChildAdmin):
    base_model = BoltFleet
    show_in_index = False
@admin.register(UklonFleet)
class UklonFleetAdmin(FleetChildAdmin):
    base_model = UklonFleet
    show_in_index = False

@admin.register(Fleet)
class FleetParentAdmin(PolymorphicParentModelAdmin):
    base_model = Fleet 
    child_models = (UberFleet, BoltFleet, UklonFleet,)
    list_filter = (PolymorphicChildModelFilter,)
    

admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(DriverStatus)
admin.site.register(Fleets_drivers_vehicles_rate)

    # drivers_maps = {
    #   "uber": {
    #     "key": "driver_uuid",
    #      "values": ['775f8943-b0ca-4079-90d3-c81d6563d0f1', '9a182345-fd18-490f-a908-94f520a9d2d1', 'cd725b41-9e47-4fd0-8a1f-3514ddf6238a']
    #   },
    #   "bolt": {
    #     "key": "mobile_number",
    #     "values": ['+380661891408', '+380936503350', '+380668914200', '+380502428878', '+380671887096']
    #   },
    #   "uklon": {
    #     "key": "signal",
    #     "values": ['324460', '362612', '372353', '372350', '357339']
    #   },
    #   "drivers": {
    #     'Олександр Холін':   ['775f8943-b0ca-4079-90d3-c81d6563d0f1', '372353', '+380661891408'],
    #     'Анатолій Мухін':    ['9a182345-fd18-490f-a908-94f520a9d2d1', '362612', '+380936503350'],
    #     'Сергій Желамський': ['cd725b41-9e47-4fd0-8a1f-3514ddf6238a', '372350', '+380668914200'],
    #     'Олег Філіппов':     ['d303a6c5-56f7-4ebf-a341-9cfa7c759388', '324460', '+380671887096'],
    #     'Юрій Філіппов':     ['9c7eb6cb-34e8-46a2-b55b-b41657878376', '357339', '+380502428878'],
    #     'Володимир Золотніков': ['368808', '+380669692591'] 
    #   },
    #   "rates": {
    #     'Олександр Холін':   {"uber": 0.50, "bolt": 0.50, "uklon": 0.50},
    #     'Анатолій Мухін':    {"uber": 0.65, "bolt": 0.65, "uklon": 0.35},
    #     'Сергій Желамський': {"uber": 0.50, "bolt": 0.50, "uklon": 0.50},
    #     'Олег Філіппов':     {"uber": 0.60, "bolt": 0.60, "uklon": 0.40},
    #     'Юрій Філіппов':     {"uber": 0.60, "bolt": 0.60, "uklon": 0.40},
    #     'Володимир Золотніков': {"uber": 0.60, "bolt": 0.60, "uklon": 0.40}
    #   }
    # }