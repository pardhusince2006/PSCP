from django.contrib import admin
from .models import Notification, Team


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'message', 'status', 'notification_type', 'created_at')
    list_filter = ('status', 'notification_type', 'created_at')
    search_fields = ('user__username', 'project__title', 'message')
    readonly_fields = ('created_at',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('project', 'created_by', 'status', 'created_at','get_members')  # Columns to display in the admin list view
    list_filter = ('status', 'created_at')  # Add filters for easier navigation
    search_fields = ('project__title', 'created_by__username')  # Enable search by project title or creator username
    filter_horizontal = ('members',)  # For Many-to-Many fields like members



    def get_members(self, obj):
        # Display all members of the team as a comma-separated list
        return ", ".join([member.get_full_name() for member in obj.members.all()])
    get_members.short_description = "Team Members"