from django.contrib import admin
from .models import User


class AdminUser(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "number", "type"]


admin.site.register(User, AdminUser)
