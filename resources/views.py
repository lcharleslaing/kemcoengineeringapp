from functools import wraps
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Department, Role, Person
from .forms import DepartmentForm, RoleForm, PersonForm


# Permission check decorator
def admin_required(view_func):
    """Decorator to ensure only superusers can access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_superuser:
            raise PermissionDenied("Only administrators can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


# Department Views
@admin_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.all().order_by('name')
    context = {
        'departments': departments,
        'page_title': 'Departments'
    }
    return render(request, 'resources/department_list.html', context)


@admin_required
def department_detail(request, pk):
    """View department details"""
    department = get_object_or_404(Department, pk=pk)
    people = department.people.filter(is_active=True).order_by('last_name', 'first_name')
    context = {
        'department': department,
        'people': people,
        'page_title': f'Department: {department.name}'
    }
    return render(request, 'resources/department_detail.html', context)


@admin_required
def department_create(request):
    """Create a new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department "{department.name}" created successfully.')
            return redirect('resources:department_detail', pk=department.pk)
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'page_title': 'Create Department',
        'form_action': 'Create'
    }
    return render(request, 'resources/department_form.html', context)


@admin_required
def department_update(request, pk):
    """Update a department"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department "{department.name}" updated successfully.')
            return redirect('resources:department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
        'page_title': f'Edit Department: {department.name}',
        'form_action': 'Update'
    }
    return render(request, 'resources/department_form.html', context)


@admin_required
def department_delete(request, pk):
    """Delete a department"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'Department "{name}" deleted successfully.')
        return redirect('resources:department_list')
    
    context = {
        'department': department,
        'page_title': f'Delete Department: {department.name}'
    }
    return render(request, 'resources/department_confirm_delete.html', context)


# Role Views
@admin_required
def role_list(request):
    """List all roles"""
    roles = Role.objects.all().order_by('name')
    context = {
        'roles': roles,
        'page_title': 'Roles'
    }
    return render(request, 'resources/role_list.html', context)


@admin_required
def role_detail(request, pk):
    """View role details"""
    role = get_object_or_404(Role, pk=pk)
    people = role.people.filter(is_active=True).order_by('last_name', 'first_name')
    context = {
        'role': role,
        'people': people,
        'page_title': f'Role: {role.name}'
    }
    return render(request, 'resources/role_detail.html', context)


@admin_required
def role_create(request):
    """Create a new role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, f'Role "{role.name}" created successfully.')
            return redirect('resources:role_detail', pk=role.pk)
    else:
        form = RoleForm()
    
    context = {
        'form': form,
        'page_title': 'Create Role',
        'form_action': 'Create'
    }
    return render(request, 'resources/role_form.html', context)


@admin_required
def role_update(request, pk):
    """Update a role"""
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save()
            messages.success(request, f'Role "{role.name}" updated successfully.')
            return redirect('resources:role_detail', pk=role.pk)
    else:
        form = RoleForm(instance=role)
    
    context = {
        'form': form,
        'role': role,
        'page_title': f'Edit Role: {role.name}',
        'form_action': 'Update'
    }
    return render(request, 'resources/role_form.html', context)


@admin_required
def role_delete(request, pk):
    """Delete a role"""
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        name = role.name
        role.delete()
        messages.success(request, f'Role "{name}" deleted successfully.')
        return redirect('resources:role_list')
    
    context = {
        'role': role,
        'page_title': f'Delete Role: {role.name}'
    }
    return render(request, 'resources/role_confirm_delete.html', context)


# Person Views
@admin_required
def person_list(request):
    """List all people"""
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    role_filter = request.GET.get('role', '')
    
    people = Person.objects.all()
    
    if search_query:
        people = people.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if department_filter:
        people = people.filter(department_id=department_filter)
    
    if role_filter:
        people = people.filter(role_id=role_filter)
    
    people = people.order_by('last_name', 'first_name')
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    roles = Role.objects.filter(is_active=True).order_by('name')
    
    context = {
        'people': people,
        'departments': departments,
        'roles': roles,
        'search_query': search_query,
        'department_filter': department_filter,
        'role_filter': role_filter,
        'page_title': 'People'
    }
    return render(request, 'resources/person_list.html', context)


@admin_required
def person_detail(request, pk):
    """View person details"""
    person = get_object_or_404(Person, pk=pk)
    context = {
        'person': person,
        'page_title': f'Person: {person.full_name}'
    }
    return render(request, 'resources/person_detail.html', context)


@admin_required
def person_create(request):
    """Create a new person"""
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save()
            messages.success(request, f'Person "{person.full_name}" created successfully.')
            return redirect('resources:person_detail', pk=person.pk)
    else:
        # Pre-fill department or role from query parameters
        initial = {}
        if 'department' in request.GET:
            try:
                initial['department'] = int(request.GET.get('department'))
            except (ValueError, TypeError):
                pass
        if 'role' in request.GET:
            try:
                initial['role'] = int(request.GET.get('role'))
            except (ValueError, TypeError):
                pass
        form = PersonForm(initial=initial)
    
    context = {
        'form': form,
        'page_title': 'Create Person',
        'form_action': 'Create'
    }
    return render(request, 'resources/person_form.html', context)


@admin_required
def person_update(request, pk):
    """Update a person"""
    person = get_object_or_404(Person, pk=pk)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            person = form.save()
            messages.success(request, f'Person "{person.full_name}" updated successfully.')
            return redirect('resources:person_detail', pk=person.pk)
    else:
        form = PersonForm(instance=person)
    
    context = {
        'form': form,
        'person': person,
        'page_title': f'Edit Person: {person.full_name}',
        'form_action': 'Update'
    }
    return render(request, 'resources/person_form.html', context)


@admin_required
def person_delete(request, pk):
    """Delete a person"""
    person = get_object_or_404(Person, pk=pk)
    if request.method == 'POST':
        name = person.full_name
        person.delete()
        messages.success(request, f'Person "{name}" deleted successfully.')
        return redirect('resources:person_list')
    
    context = {
        'person': person,
        'page_title': f'Delete Person: {person.full_name}'
    }
    return render(request, 'resources/person_confirm_delete.html', context)


# Dashboard View
@admin_required
def resources_dashboard(request):
    """Resources app dashboard"""
    try:
        departments_count = Department.objects.filter(is_active=True).count()
        roles_count = Role.objects.filter(is_active=True).count()
        people_count = Person.objects.filter(is_active=True).count()
        
        recent_departments = Department.objects.all().order_by('-created_at')[:5]
        recent_roles = Role.objects.all().order_by('-created_at')[:5]
        recent_people = Person.objects.all().order_by('-created_at')[:5]
    except (OperationalError, ProgrammingError):
        # Database tables don't exist yet - migrations not run
        departments_count = 0
        roles_count = 0
        people_count = 0
        recent_departments = []
        recent_roles = []
        recent_people = []
        messages.warning(request, 'Database tables not found. Please run migrations: python manage.py makemigrations resources && python manage.py migrate')
    
    context = {
        'departments_count': departments_count,
        'roles_count': roles_count,
        'people_count': people_count,
        'recent_departments': recent_departments,
        'recent_roles': recent_roles,
        'recent_people': recent_people,
        'page_title': 'Resources Dashboard'
    }
    return render(request, 'resources/dashboard.html', context)
