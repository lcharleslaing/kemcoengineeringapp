from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from .models import Assembly, Component, Rule, RuleVersion, Inconsistency, Configurator
from .utils import (
    parse_component_name_from_code,
    extract_triggers,
    extract_part_numbers,
    detect_inconsistencies,
    parse_markdown_import,
    parse_structured_import,
    determine_rule_type,
)
import os
import json


@login_required
def assembly_list(request):
    """List all assemblies"""
    assemblies = Assembly.objects.annotate(
        component_count=Count('components', distinct=True),
        rule_count=Count('components__rules', distinct=True),
    ).order_by('name')
    
    # Add inconsistency count manually (can't use filter in Count with related field easily)
    for assembly in assemblies:
        assembly.inconsistency_count = Inconsistency.objects.filter(
            assembly=assembly,
            status='open'
        ).count()
    
    return render(request, 'ilogic/assembly_list.html', {
        'assemblies': assemblies,
    })


@login_required
def assembly_detail(request, pk):
    """View assembly details with components and rules"""
    assembly = get_object_or_404(Assembly, pk=pk)
    components = assembly.components.all().prefetch_related('rules')
    
    # Get summary stats
    total_rules = Rule.objects.filter(component__assembly=assembly).count()
    open_inconsistencies = Inconsistency.objects.filter(
        assembly=assembly,
        status='open'
    ).count()
    
    return render(request, 'ilogic/assembly_detail.html', {
        'assembly': assembly,
        'components': components,
        'total_rules': total_rules,
        'open_inconsistencies': open_inconsistencies,
    })


