from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """Sales Design dashboard placeholder"""
    context = {
        'page_title': 'Sales Design',
        'welcome_message': 'Welcome to the Sales Design Dashboard',
    }
    return render(request, 'sales_design/dashboard.html', context)
