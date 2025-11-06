from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.conf import settings
from django.views.decorators.http import require_http_methods
import os
import tempfile

from .models import KOMForm, KOMLineItem, KOMEquipmentRequired
from .utils import parse_kom_excel
import re


def extract_job_number(value):
    """Extract 5-digit job number from a string (e.g., '35411-R4' -> '35411', '35256B' -> '35256')"""
    if not value:
        return ''
    value = str(value).strip()
    # Find first occurrence of exactly 5 consecutive digits
    # Use word boundaries or start/end of string, or non-digit characters
    match = re.search(r'(?:^|\D)(\d{5})(?:\D|$)', value)
    if match:
        return match.group(1)
    # Fallback: try without word boundaries (for cases like "35411-R4" where - is not a word boundary)
    match = re.search(r'\d{5}', value)
    if match:
        return match.group(0)
    return ''


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
    """List all KOM forms, sorted by job number then customer name"""
    kom_forms = KOMForm.objects.all().order_by('job_number', 'bill_to_company', 'ship_to_company', '-created_at')
    return render(request, 'customer/kom_list.html', {'kom_forms': kom_forms})


@admin_required
def kom_compare(request, pk1, pk2):
    """Compare two KOM forms by their raw_data JSON"""
    kom1 = get_object_or_404(KOMForm, pk=pk1)
    kom2 = get_object_or_404(KOMForm, pk=pk2)
    
    import json
    
    def get_differences(dict1, dict2, prefix=''):
        """Recursively find differences between two dictionaries"""
        differences = []
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            val1 = dict1.get(key, None)
            val2 = dict2.get(key, None)
            full_key = f"{prefix}.{key}" if prefix else key
            
            if val1 != val2:
                if isinstance(val1, dict) and isinstance(val2, dict):
                    # Recursively compare nested dicts
                    differences.extend(get_differences(val1, val2, full_key))
                else:
                    differences.append({
                        'field': full_key,
                        'kom1_value': val1,
                        'kom2_value': val2,
                    })
        
        return differences
    
    # Compare raw_data JSON - handle case where field might not exist yet
    differences = []
    try:
        raw1 = kom1.raw_data if kom1.raw_data else {}
        raw2 = kom2.raw_data if kom2.raw_data else {}
    except (AttributeError, KeyError):
        # Field doesn't exist yet (migration not run)
        raw1 = {}
        raw2 = {}
    
    if raw1 and raw2:
        differences = get_differences(raw1, raw2)
    
    # Also compare line items
    line_items_diff = []
    items1 = {item.item_number: item for item in kom1.line_items.all()}
    items2 = {item.item_number: item for item in kom2.line_items.all()}
    all_item_nums = set(items1.keys()) | set(items2.keys())
    
    for item_num in all_item_nums:
        item1 = items1.get(item_num)
        item2 = items2.get(item_num)
        if item1 and item2:
            if item1.description != item2.description or item1.value_1 != item2.value_1 or item1.value_2 != item2.value_2 or item1.value_3 != item2.value_3 or item1.value_4 != item2.value_4:
                line_items_diff.append({
                    'item_number': item_num,
                    'kom1': item1,
                    'kom2': item2,
                })
        elif item1:
            line_items_diff.append({
                'item_number': item_num,
                'kom1': item1,
                'kom2': None,
            })
        elif item2:
            line_items_diff.append({
                'item_number': item_num,
                'kom1': None,
                'kom2': item2,
            })
    
    # Compare equipment required
    equipment_diff = []
    eq1 = {eq.equipment_type: eq for eq in kom1.equipment_required.all()}
    eq2 = {eq.equipment_type: eq for eq in kom2.equipment_required.all()}
    all_eq_types = set(eq1.keys()) | set(eq2.keys())
    
    for eq_type in all_eq_types:
        e1 = eq1.get(eq_type)
        e2 = eq2.get(eq_type)
        if e1 and e2:
            if e1.qty != e2.qty or e1.kn_number != e2.kn_number or e1.description != e2.description:
                equipment_diff.append({
                    'equipment_type': eq_type,
                    'kom1': e1,
                    'kom2': e2,
                })
        elif e1:
            equipment_diff.append({
                'equipment_type': eq_type,
                'kom1': e1,
                'kom2': None,
            })
        elif e2:
            equipment_diff.append({
                'equipment_type': eq_type,
                'kom1': None,
                'kom2': e2,
            })
    
    context = {
        'kom1': kom1,
        'kom2': kom2,
        'differences': differences,
        'line_items_diff': line_items_diff,
        'equipment_diff': equipment_diff,
        'kom1_json': json.dumps(raw1, indent=2, default=str) if raw1 else '{}',
        'kom2_json': json.dumps(raw2, indent=2, default=str) if raw2 else '{}',
    }
    
    return render(request, 'customer/kom_compare.html', context)


