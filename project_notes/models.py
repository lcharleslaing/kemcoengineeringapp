from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    """Job - the main connector for all apps. Identified by 5-digit job number"""
    job_number = models.CharField(max_length=10, unique=True, db_index=True)  # e.g., "35371"
    customer_name = models.CharField(max_length=200, blank=True)  # Company name
    project_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['job_number']
    
    def __str__(self):
        return f"Job #{self.job_number} - {self.customer_name or 'No Customer'}"


class ProjectNote(models.Model):
    """General project notes - can be added from any app"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='notes')
    note_type = models.CharField(max_length=50, default='general')  # 'general', 'equipment', 'line_items', etc.
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for Job #{self.job.job_number} - {self.title or 'Untitled'}"


class EquipmentNote(models.Model):
    """Equipment and Line Items notes - created from KOM import"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='equipment_notes')
    equipment_data = models.JSONField(default=dict)  # Store equipment data as JSON
    line_items_data = models.JSONField(default=list)  # Store line items (Item# and Description) as JSON
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Equipment Note for Job #{self.job.job_number}"
