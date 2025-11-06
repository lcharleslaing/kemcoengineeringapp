from django.contrib import admin
from .models import Job, ProjectNote, EquipmentNote


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_number', 'customer_name', 'project_name', 'created_at')
    search_fields = ('job_number', 'customer_name', 'project_name')
    ordering = ('job_number',)


@admin.register(ProjectNote)
class ProjectNoteAdmin(admin.ModelAdmin):
    list_display = ('job', 'note_type', 'title', 'created_by', 'created_at')
    list_filter = ('note_type', 'created_at')
    search_fields = ('title', 'content', 'job__job_number')
    ordering = ('-created_at',)


@admin.register(EquipmentNote)
class EquipmentNoteAdmin(admin.ModelAdmin):
    list_display = ('job', 'created_by', 'created_at')
    search_fields = ('job__job_number',)
    ordering = ('-created_at',)
