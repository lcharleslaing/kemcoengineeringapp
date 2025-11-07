"""
Utility functions for parsing, analyzing, and processing iLogic rules
"""
import re
import json
from typing import Dict, List, Tuple, Optional


def parse_component_name_from_code(code: str) -> Optional[str]:
    """
    Extract component name from iLogic code.
    Looks for patterns like:
    - Parameter("RFSO FLANGE 150LB:1", ...)
    - iProperties.Value("PIPE SS304 S-5 22.5 DEG.:1", ...)
    """
    # Pattern to match component names in Parameter() or iProperties.Value() calls
    patterns = [
        r'Parameter\("([^"]+)"',
        r'iProperties\.Value\("([^"]+)"',
        r'Parameter\([\'"]([^\'"]+)[\'"]',
        r'iProperties\.Value\([\'"]([^\'"]+)[\'"]',
    ]
    
    component_names = set()
    for pattern in patterns:
        matches = re.findall(pattern, code, re.IGNORECASE)
        component_names.update(matches)
    
    # Return the most common component name (if multiple found)
    if component_names:
        # Count occurrences
        counts = {}
        for name in component_names:
            count = code.count(f'"{name}"')
            counts[name] = count
        
        # Return the most frequently referenced component
        return max(counts.items(), key=lambda x: x[1])[0]
    
    return None


def extract_triggers(code: str) -> List[str]:
    """
    Extract parameter names that trigger rules.
    Looks for patterns like:
    - If FlangeSize = ...
    - Parameter("...", "FlangeSize")
    - MATERIAL = "SS304"
    """
    triggers = set()
    
    # Pattern for If statements with parameters
    if_pattern = r'If\s+(\w+)\s*[=<>]'
    matches = re.findall(if_pattern, code, re.IGNORECASE)
    triggers.update(matches)
    
    # Pattern for Parameter() calls
    param_pattern = r'Parameter\([^,]+,\s*["\'](\w+)["\']'
    matches = re.findall(param_pattern, code, re.IGNORECASE)
    triggers.update(matches)
    
    # Pattern for variable assignments
    assign_pattern = r'(\w+)\s*=\s*["\']'
    matches = re.findall(assign_pattern, code, re.IGNORECASE)
    # Filter out common VBA keywords
    vba_keywords = {'dim', 'if', 'then', 'else', 'end', 'sub', 'function', 'as', 'string', 'integer', 'boolean'}
    triggers.update([m for m in matches if m.lower() not in vba_keywords])
    
    return sorted(list(triggers))