@admin_required
def kom_detail(request, pk):
    """View a single KOM form with all fields"""
    kom_form = get_object_or_404(KOMForm, pk=pk)
    return render(request, 'customer/kom_detail.html', {'kom': kom_form})


@admin_required
@require_http_methods(["POST"])
def kom_delete(request, pk):
    """Delete a KOM form and its associated file"""
    kom_form = get_object_or_404(KOMForm, pk=pk)
    proposal_number = kom_form.proposal_number or f"#{pk}"
    
    # Delete the associated file if it exists
    if kom_form.file_path:
        file_path = str(kom_form.file_path)
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                messages.info(request, f'Deleted file: {os.path.basename(file_path)}')
        except Exception as e:
            messages.warning(request, f'Could not delete file: {str(e)}')
    
    # Delete the KOM form (this will cascade delete line items and equipment required)
    kom_form.delete()
    
    messages.success(request, f'KOM form {proposal_number} deleted successfully.')
    return redirect('customer:kom_list')


@login_required
def kom_open_file(request, pk):
    """Return file path for Electron to open - always returns JSON"""
    from django.http import JsonResponse
    import os
    import traceback
    
    try:
        # Check authentication and permissions - return JSON, not redirect
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Permission denied. Admin access required.'}, status=403)
        
        try:
            kom_form = KOMForm.objects.get(pk=pk)
        except KOMForm.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'KOM form with ID {pk} not found'}, status=404)
        
        if not kom_form.file_path:
            return JsonResponse({'success': False, 'error': 'No file path stored for this KOM form'}, status=404)
        
        file_path = str(kom_form.file_path).strip()
        
        # Normalize the path (handle both relative and absolute paths) - ensure it's a string
        if not os.path.isabs(file_path):
            # If relative, try to resolve it
            file_path = str(os.path.abspath(file_path))
        else:
            file_path = str(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Try to find it in MEDIA_ROOT as a fallback
            if settings.MEDIA_ROOT:
                # Check if it's a relative path that should be in MEDIA_ROOT
                media_root_str = str(settings.MEDIA_ROOT)
                media_path = str(os.path.join(media_root_str, file_path.lstrip('/')))
                if os.path.exists(media_path):
                    file_path = str(os.path.abspath(media_path))
                else:
                    # Try searching in kom_files directory
                    found = False
                    kom_files_dir = str(os.path.join(media_root_str, 'kom_files'))
                    if os.path.exists(kom_files_dir):
                        for root, dirs, files in os.walk(kom_files_dir):
                            if kom_form.source_file in files:
                                file_path = str(os.path.abspath(os.path.join(root, kom_form.source_file)))
                                found = True
                                break
                    
                    if not found:
                        return JsonResponse({
                            'success': False, 
                            'error': f'File not found at: {str(file_path)}',
                            'stored_path': str(kom_form.file_path),
                            'source_file': str(kom_form.source_file),
                            'media_root': str(settings.MEDIA_ROOT) if settings.MEDIA_ROOT else None
                        }, status=404)
            else:
                return JsonResponse({
                    'success': False, 
                    'error': f'File not found at: {str(file_path)}',
                    'stored_path': str(kom_form.file_path),
                    'media_root_not_set': True
                }, status=404)
        
        # Verify it's actually a file
        if not os.path.isfile(file_path):
            return JsonResponse({
                'success': False, 
                'error': f'Path exists but is not a file: {str(file_path)}'
            }, status=404)
        
        # Return the absolute file path for Electron to open - convert to string explicitly
        final_path = str(os.path.abspath(file_path))
        return JsonResponse({
            'success': True, 
            'file_path': final_path
        })
        
    except Exception as e:
        # Catch any unexpected errors and return JSON
        error_trace = traceback.format_exc()
        print(f"Error in kom_open_file: {error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'traceback': error_trace if settings.DEBUG else None
        }, status=500)


