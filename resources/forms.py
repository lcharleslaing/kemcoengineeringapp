from django import forms
from django.db import models
from django.contrib.auth.models import User
from .models import Department, Role, Person


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'phone', 'department', 'role', 'user', 'notes', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'department': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'role': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'user': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active departments and roles
        try:
            self.fields['department'].queryset = Department.objects.filter(is_active=True)
            self.fields['role'].queryset = Role.objects.filter(is_active=True)
        except (Exception,):
            # Database tables don't exist yet - use empty querysets
            from django.db.models import QuerySet
            self.fields['department'].queryset = Department.objects.none()
            self.fields['role'].queryset = Role.objects.none()
        # Only show users without a person profile (or current user if editing)
        if self.instance and self.instance.pk and self.instance.user_id:
            user_qs = User.objects.filter(
                models.Q(person_profile__isnull=True) | models.Q(pk=self.instance.user_id)
            )
        else:
            user_qs = User.objects.filter(person_profile__isnull=True)
        self.fields['user'].queryset = user_qs.order_by('username')
        # Make user field optional
        self.fields['user'].required = False