def extract_part_numbers(code: str) -> List[Dict[str, str]]:
    """
    Extract part numbers from iLogic code.
    Returns list of dicts with: part_number, component, description, size
    """
    part_numbers = []
    
    # Pattern for KEMCO PART NUMBER assignments
    # iProperties.Value("Component:1", "Custom", "KEMCO PART NUMBER") = "800-08-009"
    pattern = r'iProperties\.Value\(["\']([^"\']+)["\'][^,]+,\s*["\']KEMCO PART NUMBER["\'][^=]*=\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, code, re.IGNORECASE)
    
    for component, part_num in matches:
        # Try to extract description
        desc_pattern = rf'iProperties\.Value\(["\']{re.escape(component)}["\'][^,]+,\s*["\']KEMCO DESCRIPTION["\'][^=]*=\s*["\']([^"\']+)["\']'
        desc_match = re.search(desc_pattern, code, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ''
        
        # Try to extract size from description or code
        size = None
        size_patterns = [
            r'(\d+(?:\.\d+)?)"',  # e.g., "2"", "1.5""
            r'(\d+(?:\.\d+)?)\s*inch',
        ]
        for sp in size_patterns:
            size_match = re.search(sp, description, re.IGNORECASE)
            if size_match:
                size = size_match.group(1)
                break
        
        part_numbers.append({
            'component': component,
            'part_number': part_num,
            'description': description,
            'size': size,
        })
    
    return part_numbers


def detect_inconsistencies(code: str, rule_name: str = '') -> List[Dict]:
    """
    Detect inconsistencies in iLogic code.
    Returns list of inconsistency dicts.
    """
    inconsistencies = []
    
    # Check for missing part numbers (XXX placeholders)
    xxx_pattern = r'["\']([\w-]+-XXX)["\']'
    xxx_matches = re.findall(xxx_pattern, code, re.IGNORECASE)
    for match in xxx_matches:
        inconsistencies.append({
            'type': 'missing_part_number',
            'severity': 'critical',
            'description': f'Missing part number placeholder found: {match}',
            'code_location': f'Contains "{match}"',
            'suggested_fix': f'Replace {match} with actual part number',
        })
    
    # Check for description mismatches (SS316 code saying SS304)
    if 'SS316' in code.upper() or 'MATERIAL = "SS316"' in code:
        # Check if descriptions say SS304 when they should say SS316
        desc_pattern = r'KEMCO DESCRIPTION["\'][^=]*=\s*["\']([^"\']*SS304[^"\']*)["\']'
        desc_matches = re.findall(desc_pattern, code, re.IGNORECASE)
        for match in desc_matches:
            if 'SS316' in code.upper() and 'SS304' in match.upper():
                inconsistencies.append({
                    'type': 'description_mismatch',
                    'severity': 'warning',
                    'description': f'Description says SS304 but code handles SS316: {match[:50]}',
                    'code_location': 'Description assignment',
                    'suggested_fix': 'Change SS304 to SS316 in description',
                })
    
    # Check for duplicate part numbers (same part number used for different sizes/materials)
    part_numbers = extract_part_numbers(code)
    part_num_counts = {}
    for pn in part_numbers:
        key = pn['part_number']
        if key not in part_num_counts:
            part_num_counts[key] = []
        part_num_counts[key].append(pn)
    
    for part_num, occurrences in part_num_counts.items():
        if len(occurrences) > 1:
            # Check if they're for different conditions
            sizes = set([o.get('size') for o in occurrences if o.get('size')])
            if len(sizes) > 1:
                inconsistencies.append({
                    'type': 'duplicate_part_number',
                    'severity': 'warning',
                    'description': f'Part number {part_num} used for multiple sizes: {", ".join(sizes)}',
                    'code_location': 'Multiple part number assignments',
                    'suggested_fix': 'Verify if same part number should be used for different sizes',
                })
    
    # Check for missing conditions (e.g., ElseIf without If)
    if_count = len(re.findall(r'\bIf\b', code, re.IGNORECASE))
    elseif_count = len(re.findall(r'\bElseIf\b', code, re.IGNORECASE))
    end_if_count = len(re.findall(r'\bEnd If\b', code, re.IGNORECASE))
    
    if if_count != end_if_count:
        inconsistencies.append({
            'type': 'logic_inconsistency',
            'severity': 'critical',
            'description': f'Mismatched If/End If statements: {if_count} If, {end_if_count} End If',
            'code_location': 'If/End If blocks',
            'suggested_fix': 'Ensure all If statements have matching End If',
        })
    
    return inconsistencies


def parse_markdown_import(content: str) -> Dict:
    """
    Parse markdown file from single-file export.
    Returns structured data ready for import.
    """
    data = {
        'assembly_name': '',
        'components': {},
    }
    
    # Extract assembly name from first heading
    assembly_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if assembly_match:
        data['assembly_name'] = assembly_match.group(1).strip()
    
    # Parse rules - more flexible pattern
    # Pattern: ## Rule: RuleName
    # *Component: [[ComponentName]]*
    # *Path: `path`* (optional)
    # ```vbnet or ```vb or ```
    # code
    # ```
    
    # Try multiple patterns for flexibility
    # Pattern 1: Full format with Path (non-greedy to avoid matching too much)
    rule_pattern1 = r'## Rule:\s*(.+?)\n\*Component:\s*\[\[(.+?)\]\]\*\n(?:\*Path:\s*`(.+?)`\*\n)?\n?```(?:vbnet|vb)?\n(.*?)```'
    matches1 = re.findall(rule_pattern1, content, re.DOTALL | re.MULTILINE)
    
    # Pattern 2: Without Path line
    rule_pattern2 = r'## Rule:\s*(.+?)\n\*Component:\s*\[\[(.+?)\]\]\*\n\n```(?:vbnet|vb)?\n(.*?)```'
    matches2 = re.findall(rule_pattern2, content, re.DOTALL | re.MULTILINE)
    
    # Pattern 3: More flexible - handle variations in spacing/newlines
    rule_pattern3 = r'## Rule:\s*(.+?)\n\*Component:\s*\[\[(.+?)\]\]\*.*?```(?:vbnet|vb)?\n(.*?)```'
    matches3 = re.findall(rule_pattern3, content, re.DOTALL | re.MULTILINE)
    
    # Combine matches (avoid duplicates)
    all_matches = []
    seen_rules = set()
    
    for match in matches1:
        rule_name = match[0].strip()
        component_name = match[1].strip()
        # Handle different match lengths (with or without path)
        if len(match) == 4:
            path = match[2] if match[2] else ''
            code = match[3]
        elif len(match) == 3:
            path = ''
            code = match[2]
        else:
            continue
        
        key = (rule_name, component_name)
        if key not in seen_rules:
            seen_rules.add(key)
            all_matches.append((rule_name, component_name, path, code))
    
    for match in matches2:
        rule_name = match[0].strip()
        component_name = match[1].strip()
        code = match[2] if len(match) > 2 else ''
        path = ''
        
        key = (rule_name, component_name)
        if key not in seen_rules:
            seen_rules.add(key)
            all_matches.append((rule_name, component_name, path, code))
    
    # Add pattern 3 matches
    for match in matches3:
        rule_name = match[0].strip()
        component_name = match[1].strip()
        code = match[2] if len(match) > 2 else ''
        path = ''
        
        key = (rule_name, component_name)
        if key not in seen_rules:
            seen_rules.add(key)
            all_matches.append((rule_name, component_name, path, code))
    
    # Process matches
    for rule_name, component_name, path, code in all_matches:
        if not component_name or not rule_name:
            continue
            
        if component_name not in data['components']:
            data['components'][component_name] = {
                'name': component_name,
                'path': path,
                'rules': [],
            }
        
        data['components'][component_name]['rules'].append({
            'name': rule_name.strip(),
            'code': code.strip(),
        })
    
    return data


def parse_structured_import(file_paths: List[str]) -> Dict:
    """
    Parse structured folder export from Inventor.
    file_paths should be list of relative file paths from the selected folder.
    Returns structured data ready for import.
    
    Expected structure (from Inventor structured export rule):
    - RootFolder/ComponentFolder/DocumentName__RuleName.txt
    - Or: RootFolder/DocumentName__RuleName.txt (root level)
    
    The export rule creates:
    - Folder structure matching assembly hierarchy
    - Files named: DocumentName__RuleName.txt
    """
    data = {
        'assembly_name': '',
        'components': {},
    }
    
    if not file_paths:
        return data
    
    # Normalize all paths
    normalized_paths = [p.replace('\\', '/') for p in file_paths]
    
    # Extract assembly name from root folder
    # File paths are like: RootFolder/ComponentFolder/DocumentName__RuleName.txt
    # Or just: RootFolder/DocumentName__RuleName.txt
    first_path = normalized_paths[0]
    parts = first_path.split('/')
    
    # Root folder is the first part
    if len(parts) > 0:
        root_folder = parts[0]
        data['assembly_name'] = root_folder
    
    for file_path in normalized_paths:
        parts = file_path.split('/')
        filename = parts[-1]  # DocumentName__RuleName.txt
        
        # Skip if not a .txt file
        if not filename.endswith('.txt'):
            continue
        
        # Extract document name and rule name from filename
        # Format from Inventor: DocumentName__RuleName.txt
        name_part = filename.replace('.txt', '')
        if '__' in name_part:
            # Split on last '__' to handle cases where document name might contain '__'
            doc_name, rule_name = name_part.rsplit('__', 1)
        else:
            # No separator, use filename as rule name
            doc_name = name_part
            rule_name = 'Main'
        
        # Determine component name from folder structure
        # The structured export creates folders matching component names
        if len(parts) >= 3:
            # Has component folder: RootFolder/ComponentFolder/File.txt
            # Component folder name is the component
            component_name = parts[-2]  # Component folder name
        elif len(parts) == 2:
            # Root level: RootFolder/File.txt
            # Use document name as component name (rule is at root level)
            component_name = doc_name
        else:
            # Just filename (shouldn't happen, but handle it)
            component_name = doc_name
        
        # Initialize component if needed
        if component_name not in data['components']:
            data['components'][component_name] = {
                'name': component_name,
                'document_name': doc_name,
                'rules': [],
            }
        
        # Add rule with file path for later reading
        data['components'][component_name]['rules'].append({
            'name': rule_name,
            'file_path': file_path,  # Keep original path for file reading
        })
    
    return data


def determine_rule_type(code: str) -> str:
    """
    Determine the type of rule based on code content.
    """
    code_upper = code.upper()
    
    if 'KEMCO PART NUMBER' in code_upper:
        if 'PARAMETER' in code_upper:
            return 'mixed'
        return 'part_number'
    elif 'KEMCO DESCRIPTION' in code_upper:
        return 'description'
    elif 'PARAMETER(' in code_upper and '=' in code_upper:
        return 'parameter'
    elif 'IPROPERTIES' in code_upper:
        return 'iproperty'
    else:
        return 'other'

