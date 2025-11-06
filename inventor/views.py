import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Inventor file extensions
INVENTOR_EXTENSIONS = {
    '.ipt',  # Part file
    '.iam',  # Assembly file
    '.idw',  # Drawing file
    '.ipn',  # Presentation file
    '.dwg',  # AutoCAD drawing (often used with Inventor)
    '.pdf',  # PDF files (often exported from Inventor)
    '.xls',  # Excel files (often used with Inventor)
    '.xlsx',  # Excel files
    '.doc',  # Word files
    '.docx',  # Word files
    '.txt',  # Text files
    '.xml',  # XML files
    '.step',  # STEP files
    '.stp',  # STEP files
    '.iges',  # IGES files
    '.igs',  # IGES files
}

# BASE_PATH can be configured via environment variable or use default
try:
    BASE_PATH = os.getenv('INVENTOR_WORKING_FOLDER', r'C:\$WorkingFolder')
except Exception as e:
    # Fallback if there's any issue getting the path
    BASE_PATH = r'C:\$WorkingFolder'
    print(f"Warning: Could not get INVENTOR_WORKING_FOLDER from environment: {e}")


def is_inventor_file(filename):
    """Check if file has an Inventor-related extension"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in INVENTOR_EXTENSIONS


@login_required
def inventor_list(request):
    """List all Inventor-related files in the working folder - search-only mode for performance"""
    try:
        search_query = request.GET.get('q', '').strip().lower()
        
        files = []
        path_exists = False
        path_error = None
        
        # Check if path exists and is accessible
        normalized_path = None
        try:
            if not BASE_PATH:
                path_error = "BASE_PATH is not configured"
                path_exists = False
            else:
                # Normalize the path - handle $ character and other special cases
                normalized_path = os.path.normpath(BASE_PATH)
                try:
                    path_exists = os.path.exists(normalized_path) and os.path.isdir(normalized_path)
                except (OSError, ValueError) as path_check_error:
                    path_error = f"Error checking path '{normalized_path}': {str(path_check_error)}"
                    path_exists = False
        except Exception as e:
            path_error = f"Error checking path: {str(e)}"
            import traceback
            print(f"Error checking BASE_PATH '{BASE_PATH}': {traceback.format_exc()}")
            path_exists = False
        
        # Only scan files if search query is provided (performance optimization)
        if path_exists and normalized_path and search_query:
            try:
                # Performance limits for search results
                max_results = 5000  # Limit search results
                result_count = 0
                total_files_scanned = 0
                max_files_to_scan = 100000  # Stop scanning after this many files checked
                
                for root, dirs, filenames in os.walk(normalized_path):
                    # Performance check: stop scanning if we've checked too many files
                    if total_files_scanned >= max_files_to_scan:
                        if not path_error:
                            path_error = f"Note: Scanned {total_files_scanned:,} files. Showing first {result_count:,} results. Try a more specific search."
                        break
                    
                    # Stop if we have enough results
                    if result_count >= max_results:
                        if not path_error:
                            path_error = f"Note: Found {result_count:,} matching files. Showing first {max_results:,} results. Try a more specific search."
                        break
                    
                    for filename in filenames:
                        total_files_scanned += 1
                        
                        # Quick extension check first
                        if not is_inventor_file(filename):
                            continue
                        
                        # Quick search filter - check filename before expensive operations
                        filename_lower = filename.lower()
                        if search_query not in filename_lower:
                            # Also check path if available
                            try:
                                file_path = os.path.join(root, filename)
                                rel_path = os.path.relpath(file_path, normalized_path)
                                if search_query not in rel_path.lower():
                                    continue
                            except:
                                continue
                        
                        try:
                            file_path = os.path.join(root, filename)
                            try:
                                rel_path = os.path.relpath(file_path, normalized_path)
                            except ValueError:
                                rel_path = file_path
                            
                            # Get file stats
                            try:
                                stat = os.stat(file_path)
                                file_size = stat.st_size
                                modified_time = stat.st_mtime
                            except (OSError, PermissionError):
                                continue
                            
                            # Get directory
                            dir_path = os.path.dirname(rel_path)
                            if dir_path == '.' or dir_path == '':
                                dir_path = 'Root'
                            
                            files.append({
                                'name': filename,
                                'path': file_path,
                                'relative_path': rel_path,
                                'directory': dir_path,
                                'size': file_size,
                                'modified': modified_time,
                                'extension': os.path.splitext(filename)[1].lower()
                            })
                            result_count += 1
                            
                            # Stop if we have enough results
                            if result_count >= max_results:
                                break
                        except Exception:
                            continue
                    
                    if result_count >= max_results:
                        break
            except (PermissionError, OSError) as e:
                # Handle permission errors or other issues
                path_error = f"Permission error or path issue: {str(e)}"
                import traceback
                print(f"Error walking BASE_PATH: {traceback.format_exc()}")
            except Exception as e:
                # Handle any other unexpected errors
                path_error = f"Unexpected error: {str(e)}"
                import traceback
                print(f"Unexpected error in os.walk: {traceback.format_exc()}")
        
        # Sort by modified time (newest first) - files are already filtered by search query
        try:
            files.sort(key=lambda x: x['modified'], reverse=True)
        except (KeyError, TypeError):
            # If modified time is missing, sort by name
            files.sort(key=lambda x: x.get('name', ''))
        
        # Format file sizes
        from datetime import datetime
        for file in files:
            size = file.get('size', 0)
            if size < 1024:
                file['size_str'] = f"{size} B"
            elif size < 1024 * 1024:
                file['size_str'] = f"{size / 1024:.1f} KB"
            else:
                file['size_str'] = f"{size / (1024 * 1024):.1f} MB"
            
            # Format modified time
            modified = file.get('modified', 0)
            try:
                file['modified_str'] = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, OSError):
                file['modified_str'] = 'Unknown'
        
        context = {
            'files': files,
            'base_path': BASE_PATH or 'Not configured',
            'search_query': search_query or '',
            'path_exists': path_exists,
            'path_error': path_error or '',
        }
        
        return render(request, 'inventor/list.html', context)
    except Exception as e:
        # Catch any unexpected errors and return a safe response
        import traceback
        from django.http import HttpResponse
        
        error_details = traceback.format_exc()
        print(f"Error in inventor_list: {error_details}")
        
        # Try to render template, but if that fails, return a simple error response
        try:
            context = {
                'files': [],
                'base_path': BASE_PATH or 'Not configured',
                'search_query': '',
                'path_exists': False,
                'path_error': f"Unexpected error: {str(e)}",
            }
            return render(request, 'inventor/list.html', context)
        except Exception as template_error:
            # If template rendering fails, return a simple error message
            return HttpResponse(f"Error loading Inventor files: {str(e)}<br><br>Template error: {str(template_error)}<br><br>Details: {error_details}", status=500)


@login_required
def inventor_open_file(request, file_path_encoded):
    """Return file path for Electron to open"""
    import urllib.parse
    from django.http import JsonResponse
    
    # Decode the file path
    try:
        file_path = urllib.parse.unquote(file_path_encoded)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid file path'}, status=400)
    
    # Security check - ensure file is within base path
    if not os.path.abspath(file_path).startswith(os.path.abspath(BASE_PATH)):
        return JsonResponse({'success': False, 'error': 'File path not allowed'}, status=403)
    
    if not os.path.exists(file_path):
        return JsonResponse({'success': False, 'error': 'File not found'}, status=404)
    
    # Return the file path for Electron to open
    return JsonResponse({'success': True, 'file_path': file_path})


@login_required
def inventor_open_location(request, file_path_encoded):
    """Open the file location in Windows Explorer"""
    import urllib.parse
    import subprocess
    from django.http import JsonResponse
    
    # Decode the file path
    try:
        file_path = urllib.parse.unquote(file_path_encoded)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid file path'}, status=400)
    
    # Security check - ensure file is within base path
    try:
        if not os.path.abspath(file_path).startswith(os.path.abspath(BASE_PATH)):
            return JsonResponse({'success': False, 'error': 'File path not allowed'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Path validation error: {str(e)}'}, status=500)
    
    if not os.path.exists(file_path):
        return JsonResponse({'success': False, 'error': 'File not found'}, status=404)
    
    # Get the directory containing the file
    directory = os.path.dirname(file_path)
    
    # Open in Windows Explorer
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer /select,"{file_path}"')
        elif os.name == 'posix':  # Linux/Mac
            subprocess.Popen(['xdg-open', directory])
        return JsonResponse({'success': True, 'message': 'Location opened'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
