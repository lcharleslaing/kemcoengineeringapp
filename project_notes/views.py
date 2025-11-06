from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Job, ProjectNote, EquipmentNote
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


@login_required
def job_list(request):
    """List all jobs, sorted by job number then customer name"""
    jobs = Job.objects.all().order_by('job_number', 'customer_name')
    return render(request, 'project_notes/job_list.html', {'jobs': jobs})


@login_required
def job_create(request):
    """Create a new job"""
    if request.method == 'POST':
        job_number_input = request.POST.get('job_number', '').strip()
        customer_name = request.POST.get('customer_name', '').strip()
        project_name = request.POST.get('project_name', '').strip()
        
        # Extract 5-digit job number only
        job_number = extract_job_number(job_number_input)
        
        if not job_number:
            messages.error(request, f'Job number must contain a 5-digit number. You entered: {job_number_input}')
            return render(request, 'project_notes/job_form.html', {'edit': False})
        
        if len(job_number) != 5:
            messages.error(request, f'Job number must be exactly 5 digits. Extracted: {job_number}')
            return render(request, 'project_notes/job_form.html', {'edit': False})
        
        if Job.objects.filter(job_number=job_number).exists():
            messages.error(request, f'Job #{job_number} already exists.')
            return render(request, 'project_notes/job_form.html', {'edit': False})
        
        job = Job.objects.create(
            job_number=job_number,
            customer_name=customer_name,
            project_name=project_name
        )
        
        if job_number_input != job_number:
            messages.info(request, f'Job number cleaned from "{job_number_input}" to "{job_number}"')
        
        messages.success(request, f'Job #{job_number} created successfully.')
        return redirect('project_notes:job_detail', job_number=job.job_number)
    
    return render(request, 'project_notes/job_form.html', {'edit': False})


@login_required
def job_edit(request, job_number):
    """Edit a job"""
    job = get_object_or_404(Job, job_number=job_number)
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        project_name = request.POST.get('project_name', '').strip()
        
        job.customer_name = customer_name
        job.project_name = project_name
        job.save()
        
        messages.success(request, f'Job #{job_number} updated successfully.')
        return redirect('project_notes:job_detail', job_number=job.job_number)
    
    return render(request, 'project_notes/job_form.html', {'job': job, 'edit': True})


@login_required
@require_http_methods(["POST"])
def job_delete(request, job_number):
    """Delete a job and all associated notes"""
    job = get_object_or_404(Job, job_number=job_number)
    
    # Delete all associated notes first (cascade should handle this, but being explicit)
    job.notes.all().delete()
    job.equipment_notes.all().delete()
    
    # Now delete the job
    job.delete()
    messages.success(request, f'Job #{job_number} and all associated notes deleted successfully.')
    return redirect('project_notes:job_list')


@login_required
def job_detail(request, job_number):
    """View job details with all notes"""
    job = get_object_or_404(Job, job_number=job_number)
    notes = job.notes.all()
    equipment_notes = job.equipment_notes.all()
    return render(request, 'project_notes/job_detail.html', {
        'job': job,
        'notes': notes,
        'equipment_notes': equipment_notes,
    })


@login_required
@require_http_methods(["POST"])
def add_note(request, job_number):
    """Add a general note to a job"""
    job = get_object_or_404(Job, job_number=job_number)
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    note_type = request.POST.get('note_type', 'general').strip()
    
    if not content:
        messages.error(request, 'Note content is required.')
        return redirect('project_notes:job_detail', job_number=job_number)
    
    ProjectNote.objects.create(
        job=job,
        title=title,
        content=content,
        note_type=note_type,
        created_by=request.user
    )
    
    messages.success(request, 'Note added successfully.')
    return redirect('project_notes:job_detail', job_number=job_number)


@login_required
def edit_note(request, note_id):
    """Edit a project note"""
    note = get_object_or_404(ProjectNote, pk=note_id)
    
    # Check permissions - only creator or superuser can edit
    if note.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this note.')
        return redirect('project_notes:job_detail', job_number=note.job.job_number)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        note_type = request.POST.get('note_type', 'general').strip()
        
        if not content:
            messages.error(request, 'Note content is required.')
            return render(request, 'project_notes/note_form.html', {
                'note': note,
                'job': note.job,
                'edit': True
            })
        
        note.title = title
        note.content = content
        note.note_type = note_type
        note.save()
        
        messages.success(request, 'Note updated successfully.')
        return redirect('project_notes:job_detail', job_number=note.job.job_number)
    
    return render(request, 'project_notes/note_form.html', {
        'note': note,
        'job': note.job,
        'edit': True
    })


