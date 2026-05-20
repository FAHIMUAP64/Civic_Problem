from django.contrib import admin
from .models import Complaint, Notification


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ['id', 'title', 'category', 'status', 'deadline', 'created_by', 'is_overdue_display']
    list_filter   = ['status', 'category']
    search_fields = ['title', 'description']
    ordering      = ['-id']

    def is_overdue_display(self, obj):
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = 'Overdue?'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'complaint', 'is_read', 'created_at']
    list_filter   = ['is_read']
    ordering      = ['-created_at']
