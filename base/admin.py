from django.contrib import admin
from django.utils.html import format_html

from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo_tag', 'role', 'department', 'phone', 'created_at']
    list_filter = ['role', 'department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'photo_tag']

    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                f'<img src="{obj.photo.url}" width="40" style="border-radius: 50px;" />'
            )
        return "Aucune photo"
    
    photo_tag.short_description = 'Photo'
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations professionnelles', {
            'fields': ('role', 'department', 'phone')
        }),
        ('Informations personnelles', {
            'fields': ('photo', 'photo_tag',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    