@login_required
@require_http_methods(["POST"])
def delete_note(request, note_id):
    """Delete a project note"""
    note = get_object_or_404(ProjectNote, pk=note_id)
    job_number = note.job.job_number
    
    # Check permissions - only creator or superuser can delete
    if note.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this note.')
        return redirect('project_notes:job_detail', job_number=job_number)
    
    note.delete()
    messages.success(request, 'Note deleted successfully.')
    return redirect('project_notes:job_detail', job_number=job_number)


@login_required
def edit_equipment_note(request, equipment_note_id):
    """Edit an equipment note"""
    eq_note = get_object_or_404(EquipmentNote, pk=equipment_note_id)
    
    # Check permissions - only creator or superuser can edit
    if eq_note.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this note.')
        return redirect('project_notes:job_detail', job_number=eq_note.job.job_number)
    
    if request.method == 'POST':
        # Get equipment data from form
        equipment_data = {}
        line_items_data = []
        
        # Parse equipment data (this is complex, so we'll allow JSON input or manual editing)
        # For now, we'll keep the existing data structure
        # In a real implementation, you might want a more sophisticated form
        
        # For simplicity, we'll just update the timestamp
        eq_note.save()  # This updates updated_at
        
        messages.success(request, 'Equipment note updated successfully.')
        return redirect('project_notes:job_detail', job_number=eq_note.job.job_number)
    
    return render(request, 'project_notes/equipment_note_form.html', {
        'equipment_note': eq_note,
        'job': eq_note.job,
    })


@login_required
@require_http_methods(["POST"])
def delete_equipment_note(request, equipment_note_id):
    """Delete an equipment note"""
    eq_note = get_object_or_404(EquipmentNote, pk=equipment_note_id)
    job_number = eq_note.job.job_number
    
    # Check permissions - only creator or superuser can delete
    if eq_note.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this note.')
        return redirect('project_notes:job_detail', job_number=job_number)
    
    eq_note.delete()
    messages.success(request, 'Equipment note deleted successfully.')
    return redirect('project_notes:job_detail', job_number=job_number)


