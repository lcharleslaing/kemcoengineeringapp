from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model"""
    
    list_display = ['title', 'user', 'start_datetime', 'end_datetime', 'location', 'created_at']
    list_filter = ['start_datetime', 'end_datetime', 'user', 'created_at']
    search_fields = ['title', 'description', 'location', 'user__username']
    date_hierarchy = 'start_datetime'
    ordering = ['-start_datetime']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
