from django.contrib import admin
from .models import Notification, ExpoPushToken

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('title', 'message', 'created_at', 'is_read')
	search_fields = ('title', 'message')
	readonly_fields = ('created_at',)

@admin.register(ExpoPushToken)
class ExpoPushTokenAdmin(admin.ModelAdmin):
	list_display = ('token', 'created_at', 'updated_at')
	search_fields = ('token',)
