from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Department(models.Model):
    """Represents an organizational department"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this department")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('resources:department_detail', kwargs={'pk': self.pk})
    
    @property
    def active_people_count(self):
        """Count of active people in this department"""
        return self.people.filter(is_active=True).count()


class Role(models.Model):
    """Represents a role/position within the organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this role")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('resources:role_detail', kwargs={'pk': self.pk})
    
    @property
    def active_people_count(self):
        """Count of active people with this role"""
        return self.people.filter(is_active=True).count()


class Person(models.Model):
    """Represents a person/resource within the organization"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people',
        help_text="Department this person belongs to"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people',
        help_text="Role/position of this person"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='person_profile',
        help_text="Link to Django user account (optional)"
    )
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this person")
    notes = models.TextField(blank=True, help_text="Additional notes about this person")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Person"
        verbose_name_plural = "People"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('resources:person_detail', kwargs={'pk': self.pk})
    
    def get_display_name(self):
        """Return display name with department and role"""
        parts = [self.full_name]
        if self.department:
            parts.append(f"({self.department.name})")
        if self.role:
            parts.append(f"- {self.role.name}")
        return " ".join(parts)
