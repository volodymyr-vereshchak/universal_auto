from django.contrib import admin
from .models import Driver, Fleet, Vehicle, Fleets_drivers_vehicles_rate
# Register your models here.
admin.site.register(Driver)
admin.site.register(Fleet)
admin.site.register(Vehicle)
admin.site.register(Fleets_drivers_vehicles_rate)
