from django.contrib import admin

class AdminUser(admin.ModelAdmin):
    list_display = ["id", "email", "phone_number", "type", "created_at"]

from .models import Driver, Fleet, Vehicle, Fleets_drivers_vehicles_rate User
admin.site.register(User, AdminUser)
admin.site.register(Driver)
admin.site.register(Fleet)
admin.site.register(Vehicle)
admin.site.register(Fleets_drivers_vehicles_rate)