@login_required
def assembly_create(request):
    """Create a new assembly"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        inventor_file_path = request.POST.get('inventor_file_path', '').strip()
        
        if not name:
            messages.error(request, 'Assembly name is required.')
            return render(request, 'ilogic/assembly_form.html', {'edit': False})
        
        assembly = Assembly.objects.create(
            name=name,
            description=description,
            inventor_file_path=inventor_file_path,
            created_by=request.user,
        )
        
        messages.success(request, f'Assembly "{name}" created successfully.')
        return redirect('ilogic:assembly_detail', pk=assembly.pk)
    
    return render(request, 'ilogic/assembly_form.html', {'edit': False})


@login_required
def assembly_edit(request, pk):
    """Edit an assembly"""
    assembly = get_object_or_404(Assembly, pk=pk)
    
    if request.method == 'POST':
        assembly.name = request.POST.get('name', '').strip()
        assembly.description = request.POST.get('description', '').strip()
        assembly.inventor_file_path = request.POST.get('inventor_file_path', '').strip()
        assembly.save()
        
        messages.success(request, f'Assembly "{assembly.name}" updated successfully.')
        return redirect('ilogic:assembly_detail', pk=assembly.pk)
    
    return render(request, 'ilogic/assembly_form.html', {'edit': True, 'assembly': assembly})


@login_required
@require_http_methods(["POST"])
def assembly_delete(request, pk):
    """Delete an assembly and all its components/rules"""
    assembly = get_object_or_404(Assembly, pk=pk)
    name = assembly.name
    
    # Delete will cascade to components and rules
    assembly.delete()
    
    messages.success(request, f'Assembly "{name}" and all associated data deleted successfully.')
    return redirect('ilogic:assembly_list')


@login_required
def component_detail(request, pk):
    """View component details with all rules"""
    component = get_object_or_404(Component, pk=pk)
    rules = component.rules.all()
    
    # Get inconsistencies for this component
    inconsistencies = Inconsistency.objects.filter(
        component=component,
        status='open'
    ).order_by('-severity', '-found_at')
    
    return render(request, 'ilogic/component_detail.html', {
        'component': component,
        'rules': rules,
        'inconsistencies': inconsistencies,
    })


@login_required
def component_edit(request, pk):
    """Edit a component"""
    component = get_object_or_404(Component, pk=pk)
    
    if request.method == 'POST':
        component.name = request.POST.get('name', '').strip()
        component.inventor_instance_name = request.POST.get('inventor_instance_name', '').strip()
        component.component_type = request.POST.get('component_type', '').strip()
        component.description = request.POST.get('description', '').strip()
        component.save()
        
        messages.success(request, f'Component "{component.name}" updated successfully.')
        return redirect('ilogic:component_detail', pk=component.pk)
    
    return render(request, 'ilogic/component_form.html', {'edit': True, 'component': component})


@login_required
@require_http_methods(["POST"])
def component_delete(request, pk):
    """Delete a component and all its rules"""
    component = get_object_or_404(Component, pk=pk)
    name = component.name
    assembly_pk = component.assembly.pk
    
    component.delete()
    
    messages.success(request, f'Component "{name}" and all associated rules deleted successfully.')
    return redirect('ilogic:assembly_detail', pk=assembly_pk)


@login_required
def rule_detail(request, pk):
    """View rule details with code and analysis"""
    rule = get_object_or_404(Rule, pk=pk)
    inconsistencies = rule.inconsistencies.filter(status='open').order_by('-severity')
    versions = rule.versions.all().order_by('-version_number')
    
    # Extract data for display
    part_numbers = extract_part_numbers(rule.rule_code)
    
    return render(request, 'ilogic/rule_detail.html', {
        'rule': rule,
        'inconsistencies': inconsistencies,
        'versions': versions,
        'part_numbers': part_numbers,
    })


@login_required
def rule_edit(request, pk):
    """Edit a rule"""
    rule = get_object_or_404(Rule, pk=pk)
    
    if request.method == 'POST':
        # Save current version before updating
        current_version = RuleVersion.objects.filter(rule=rule).order_by('-version_number').first()
        version_number = (current_version.version_number + 1) if current_version else 1
        
        RuleVersion.objects.create(
            rule=rule,
            version_number=version_number,
            code_snapshot=rule.rule_code,
            change_notes=request.POST.get('change_notes', ''),
            created_by=request.user,
        )
        
        # Update rule
        rule.rule_name = request.POST.get('rule_name', '').strip()
        rule.rule_code = request.POST.get('rule_code', '').strip()
        rule.rule_type = determine_rule_type(rule.rule_code)
        rule.triggers = extract_triggers(rule.rule_code)
        rule.extracted_data = {
            'part_numbers': extract_part_numbers(rule.rule_code),
        }
        rule.notes = request.POST.get('notes', '').strip()
        rule.save()
        
        # Re-analyze for inconsistencies
        analyze_rule(rule)
        
        messages.success(request, f'Rule "{rule.rule_name}" updated successfully.')
        return redirect('ilogic:rule_detail', pk=rule.pk)
    
    return render(request, 'ilogic/rule_form.html', {'edit': True, 'rule': rule})


@login_required
@require_http_methods(["POST"])
def rule_delete(request, pk):
    """Delete a rule"""
    rule = get_object_or_404(Rule, pk=pk)
    component_pk = rule.component.pk
    
    rule.delete()
    
    messages.success(request, 'Rule deleted successfully.')
    return redirect('ilogic:component_detail', pk=component_pk)


@login_required
def rule_analyze(request, pk):
    """Analyze a rule for inconsistencies"""
    rule = get_object_or_404(Rule, pk=pk)
    
    # Run analysis
    inconsistencies = detect_inconsistencies(rule.rule_code, rule.rule_name)
    
    # Save inconsistencies to database
    for inc in inconsistencies:
        Inconsistency.objects.get_or_create(
            rule=rule,
            inconsistency_type=inc['type'],
            defaults={
                'severity': inc['severity'],
                'description': inc['description'],
                'code_location': inc.get('code_location', ''),
                'suggested_fix': inc.get('suggested_fix', ''),
                'found_by': request.user,
            }
        )
    
    messages.success(request, f'Analysis complete. Found {len(inconsistencies)} inconsistencies.')
    return redirect('ilogic:rule_detail', pk=rule.pk)


def analyze_rule(rule):
    """Helper function to analyze a rule and create inconsistency records"""
    inconsistencies = detect_inconsistencies(rule.rule_code, rule.rule_name)
    
    for inc in inconsistencies:
        Inconsistency.objects.get_or_create(
            rule=rule,
            component=rule.component,
            assembly=rule.component.assembly,
            inconsistency_type=inc['type'],
            defaults={
                'severity': inc['severity'],
                'description': inc['description'],
                'code_location': inc.get('code_location', ''),
                'suggested_fix': inc.get('suggested_fix', ''),
            }
        )


@login_required
def import_paste(request):
    """Import rules by pasting code"""
    if request.method == 'POST':
        assembly_name = request.POST.get('assembly_name', '').strip()
        code = request.POST.get('code', '').strip()
        
        if not assembly_name or not code:
            messages.error(request, 'Assembly name and code are required.')
            return render(request, 'ilogic/import_paste.html')
        
        # Get or create assembly
        assembly, created = Assembly.objects.get_or_create(
            name=assembly_name,
            defaults={'created_by': request.user}
        )
        
        # Try to extract component name from code
        component_name = parse_component_name_from_code(code) or 'Unknown Component'
        
        # Get or create component
        component, created = Component.objects.get_or_create(
            assembly=assembly,
            name=component_name
        )
        
        # Create rule
        rule_name = request.POST.get('rule_name', 'Imported Rule').strip()
        rule = Rule.objects.create(
            component=component,
            rule_name=rule_name,
            rule_code=code,
            rule_type=determine_rule_type(code),
            triggers=extract_triggers(code),
            extracted_data={
                'part_numbers': extract_part_numbers(code),
            },
            created_by=request.user,
        )
        
        # Analyze for inconsistencies
        analyze_rule(rule)
        
        messages.success(request, f'Rule imported successfully. Found {len(detect_inconsistencies(code))} potential issues.')
        return redirect('ilogic:rule_detail', pk=rule.pk)
    
    return render(request, 'ilogic/import_paste.html')


@login_required
def import_markdown(request):
    """Import from markdown file (single file export)"""
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'Please select a markdown file.')
            return render(request, 'ilogic/import_markdown.html')
        
        try:
            file = request.FILES['file']
            content = file.read().decode('utf-8', errors='ignore')
            
            # Debug: log file size
            print(f"Markdown import: File size: {len(content)} chars")
            print(f"Markdown import: File name: {file.name}")
            print(f"Markdown import: First 500 chars: {content[:500]}")
            
            # Parse markdown (this can take time for large files)
            print(f"Markdown import: Starting parse...")
            import time
            start_time = time.time()
            data = parse_markdown_import(content)
            parse_time = time.time() - start_time
            print(f"Markdown import: Parse completed in {parse_time:.2f} seconds")
            print(f"Markdown import: Parsed assembly: '{data['assembly_name']}', Components: {len(data['components'])}")
            for comp_name, comp_data in data['components'].items():
                print(f"Markdown import: Component '{comp_name}' has {len(comp_data['rules'])} rule(s)")
            
            if not data['assembly_name']:
                error_msg = 'Could not parse assembly name from file. Make sure the file starts with "# Assembly Name"'
                print(f"Markdown import ERROR: {error_msg}")
                messages.error(request, error_msg)
                return render(request, 'ilogic/import_markdown.html', {
                    'debug_info': {
                        'file_size': len(content),
                        'first_chars': content[:200],
                        'assembly_found': False,
                    }
                })
            
            if not data['components']:
                error_msg = 'No rules found in file. Make sure the file contains rules in the format: "## Rule: RuleName" followed by code blocks.'
                print(f"Markdown import ERROR: {error_msg}")
                messages.error(request, error_msg)
                return render(request, 'ilogic/import_markdown.html', {
                    'debug_info': {
                        'file_size': len(content),
                        'assembly_name': data['assembly_name'],
                        'components_found': 0,
                    }
                })
            
            # Get or create assembly
            assembly, created = Assembly.objects.get_or_create(
                name=data['assembly_name'],
                defaults={'created_by': request.user}
            )
            
            imported_count = 0
            total_rules = sum(len(comp_data['rules']) for comp_data in data['components'].values())
            print(f"Markdown import: Processing {total_rules} total rule(s) across {len(data['components'])} component(s)")
            
            process_start = time.time()
            for idx, (comp_name, comp_data) in enumerate(data['components'].items(), 1):
                print(f"Markdown import: Processing component {idx}/{len(data['components'])}: {comp_name}")
                
                # Get or create component
                component, comp_created = Component.objects.get_or_create(
                    assembly=assembly,
                    name=comp_name
                )
                
                # Create rules
                for rule_idx, rule_data in enumerate(comp_data['rules'], 1):
                    if not rule_data.get('code'):
                        continue
                    
                    if rule_idx % 10 == 0:
                        print(f"Markdown import: Processing rule {rule_idx}/{len(comp_data['rules'])} for {comp_name}")
                        
                    rule, rule_created = Rule.objects.get_or_create(
                        component=component,
                        rule_name=rule_data['name'],
                        defaults={
                            'rule_code': rule_data['code'],
                            'rule_type': determine_rule_type(rule_data['code']),
                            'triggers': extract_triggers(rule_data['code']),
                            'extracted_data': {
                                'part_numbers': extract_part_numbers(rule_data['code']),
                            },
                            'created_by': request.user,
                        }
                    )
                    
                    if rule_created:
                        imported_count += 1
                        # Analyze for inconsistencies (this can be slow, do it in background or skip for now)
                        # analyze_rule(rule)  # Commented out to speed up import
            
            process_time = time.time() - process_start
            print(f"Markdown import: Processing completed in {process_time:.2f} seconds")
            
            if imported_count == 0:
                warning_msg = 'No new rules were imported. Rules may already exist.'
                print(f"Markdown import WARNING: {warning_msg}")
                messages.warning(request, warning_msg)
            else:
                success_msg = f'Imported {imported_count} rule(s) from markdown file.'
                print(f"Markdown import SUCCESS: {success_msg}")
                messages.success(request, success_msg)
            
            print(f"Markdown import: Redirecting to assembly {assembly.pk}")
            return redirect('ilogic:assembly_detail', pk=assembly.pk)
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f'Error importing markdown file: {str(e)}'
            print(f"Markdown import EXCEPTION: {error_msg}")
            print(f"Markdown import TRACEBACK: {error_trace}")
            messages.error(request, error_msg)
            return render(request, 'ilogic/import_markdown.html', {
                'error_details': str(e),
                'error_traceback': error_trace,
            })
    
    return render(request, 'ilogic/import_markdown.html')


@login_required
def import_structured(request):
    """Import from structured folder (folder selection)"""
    if request.method == 'POST':
        print(f"Structured import: POST request received")
        print(f"Structured import: FILES keys: {list(request.FILES.keys())}")
        
        if 'files' not in request.FILES:
            error_msg = 'Please select a folder.'
            print(f"Structured import ERROR: {error_msg}")
            messages.error(request, error_msg)
            return render(request, 'ilogic/import_structured.html')
        
        uploaded_files = request.FILES.getlist('files')
        print(f"Structured import: Received {len(uploaded_files)} file(s)")
        
        if not uploaded_files:
            error_msg = 'No files selected. Please select the root folder from your export.'
            print(f"Structured import ERROR: {error_msg}")
            messages.error(request, error_msg)
            return render(request, 'ilogic/import_structured.html')
        
        try:
            # Filter to only .txt files
            txt_files = [f for f in uploaded_files if f.name.endswith('.txt')]
            print(f"Structured import: Found {len(txt_files)} .txt file(s) out of {len(uploaded_files)} total")
            
            if not txt_files:
                error_msg = f'No .txt rule files found in the selected folder. Found {len(uploaded_files)} file(s) but none were .txt files.'
                print(f"Structured import ERROR: {error_msg}")
                print(f"Structured import: File names: {[f.name for f in uploaded_files[:10]]}")
                messages.error(request, error_msg)
                return render(request, 'ilogic/import_structured.html')
            
            # Build file paths from the uploaded files
            # The webkitdirectory input provides the full path in file.name
            # Format is typically: "FolderName/SubFolder/File.txt"
            file_paths = []
            file_contents = {}
            
            for file in txt_files:
                # Get the relative path from the file name
                # The browser provides the full path relative to the selected folder
                rel_path = file.name.replace('\\', '/')
                file_paths.append(rel_path)
                
                # Read file content
                content = file.read().decode('utf-8', errors='ignore')
                file_contents[rel_path] = content
            
            # Parse structure
            print(f"Structured import: Parsing {len(file_paths)} file paths")
            data = parse_structured_import(file_paths)
            print(f"Structured import: Parsed assembly: '{data['assembly_name']}', Components: {len(data['components'])}")
            
            if not data['assembly_name']:
                error_msg = f'Could not determine assembly name from folder structure. File paths: {file_paths[:5]}'
                print(f"Structured import ERROR: {error_msg}")
                messages.error(request, error_msg)
                return render(request, 'ilogic/import_structured.html')
            
            # Get or create assembly
            assembly, created = Assembly.objects.get_or_create(
                name=data['assembly_name'],
                defaults={'created_by': request.user}
            )
            
            imported_count = 0
            
            # Process each component
            for comp_name, comp_data in data['components'].items():
                # Get or create component
                component, comp_created = Component.objects.get_or_create(
                    assembly=assembly,
                    name=comp_name
                )
                
                # Read and process each rule file
                for rule_data in comp_data['rules']:
                    # Get the file content we already read
                    rule_file_path = rule_data.get('file_path')
                    if rule_file_path and rule_file_path in file_contents:
                        rule_code = file_contents[rule_file_path]
                        
                        # Create rule
                        rule, rule_created = Rule.objects.get_or_create(
                            component=component,
                            rule_name=rule_data['name'],
                            defaults={
                                'rule_code': rule_code,
                                'rule_type': determine_rule_type(rule_code),
                                'triggers': extract_triggers(rule_code),
                                'extracted_data': {
                                    'part_numbers': extract_part_numbers(rule_code),
                                },
                                'created_by': request.user,
                            }
                        )
                        
                        if rule_created:
                            imported_count += 1
                            # Analyze for inconsistencies (can be slow - do after import or in background)
                            # analyze_rule(rule)  # Commented out to speed up import
            
            success_msg = f'Imported {imported_count} rule(s) from structured folder.'
            print(f"Structured import SUCCESS: {success_msg}")
            messages.success(request, success_msg)
            return redirect('ilogic:assembly_detail', pk=assembly.pk)
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f'Error importing structured folder: {str(e)}'
            print(f"Structured import EXCEPTION: {error_msg}")
            print(f"Structured import TRACEBACK: {error_trace}")
            messages.error(request, error_msg)
            return render(request, 'ilogic/import_structured.html', {
                'error_details': str(e),
                'error_traceback': error_trace,
            })
    
    return render(request, 'ilogic/import_structured.html')


@login_required
def analysis_dashboard(request):
    """Dashboard showing all inconsistencies and analysis"""
    inconsistencies = Inconsistency.objects.filter(status='open').order_by('-severity', '-found_at')
    
    # Group by type
    by_type = {}
    for inc in inconsistencies:
        inc_type = inc.get_inconsistency_type_display()
        if inc_type not in by_type:
            by_type[inc_type] = []
        by_type[inc_type].append(inc)
    
    # Stats
    total_critical = inconsistencies.filter(severity='critical').count()
    total_warning = inconsistencies.filter(severity='warning').count()
    total_info = inconsistencies.filter(severity='info').count()
    
    return render(request, 'ilogic/analysis_dashboard.html', {
        'inconsistencies': inconsistencies,
        'by_type': by_type,
        'total_critical': total_critical,
        'total_warning': total_warning,
        'total_info': total_info,
    })


@login_required
def assembly_analysis(request, pk):
    """Analysis report for a specific assembly"""
    assembly = get_object_or_404(Assembly, pk=pk)
    inconsistencies = Inconsistency.objects.filter(
        assembly=assembly,
        status='open'
    ).order_by('-severity', '-found_at')
    
    return render(request, 'ilogic/assembly_analysis.html', {
        'assembly': assembly,
        'inconsistencies': inconsistencies,
    })


@login_required
def inconsistency_list(request):
    """List all inconsistencies"""
    status_filter = request.GET.get('status', 'open')
    severity_filter = request.GET.get('severity', '')
    
    inconsistencies = Inconsistency.objects.all()
    
    if status_filter:
        inconsistencies = inconsistencies.filter(status=status_filter)
    if severity_filter:
        inconsistencies = inconsistencies.filter(severity=severity_filter)
    
    inconsistencies = inconsistencies.order_by('-severity', '-found_at')
    
    return render(request, 'ilogic/inconsistency_list.html', {
        'inconsistencies': inconsistencies,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
    })


@login_required
def inconsistency_detail(request, pk):
    """View inconsistency details"""
    inconsistency = get_object_or_404(Inconsistency, pk=pk)
    
    return render(request, 'ilogic/inconsistency_detail.html', {
        'inconsistency': inconsistency,
    })


@login_required
def inconsistency_fix(request, pk):
    """Mark inconsistency as fixed"""
    inconsistency = get_object_or_404(Inconsistency, pk=pk)
    
    if request.method == 'POST':
        inconsistency.status = 'fixed'
        inconsistency.fixed_by = request.user
        from django.utils import timezone
        inconsistency.fixed_at = timezone.now()
        inconsistency.save()
        
        messages.success(request, 'Inconsistency marked as fixed.')
        return redirect('ilogic:inconsistency_detail', pk=pk)
    
    return render(request, 'ilogic/inconsistency_fix.html', {
        'inconsistency': inconsistency,
    })


@login_required
def configurator_list(request):
    """List all configurators"""
    configurators = Configurator.objects.all().order_by('assembly', 'name')
    
    return render(request, 'ilogic/configurator_list.html', {
        'configurators': configurators,
    })


@login_required
def configurator_create(request):
    """Create a new configurator"""
    if request.method == 'POST':
        assembly_pk = request.POST.get('assembly')
        name = request.POST.get('name', '').strip()
        
        if not assembly_pk or not name:
            messages.error(request, 'Assembly and name are required.')
            assemblies = Assembly.objects.all()
            return render(request, 'ilogic/configurator_form.html', {
                'edit': False,
                'assemblies': assemblies,
            })
        
        assembly = get_object_or_404(Assembly, pk=assembly_pk)
        configurator = Configurator.objects.create(
            assembly=assembly,
            name=name,
            created_by=request.user,
        )
        
        messages.success(request, f'Configurator "{name}" created successfully.')
        return redirect('ilogic:configurator_detail', pk=configurator.pk)
    
    assemblies = Assembly.objects.all()
    return render(request, 'ilogic/configurator_form.html', {
        'edit': False,
        'assemblies': assemblies,
    })


@login_required
def configurator_detail(request, pk):
    """View configurator and run simulations"""
    configurator = get_object_or_404(Configurator, pk=pk)
    
    return render(request, 'ilogic/configurator_detail.html', {
        'configurator': configurator,
    })


@login_required
def configurator_simulate(request, pk):
    """Simulate rule execution with given parameters"""
    configurator = get_object_or_404(Configurator, pk=pk)
    
    if request.method == 'POST':
        # Get input parameters from form
        input_params = {}
        for key, value in request.POST.items():
            if key.startswith('param_'):
                param_name = key.replace('param_', '')
                input_params[param_name] = value
        
        # TODO: Implement rule execution simulation
        # For now, just return the parameters
        configurator.input_parameters = input_params
        configurator.simulation_results = {
            'status': 'simulated',
            'parameters': input_params,
            'bom': {},  # Will be generated by simulation engine
        }
        configurator.save()
        
        messages.success(request, 'Simulation completed.')
        return redirect('ilogic:configurator_detail', pk=configurator.pk)
    
    return redirect('ilogic:configurator_detail', pk=configurator.pk)
