from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
import os
import tempfile

from .models import KOMForm, KOMLineItem, KOMEquipmentRequired
from .utils import parse_kom_excel


def admin_required(view_func):
    """Decorator to ensure only superusers can access"""
    from functools import wraps
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_superuser:
            raise PermissionDenied("Only administrators can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def kom_list(request):
    """List all KOM forms"""
    kom_forms = KOMForm.objects.all().order_by('-proposal_date', '-created_at')
    return render(request, 'customer/kom_list.html', {'kom_forms': kom_forms})


@admin_required
def kom_detail(request, pk):
    """View a single KOM form with all fields"""
    kom_form = get_object_or_404(KOMForm, pk=pk)
    return render(request, 'customer/kom_detail.html', {'kom': kom_form})


@admin_required
def kom_import(request):
    """Import KOM Excel file"""
    if request.method == 'POST':
        if 'kom_file' not in request.FILES:
            messages.error(request, 'No file uploaded.')
            return redirect('customer:kom_import')
        
        uploaded_file = request.FILES['kom_file']
        
        # Validate file extension
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload an Excel file (.xlsx or .xls)')
            return redirect('customer:kom_import')
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        try:
            # Parse the Excel file
            parsed_data = parse_kom_excel(tmp_path)
            
            # Create KOMForm instance
            with transaction.atomic():
                kom_form = KOMForm.objects.create(
                    created_by=request.user,
                    source_file=uploaded_file.name,
                    **{k: v for k, v in parsed_data.items() if k not in ['line_items', 'equipment_required']}
                )
                
                # Create line items
                for item_data in parsed_data.get('line_items', []):
                    if item_data.get('item_number') or item_data.get('description'):
                        KOMLineItem.objects.create(kom_form=kom_form, **item_data)
                
                # Create equipment required
                for eq_data in parsed_data.get('equipment_required', []):
                    if eq_data.get('equipment_type') or eq_data.get('description'):
                        KOMEquipmentRequired.objects.create(kom_form=kom_form, **eq_data)
            
            messages.success(request, f'KOM form imported successfully! Proposal #{kom_form.proposal_number}')
            return redirect('customer:kom_detail', pk=kom_form.pk)
            
        except Exception as e:
            import traceback
            messages.error(request, f'Error importing KOM file: {str(e)}')
            print(f"KOM import error: {traceback.format_exc()}")
            return redirect('customer:kom_import')
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    return render(request, 'customer/kom_import.html')
