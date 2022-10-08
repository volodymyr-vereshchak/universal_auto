from django.contrib import admin
from .models import User


class AdminUser(admin.ModelAdmin):
    list_display = ["id", "email", "phone_number", "type", "created_at"]


admin.site.register(User, AdminUser)
