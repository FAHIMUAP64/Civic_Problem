from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register Custom User Model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass