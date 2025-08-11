from django.contrib import admin
from .models import RefreshToken
# Register your models here.
@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')