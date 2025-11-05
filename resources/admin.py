from django.contrib import admin
from .models import Department, Role, Person


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'active_people_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'active_people_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'active_people_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'active_people_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'active_people_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'active_people_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'role', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'department', 'role', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Organization', {
            'fields': ('department', 'role', 'user')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    autocomplete_fields = ['user']