@admin_required
def kom_export_text(request, pk):
    """Export KOM form as formatted text"""
    from django.http import HttpResponse
    
    kom_form = get_object_or_404(KOMForm, pk=pk)
    
    def format_field(label, value, default="MISSING"):
        """Format a field, showing MISSING if empty"""
        if value is None or value == '' or value == '-':
            return f"{label}: {default}"
        if isinstance(value, bool):
            return f"{label}: {'YES' if value else 'NO'}"
        if hasattr(value, 'strftime'):  # Date object
            return f"{label}: {value.strftime('%m/%d/%Y')}"
        return f"{label}: {value}"
    
    output = []
    output.append("=" * 80)
    output.append(f"KOM FORM EXPORT - Proposal #{kom_form.proposal_number or 'N/A'}")
    output.append(f"Project: {kom_form.project_name or 'N/A'}")
    output.append(f"Source File: {kom_form.source_file or 'N/A'}")
    output.append(f"Exported: {kom_form.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 80)
    output.append("")
    
    # TO BE COMPLETED BY SALES
    output.append("TO BE COMPLETED BY SALES")
    output.append("-" * 80)
    output.append(format_field("Proposal #", kom_form.proposal_number))
    output.append(format_field("Proposal Date", kom_form.proposal_date))
    output.append(format_field("Sales Rep", kom_form.sales_rep))
    output.append(format_field("Date of OC", kom_form.date_of_oc))
    output.append(format_field("Industry", kom_form.industry))
    output.append(format_field("Industry Subcategory", kom_form.industry_subcategory))
    output.append(format_field("Discount", f"{kom_form.discount}%" if kom_form.discount else None))
    output.append(format_field("PO#", kom_form.po_number))
    output.append("")
    output.append("COMMISSIONS:")
    output.append(format_field("  Comm #1 (Inside) %", f"{kom_form.comm_1_inside_percent}%" if kom_form.comm_1_inside_percent else None))
    output.append(format_field("  Comm #1 (Inside) Name", kom_form.comm_1_inside_name))
    output.append(format_field("  Comm #2 (Inside) %", f"{kom_form.comm_2_inside_percent}%" if kom_form.comm_2_inside_percent else None))
    output.append(format_field("  Comm #2 (Inside) Name", kom_form.comm_2_inside_name))
    output.append(format_field("  Comm (Outside) Amount", f"${kom_form.comm_outside_amount}" if kom_form.comm_outside_amount else None))
    output.append(format_field("  Comm (Outside) Name", kom_form.comm_outside_name))
    output.append("")
    output.append(format_field("Consultant", kom_form.consultant))
    output.append(format_field("Contractor Name", kom_form.contractor_name))
    output.append(format_field("Desired Delivery", kom_form.desired_delivery))
    output.append("")
    
    # BILL TO
    output.append("BILL TO")
    output.append("-" * 80)
    output.append(format_field("Name", kom_form.bill_to_name))
    output.append(format_field("Phone", kom_form.bill_to_phone))
    output.append(format_field("Email", kom_form.bill_to_email))
    output.append(format_field("Company", kom_form.bill_to_company))
    output.append(format_field("Address", kom_form.bill_to_address))
    output.append(format_field("City", kom_form.bill_to_city))
    output.append(format_field("State", kom_form.bill_to_state))
    output.append(format_field("ZIP", kom_form.bill_to_zip))
    output.append("")
    
    # SHIP TO
    output.append("SHIP TO")
    output.append("-" * 80)
    output.append(format_field("Name", kom_form.ship_to_name))
    output.append(format_field("Phone", kom_form.ship_to_phone))
    output.append(format_field("Email", kom_form.ship_to_email))
    output.append(format_field("Company", kom_form.ship_to_company))
    output.append(format_field("Address", kom_form.ship_to_address))
    output.append(format_field("City", kom_form.ship_to_city))
    output.append(format_field("State", kom_form.ship_to_state))
    output.append(format_field("ZIP", kom_form.ship_to_zip))
    output.append("")
    
    # TAX INFORMATION
    output.append("TAX INFORMATION")
    output.append("-" * 80)
    output.append(format_field("Tax Exempt", kom_form.tax_exempt))
    output.append(format_field("Exempt Cert in Hand", kom_form.exempt_cert_in_hand))
    output.append(format_field("Tax Action Who", kom_form.tax_action_who))
    output.append(format_field("Tax Action When", kom_form.tax_action_when))
    output.append(format_field("Confirm Tax Status Noted", kom_form.confirm_tax_status_noted))
    output.append(format_field("Customer in Sage", kom_form.customer_in_sage))
    output.append("")
    
    # PAYMENT MILESTONES
    output.append("PAYMENT MILESTONES")
    output.append("-" * 80)
    for i in range(1, 6):
        event = getattr(kom_form, f'payment_milestone_{i}_event', '')
        percent = getattr(kom_form, f'payment_milestone_{i}_percent', None)
        terms = getattr(kom_form, f'payment_milestone_{i}_terms', '')
        notes = getattr(kom_form, f'payment_milestone_{i}_notes', '')
        if event or percent or terms or notes:
            output.append(f"Milestone {i}:")
            output.append(format_field("  Event", event))
            output.append(format_field("  Percent", f"{percent}%" if percent else None))
            output.append(format_field("  Terms", terms))
            output.append(format_field("  Notes", notes))
    output.append("")
    
    # SHIPPING
    output.append("SHIPPING")
    output.append("-" * 80)
    output.append(format_field("Freight", kom_form.freight))
    output.append(format_field("International", kom_form.international))
    output.append(format_field("International Freight Method", kom_form.international_freight_method))
    output.append(format_field("Shipping Instructions", kom_form.shipping_instructions))
    output.append("")
    
    # SPECIFICATIONS
    output.append("SPECIFICATIONS AND TERMS & CONDITIONS")
    output.append("-" * 80)
    output.append(format_field("Specifications Provided", kom_form.specifications_provided))
    output.append(format_field("Specifications Agreed", kom_form.specifications_agreed))
    output.append(format_field("Liquidated Damages", kom_form.liquidated_damages))
    output.append(format_field("Liquidated Damages Rate & Cap", kom_form.liquidated_damages_rate_cap))
    output.append(format_field("Passivation", kom_form.passivation))
    output.append(format_field("Passivation In/Out/Both", kom_form.passivation_in_out_both))
    output.append("")
    
    # APPROVAL PRINTS
    output.append("APPROVAL PRINTS")
    output.append("-" * 80)
    output.append(format_field("Approval Prints Required", kom_form.approval_prints_required))
    output.append(format_field("Approval Prints Electrical", kom_form.approval_prints_electrical))
    output.append(format_field("LL & Mech Approval", kom_form.approval_prints_ll_mech))
    output.append(format_field("Elect Approval", kom_form.approval_prints_elect))
    output.append(format_field("Engineering Order Prior to Approval", kom_form.engineering_order_prior_to_approval))
    output.append("")
    
    # EQUIPMENT - Heaters
    output.append("EQUIPMENT - HEATERS")
    output.append("-" * 80)
    output.append("HTR - 1:")
    output.append(format_field("  Qty", kom_form.htr_1_qty))
    output.append(format_field("  Type", kom_form.htr_1_type))
    output.append(format_field("  Emissions", kom_form.htr_1_emissions))
    output.append(format_field("  Size", kom_form.htr_1_size))
    output.append(format_field("  Pump/Grav", kom_form.htr_1_pump_grav))
    output.append(format_field("  Material", kom_form.htr_1_material))
    output.append("")
    output.append("HTR - 2:")
    output.append(format_field("  Qty", kom_form.htr_2_qty))
    output.append(format_field("  Type", kom_form.htr_2_type))
    output.append(format_field("  Emissions", kom_form.htr_2_emissions))
    output.append(format_field("  Size", kom_form.htr_2_size))
    output.append(format_field("  Pump/Grav", kom_form.htr_2_pump_grav))
    output.append(format_field("  Material", kom_form.htr_2_material))
    output.append("")
    
    # Stack Economizer
    output.append("STACK ECONOMIZER")
    output.append("-" * 80)
    output.append(format_field("Size (BHP)", kom_form.stk_econ_size_bhp))
    output.append(format_field("Pump/Grav", kom_form.stk_econ_pump_grav))
    output.append(format_field("Material", kom_form.stk_econ_material))
    output.append("")
    
    # Stack
    output.append("STACK(S)")
    output.append("-" * 80)
    output.append(format_field("Length (ft)", kom_form.stack_length_ft))
    output.append(format_field("Total", kom_form.stack_total))
    output.append(format_field("Caps", kom_form.stack_caps))
    output.append("")
    
    # HR
    output.append("HR")
    output.append("-" * 80)
    output.append(format_field("# Sections", kom_form.hr_sections))
    output.append(format_field("Diam (in)", kom_form.hr_diam_in))
    output.append(format_field("Tubes", kom_form.hr_tubes))
    output.append(format_field("Material", kom_form.hr_material))
    output.append("")
    
    # TANKS
    output.append("TANKS")
    output.append("-" * 80)
    for i in range(1, 4):
        tank_type = getattr(kom_form, f'tank_{i}_type', '')
        if tank_type or getattr(kom_form, f'tank_{i}_dia_in', None):
            output.append(f"Tank {i}:")
            output.append(format_field("  Type", tank_type))
            output.append(format_field("  Dia (in)", getattr(kom_form, f'tank_{i}_dia_in', None)))
            output.append(format_field("  Ht (ft)", getattr(kom_form, f'tank_{i}_ht_ft', None)))
            output.append(format_field("  GA", getattr(kom_form, f'tank_{i}_ga', '')))
            output.append(format_field("  Material", getattr(kom_form, f'tank_{i}_material', '')))
            output.append("")
    
    # PUMPS
    output.append("PUMPS")
    output.append("-" * 80)
    output.append(format_field("Packaging", kom_form.pump_packaging))
    output.append(format_field("Piping Material", kom_form.pump_piping_material))
    output.append("")
    for i in range(1, 5):
        pump_type = getattr(kom_form, f'pump_{i}_type', '')
        if pump_type or getattr(kom_form, f'pump_{i}_qty', None):
            output.append(f"Pump {i}:")
            output.append(format_field("  Type", pump_type))
            output.append(format_field("  Qty", getattr(kom_form, f'pump_{i}_qty', None)))
            output.append(format_field("  Flow (gpm)", getattr(kom_form, f'pump_{i}_flow_gpm', None)))
            output.append(format_field("  TDH (ft)", getattr(kom_form, f'pump_{i}_tdh_ft', None)))
            output.append("")
    
    # Steam Heaters
    output.append("STEAM HEATERS")
    output.append("-" * 80)
    for i in range(1, 3):
        if getattr(kom_form, f'steam_heater_{i}_dia_in', None) or getattr(kom_form, f'steam_heater_{i}_material', ''):
            output.append(f"Steam Heater {i}:")
            output.append(format_field("  Dia (in)", getattr(kom_form, f'steam_heater_{i}_dia_in', None)))
            output.append(format_field("  Length (in)", getattr(kom_form, f'steam_heater_{i}_length_in', None)))
            output.append(format_field("  Material", getattr(kom_form, f'steam_heater_{i}_material', '')))
            output.append(format_field("  Valve Type", getattr(kom_form, f'steam_heater_{i}_valve_type', '')))
            output.append("")
    
    # Softener
    output.append("SOFTENER")
    output.append("-" * 80)
    output.append(format_field("ASME Coded", kom_form.softener_asme_coded))
    output.append(format_field("Tank Material", kom_form.softener_tank_material))
    output.append(format_field("Face Plumbing Material", kom_form.softener_face_plumbing_material))
    output.append("")
    
    # Panel
    output.append("PANEL(S)")
    output.append("-" * 80)
    output.append(format_field("Qty", kom_form.panel_qty))
    output.append(format_field("PLC", kom_form.panel_plc))
    output.append(format_field("Split Volt", kom_form.panel_split_volt))
    output.append("")
    
    # Other Equipment
    output.append("OTHER EQUIPMENT")
    output.append("-" * 80)
    output.append(format_field("Vent Condenser", kom_form.other_vent_condenser))
    output.append(format_field("Shaker Screen", kom_form.other_shaker_screen))
    output.append("")
    
    # UTILITIES
    output.append("UTILITIES")
    output.append("-" * 80)
    output.append(format_field("City Water Meter (in)", kom_form.city_water_meter_in))
    output.append(format_field("Electrical", kom_form.electrical))
    output.append(format_field("Fuel Type", kom_form.fuel_type))
    output.append(format_field("Gas Pressure (psi)", kom_form.gas_pressure_psi))
    output.append(format_field("Onsite Gas Supply Diameter (in)", kom_form.onsite_gas_supply_diameter_in))
    output.append(format_field("Gas Train Orientation", kom_form.gas_train_orientation))
    output.append(format_field("Utilities Match Proposal", kom_form.utilities_match_proposal))
    output.append("")
    
    # OTHER INFO
    output.append("OTHER INFO")
    output.append("-" * 80)
    output.append(format_field("Notes", kom_form.notes))
    output.append(format_field("Other Info", kom_form.other_info))
    output.append(format_field("Project Name", kom_form.project_name))
    output.append(format_field("Project Type", kom_form.project_type))
    output.append("")
    
    # LINE ITEMS
    output.append("LINE ITEMS (TO BE COMPLETED BY APPS)")
    output.append("-" * 80)
    line_items = kom_form.line_items.all()
    if line_items:
        for item in line_items:
            output.append(f"Item: {item.item_number or 'N/A'}")
            output.append(format_field("  Description", item.description))
            output.append(format_field("  Value 1", f"${item.value_1}" if item.value_1 else None))
            output.append(format_field("  Value 2", f"${item.value_2}" if item.value_2 else None))
            output.append(format_field("  Value 3", f"${item.value_3}" if item.value_3 else None))
            output.append(format_field("  Value 4", f"${item.value_4}" if item.value_4 else None))
            output.append("")
    else:
        output.append("MISSING - No line items found")
        output.append("")
    
    # LABOR HOURS
    output.append("LABOR HOURS")
    output.append("-" * 80)
    output.append(format_field("HR", kom_form.labor_hr))
    output.append(format_field("Pkg", kom_form.labor_pkg))
    output.append(format_field("Fab", kom_form.labor_fab))
    output.append(format_field("Wiring", kom_form.labor_wiring))
    output.append("")
    
    # EQUIPMENT REQUIRED
    output.append("EQUIPMENT REQUIRED")
    output.append("-" * 80)
    equipment = kom_form.equipment_required.all()
    if equipment:
        for eq in equipment:
            output.append(f"{eq.equipment_type}:")
            output.append(format_field("  Qty", eq.qty))
            output.append(format_field("  KN Number", eq.kn_number))
            output.append(format_field("  Description", eq.description))
            output.append("")
    else:
        output.append("MISSING - No equipment required found")
        output.append("")
    
    # CAPITAL
    output.append("CAPITAL")
    output.append("-" * 80)
    output.append(format_field("Sell Price", f"${kom_form.capital_sell_price}" if kom_form.capital_sell_price else None))
    output.append(format_field("Equip Cost", f"${kom_form.capital_equip_cost}" if kom_form.capital_equip_cost else None))
    output.append(format_field("Freight", f"${kom_form.capital_freight}" if kom_form.capital_freight else None))
    output.append(format_field("Startup Cost", f"${kom_form.capital_startup_cost}" if kom_form.capital_startup_cost else None))
    output.append(format_field("Protect Cost", f"${kom_form.capital_protect_cost}" if kom_form.capital_protect_cost else None))
    output.append(format_field("Net Revenue", f"${kom_form.capital_net_revenue}" if kom_form.capital_net_revenue else None))
    output.append("")
    
    # INSTALL
    output.append("INSTALL")
    output.append("-" * 80)
    output.append(format_field("Sell Price", f"${kom_form.install_sell_price}" if kom_form.install_sell_price else None))
    output.append(format_field("Install Cost", f"${kom_form.install_cost}" if kom_form.install_cost else None))
    output.append(format_field("# of Trips", kom_form.install_trips))
    output.append(format_field("# of Days", kom_form.install_days))
    output.append(format_field("Net Revenue", f"${kom_form.install_net_revenue}" if kom_form.install_net_revenue else None))
    output.append("")
    
    # ENGINEERING
    output.append("TO BE COMPLETED BY ENG")
    output.append("-" * 80)
    output.append(format_field("Weld In&Out", kom_form.eng_weld_in_out))
    output.append(format_field("Height Greater than 20'", kom_form.eng_height_greater_than_20ft))
    output.append(format_field("Crane Req'd", kom_form.eng_crane_reqd))
    output.append(format_field("Hi Temp Htr", kom_form.eng_hi_temp_htr))
    output.append(format_field("Large HP or Excessive LL Pumps", kom_form.eng_large_hp_or_excessive_ll_pumps))
    output.append(format_field("Generator Need", kom_form.eng_generator_need))
    output.append(format_field("Special Testing Reqd", kom_form.eng_special_testing_reqd))
    output.append(format_field("Extra Fork Lift or Scissor Lift Reqd", kom_form.eng_extra_forklift_or_scissor_lift_reqd))
    output.append("")
    
    output.append("=" * 80)
    output.append("END OF EXPORT")
    output.append("=" * 80)
    
    text_content = "\n".join(output)
    
    response = HttpResponse(text_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'inline; filename="kom_export_{kom_form.proposal_number or "unknown"}.txt"'
    return response


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
        
        # Get file path from form if provided (Electron can pass this)
        original_file_path = request.POST.get('file_path', '').strip()
        
        # Save uploaded file temporarily for parsing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # ALWAYS save a copy to MEDIA_ROOT so we can reliably open it later
        # This ensures the file exists even if the original path is inaccessible
        from django.utils import timezone
        import uuid
        import shutil
        
        ts = timezone.now()
        year = ts.strftime('%Y')
        month = ts.strftime('%m')
        dest_dir = os.path.join(settings.MEDIA_ROOT, 'kom_files', year, month)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Create a safe filename with timestamp and UUID to avoid collisions
        safe_name = uploaded_file.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Remove any path components that might be in the filename
        safe_name = os.path.basename(safe_name)
        unique_id = str(uuid.uuid4())[:8]
        dest_filename = f"{int(ts.timestamp())}_{unique_id}_{safe_name}"
        dest_path = os.path.join(dest_dir, dest_filename)
        
        # Copy the temp file to the permanent location - THIS MUST SUCCEED
        try:
            # Use shutil.copy2 to preserve metadata
            shutil.copy2(tmp_path, dest_path)
            # Normalize the path to absolute string
            file_path = str(os.path.abspath(dest_path))
            # Verify the file was saved and exists
            if not os.path.exists(file_path):
                raise Exception(f"File was not saved correctly to {file_path}")
            if not os.path.isfile(file_path):
                raise Exception(f"Saved path is not a file: {file_path}")
        except Exception as e:
            # If saving to MEDIA_ROOT fails, try original path ONLY if it exists and is accessible
            if original_file_path and os.path.exists(original_file_path) and os.path.isfile(original_file_path):
                file_path = str(os.path.abspath(original_file_path))
                messages.warning(request, f'Could not save file copy to media directory. Using original file path. Error: {str(e)}')
            else:
                # FAIL the import - we cannot proceed without a reliable file path
                messages.error(request, f'Failed to save imported file. Cannot proceed with import. Error: {str(e)}')
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                return redirect('customer:kom_import')
        
        try:
            # Parse the Excel file - returns JSON-serializable data
            parsed_data = parse_kom_excel(tmp_path)
            
            # Create KOMForm instance - save raw_data JSON first
            with transaction.atomic():
                # Extract line_items and equipment_required before saving (copy them, don't modify original)
                line_items_data = parsed_data.get('line_items', [])
                equipment_required_data = parsed_data.get('equipment_required', [])
                
                # Create KOMForm with raw_data JSON stored
                # First, convert date strings to date objects for direct field assignment
                from datetime import datetime as dt
                from decimal import Decimal as Dec
                
                field_data = {}
                for key, value in parsed_data.items():
                    if key in ['line_items', 'equipment_required']:
                        continue
                    if hasattr(KOMForm, key):
                        # Handle date strings (ISO format)
                        if 'date' in key and isinstance(value, str):
                            try:
                                field_data[key] = dt.fromisoformat(value).date()
                            except:
                                field_data[key] = value
                        # Handle decimals (from float)
                        elif isinstance(value, (int, float)) and ('percent' in key or 'cost' in key or 'price' in key or 'amount' in key or 'revenue' in key or 'discount' in key):
                            try:
                                field_data[key] = Dec(str(value))
                            except:
                                field_data[key] = value
                        # Handle integers
                        elif isinstance(value, float) and ('qty' in key or 'sections' in key or 'trips' in key or 'days' in key):
                            field_data[key] = int(value) if value else None
                        else:
                            field_data[key] = value
                
                # Create KOMForm with raw_data JSON stored
                # Try to include raw_data, but handle if field doesn't exist yet
                # Ensure file_path is a string and verify it exists before saving
                file_path_str = str(file_path)
                if not os.path.exists(file_path_str):
                    raise Exception(f"Cannot save KOM: File does not exist at {file_path_str}")
                
                # Extract 5-digit job number from proposal_number
                proposal_number = field_data.get('proposal_number', '').strip()
                job_number = extract_job_number(proposal_number)
                
                if not job_number:
                    messages.warning(request, f'Could not extract 5-digit job number from proposal number: {proposal_number}')
                
                create_kwargs = {
                    'created_by': request.user,
                    'source_file': uploaded_file.name,
                    'file_path': file_path_str,  # Store the file path as string
                    'job_number': job_number,  # Extracted 5-digit number only
                    **field_data
                }
                
                # Try to add raw_data - if it fails, the field doesn't exist yet
                try:
                    # Check if we can create with raw_data
                    create_kwargs['raw_data'] = parsed_data
                    kom_form = KOMForm.objects.create(**create_kwargs)
                except Exception as db_error:
                    # If it's a database error about missing column, try without raw_data
                    error_str = str(db_error).lower()
                    if 'no such column' in error_str or 'raw_data' in error_str or 'column' in error_str:
                        # Remove raw_data and try again
                        create_kwargs.pop('raw_data', None)
                        kom_form = KOMForm.objects.create(**create_kwargs)
                        messages.warning(request, 'KOM imported, but raw_data field not available. Please run migrations: python manage.py makemigrations customer && python manage.py migrate')
                    else:
                        # Re-raise if it's a different error
                        raise
                
                # Create line items
                for item_data in line_items_data:
                    if item_data.get('item_number') or item_data.get('description'):
                        KOMLineItem.objects.create(kom_form=kom_form, **item_data)
                
                # Create equipment required
                for eq_data in equipment_required_data:
                    if eq_data.get('equipment_type') or eq_data.get('description'):
                        KOMEquipmentRequired.objects.create(kom_form=kom_form, **eq_data)
            
            # Display validation warnings if any
            validation_warnings = parsed_data.get('_validation_warnings', [])
            if validation_warnings:
                for warning in validation_warnings:
                    messages.warning(request, f'Parser Warning: {warning}')
            
            # Verify file_path was saved correctly
            kom_form.refresh_from_db()
            if not kom_form.file_path:
                messages.error(request, 'WARNING: File path was not saved to database. File may not be openable.')
            elif not os.path.exists(str(kom_form.file_path)):
                messages.warning(request, f'WARNING: File path saved but file does not exist at: {kom_form.file_path}')
            
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