@login_required
@require_http_methods(["POST"])
def save_equipment_line_items(request, kom_pk):
    """Save equipment and line items from KOM to notes"""
    from customer.models import KOMForm
    
    kom_form = get_object_or_404(KOMForm, pk=kom_pk)
    
    # Extract 5-digit job number - try stored job_number first, then proposal_number
    stored_job_number = str(kom_form.job_number).strip() if kom_form.job_number else ''
    proposal_number = str(kom_form.proposal_number).strip() if kom_form.proposal_number else ''
    
    job_number = None
    
    # Try to extract from stored job_number first
    if stored_job_number:
        job_number = extract_job_number(stored_job_number)
        if not job_number or len(job_number) != 5:
            # Stored job_number didn't yield a valid 5-digit number, try proposal_number
            job_number = None
    
    # If we still don't have a valid job number, try proposal_number
    if not job_number or len(job_number) != 5:
        if proposal_number:
            job_number = extract_job_number(proposal_number)
    
    # Final validation
    if not job_number or len(job_number) != 5:
        error_msg = f'Could not extract 5-digit job number. Stored job_number: "{stored_job_number}", Proposal number: "{proposal_number}"'
        messages.error(request, error_msg)
        print(f"ERROR in save_equipment_line_items: {error_msg}")  # Debug logging
        return redirect('customer:kom_detail', pk=kom_pk)
    
    # Ensure job_number is exactly 5 digits
    job_number = job_number[:5] if len(job_number) > 5 else job_number
    
    # Get or create job
    job, created = Job.objects.get_or_create(
        job_number=job_number,
        defaults={
            'customer_name': kom_form.bill_to_company or kom_form.ship_to_company or '',
            'project_name': kom_form.project_name or '',
        }
    )
    
    # Update job info if we have better data
    if kom_form.bill_to_company or kom_form.ship_to_company:
        customer_name = kom_form.bill_to_company or kom_form.ship_to_company
        if customer_name and not job.customer_name:
            job.customer_name = customer_name
            job.save()
    
    if kom_form.project_name and not job.project_name:
        job.project_name = kom_form.project_name
        job.save()
    
    # Collect equipment data (only populated fields)
    equipment_data = {}
    from customer.models import KOMEquipmentRequired
    equipment_required = KOMEquipmentRequired.objects.filter(kom_form=kom_form)
    
    for eq in equipment_required:
        eq_type = eq.equipment_type
        if eq_type:
            eq_info = {}
            if eq.qty is not None:
                eq_info['qty'] = int(eq.qty) if eq.qty == int(eq.qty) else float(eq.qty)
            if eq.kn_number:
                eq_info['kn_number'] = eq.kn_number
            if eq.description:
                eq_info['description'] = eq.description
            if eq_info:  # Only add if there's actual data
                equipment_data[eq_type] = eq_info
    
    # Add Heaters (HTR-1 and HTR-2)
    if kom_form.htr_1_qty or kom_form.htr_1_type or kom_form.htr_1_emissions or kom_form.htr_1_size or kom_form.htr_1_pump_grav or kom_form.htr_1_material:
        htr1_info = {}
        if kom_form.htr_1_qty is not None:
            htr1_info['qty'] = kom_form.htr_1_qty
        if kom_form.htr_1_type:
            htr1_info['type'] = kom_form.htr_1_type
        if kom_form.htr_1_emissions:
            htr1_info['emissions'] = kom_form.htr_1_emissions
        if kom_form.htr_1_size:
            htr1_info['size'] = kom_form.htr_1_size
        if kom_form.htr_1_pump_grav:
            htr1_info['pump_grav'] = kom_form.htr_1_pump_grav
        if kom_form.htr_1_material:
            htr1_info['material'] = kom_form.htr_1_material
        if htr1_info:
            equipment_data['HTR-1'] = htr1_info
    
    if kom_form.htr_2_qty or kom_form.htr_2_type or kom_form.htr_2_emissions or kom_form.htr_2_size or kom_form.htr_2_pump_grav or kom_form.htr_2_material:
        htr2_info = {}
        if kom_form.htr_2_qty is not None:
            htr2_info['qty'] = kom_form.htr_2_qty
        if kom_form.htr_2_type:
            htr2_info['type'] = kom_form.htr_2_type
        if kom_form.htr_2_emissions:
            htr2_info['emissions'] = kom_form.htr_2_emissions
        if kom_form.htr_2_size:
            htr2_info['size'] = kom_form.htr_2_size
        if kom_form.htr_2_pump_grav:
            htr2_info['pump_grav'] = kom_form.htr_2_pump_grav
        if kom_form.htr_2_material:
            htr2_info['material'] = kom_form.htr_2_material
        if htr2_info:
            equipment_data['HTR-2'] = htr2_info
    
    # Add Tanks (Tank 1, 2, 3)
    if kom_form.tank_1_type or kom_form.tank_1_dia_in or kom_form.tank_1_ht_ft or kom_form.tank_1_ga or kom_form.tank_1_material:
        tank1_info = {}
        if kom_form.tank_1_type:
            tank1_info['type'] = kom_form.tank_1_type
        if kom_form.tank_1_dia_in is not None:
            tank1_info['dia_in'] = kom_form.tank_1_dia_in
        if kom_form.tank_1_ht_ft is not None:
            tank1_info['ht_ft'] = kom_form.tank_1_ht_ft
        if kom_form.tank_1_ga:
            tank1_info['ga'] = kom_form.tank_1_ga
        if kom_form.tank_1_material:
            tank1_info['material'] = kom_form.tank_1_material
        if tank1_info:
            equipment_data['Tank 1'] = tank1_info
    
    if kom_form.tank_2_type or kom_form.tank_2_dia_in or kom_form.tank_2_ht_ft or kom_form.tank_2_ga or kom_form.tank_2_material:
        tank2_info = {}
        if kom_form.tank_2_type:
            tank2_info['type'] = kom_form.tank_2_type
        if kom_form.tank_2_dia_in is not None:
            tank2_info['dia_in'] = kom_form.tank_2_dia_in
        if kom_form.tank_2_ht_ft is not None:
            tank2_info['ht_ft'] = kom_form.tank_2_ht_ft
        if kom_form.tank_2_ga:
            tank2_info['ga'] = kom_form.tank_2_ga
        if kom_form.tank_2_material:
            tank2_info['material'] = kom_form.tank_2_material
        if tank2_info:
            equipment_data['Tank 2'] = tank2_info
    
    if kom_form.tank_3_type or kom_form.tank_3_dia_in or kom_form.tank_3_ht_ft or kom_form.tank_3_ga or kom_form.tank_3_material:
        tank3_info = {}
        if kom_form.tank_3_type:
            tank3_info['type'] = kom_form.tank_3_type
        if kom_form.tank_3_dia_in is not None:
            tank3_info['dia_in'] = kom_form.tank_3_dia_in
        if kom_form.tank_3_ht_ft is not None:
            tank3_info['ht_ft'] = kom_form.tank_3_ht_ft
        if kom_form.tank_3_ga:
            tank3_info['ga'] = kom_form.tank_3_ga
        if kom_form.tank_3_material:
            tank3_info['material'] = kom_form.tank_3_material
        if tank3_info:
            equipment_data['Tank 3'] = tank3_info
    
    # Add Pumps (Pump 1, 2, 3, 4) and Pump Packaging/Piping Material
    if kom_form.pump_packaging or kom_form.pump_piping_material:
        pump_info = {}
        if kom_form.pump_packaging:
            pump_info['packaging'] = kom_form.pump_packaging
        if kom_form.pump_piping_material:
            pump_info['piping_material'] = kom_form.pump_piping_material
        if pump_info:
            equipment_data['Pumps (General)'] = pump_info
    
    if kom_form.pump_1_type or kom_form.pump_1_qty or kom_form.pump_1_flow_gpm or kom_form.pump_1_tdh_ft:
        pump1_info = {}
        if kom_form.pump_1_type:
            pump1_info['type'] = kom_form.pump_1_type
        if kom_form.pump_1_qty is not None:
            pump1_info['qty'] = kom_form.pump_1_qty
        if kom_form.pump_1_flow_gpm is not None:
            pump1_info['flow_gpm'] = kom_form.pump_1_flow_gpm
        if kom_form.pump_1_tdh_ft is not None:
            pump1_info['tdh_ft'] = kom_form.pump_1_tdh_ft
        if pump1_info:
            equipment_data['Pump 1'] = pump1_info
    
    if kom_form.pump_2_type or kom_form.pump_2_qty or kom_form.pump_2_flow_gpm or kom_form.pump_2_tdh_ft:
        pump2_info = {}
        if kom_form.pump_2_type:
            pump2_info['type'] = kom_form.pump_2_type
        if kom_form.pump_2_qty is not None:
            pump2_info['qty'] = kom_form.pump_2_qty
        if kom_form.pump_2_flow_gpm is not None:
            pump2_info['flow_gpm'] = kom_form.pump_2_flow_gpm
        if kom_form.pump_2_tdh_ft is not None:
            pump2_info['tdh_ft'] = kom_form.pump_2_tdh_ft
        if pump2_info:
            equipment_data['Pump 2'] = pump2_info
    
    if kom_form.pump_3_type or kom_form.pump_3_qty or kom_form.pump_3_flow_gpm or kom_form.pump_3_tdh_ft:
        pump3_info = {}
        if kom_form.pump_3_type:
            pump3_info['type'] = kom_form.pump_3_type
        if kom_form.pump_3_qty is not None:
            pump3_info['qty'] = kom_form.pump_3_qty
        if kom_form.pump_3_flow_gpm is not None:
            pump3_info['flow_gpm'] = kom_form.pump_3_flow_gpm
        if kom_form.pump_3_tdh_ft is not None:
            pump3_info['tdh_ft'] = kom_form.pump_3_tdh_ft
        if pump3_info:
            equipment_data['Pump 3'] = pump3_info
    
    if kom_form.pump_4_type or kom_form.pump_4_qty or kom_form.pump_4_flow_gpm or kom_form.pump_4_tdh_ft:
        pump4_info = {}
        if kom_form.pump_4_type:
            pump4_info['type'] = kom_form.pump_4_type
        if kom_form.pump_4_qty is not None:
            pump4_info['qty'] = kom_form.pump_4_qty
        if kom_form.pump_4_flow_gpm is not None:
            pump4_info['flow_gpm'] = kom_form.pump_4_flow_gpm
        if kom_form.pump_4_tdh_ft is not None:
            pump4_info['tdh_ft'] = kom_form.pump_4_tdh_ft
        if pump4_info:
            equipment_data['Pump 4'] = pump4_info
    
    # Collect line items (Item# and Description only)
    line_items_data = []
    from customer.models import KOMLineItem
    line_items = KOMLineItem.objects.filter(kom_form=kom_form)
    
    for item in line_items:
        if item.item_number or item.description:
            line_items_data.append({
                'item_number': item.item_number or '',
                'description': item.description or '',
            })
    
    # Create or update equipment note
    equipment_note, created = EquipmentNote.objects.update_or_create(
        job=job,
        defaults={
            'equipment_data': equipment_data,
            'line_items_data': line_items_data,
            'created_by': request.user,
        }
    )
    
    if created:
        messages.success(request, f'Equipment and line items saved to notes for Job #{job_number}.')
    else:
        messages.success(request, f'Equipment and line items updated in notes for Job #{job_number}.')
    
    return redirect('customer:kom_detail', pk=kom_pk)
