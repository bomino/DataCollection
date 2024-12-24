

# collection/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .forms import DataUploadForm
from .models import DataUpload, DataTemplate
from django.http import FileResponse
from django.conf import settings
import os
from pathlib import Path
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .utils import TEMPLATE_HEADERS
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required
def home(request):
    # Get upload statistics
    stats = {
        'total_uploads': DataUpload.objects.filter(user=request.user).count(),
        'pending_count': DataUpload.objects.filter(user=request.user,status='pending').count(),
        'approved_count': DataUpload.objects.filter(user=request.user,status='approved').count(),
        'rejected_count': DataUpload.objects.filter(user=request.user,status='rejected').count(),
    }
    
    # Get recent uploads (last 5)
    recent_uploads = DataUpload.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_uploads': recent_uploads
    }
    
    return render(request, 'collection/home.html', context)

@login_required
def upload_data(request):
    template_type = request.GET.get('type')
    if not template_type or template_type not in dict(DataTemplate.TEMPLATE_TYPES):
        return HttpResponseBadRequest("Invalid template type")
       
    try:
        template = DataTemplate.objects.get(template_type=template_type)
        template_headers = template.required_headers.get('headers', [])
    except DataTemplate.DoesNotExist:
        template_headers = []

    if request.method == 'POST':
        form = DataUploadForm(request.POST, request.FILES, template_type=template_type)
        form.user = request.user
        if form.is_valid():
            upload = form.save()
            # Let's add some debug print statements
            print(f"Validation result before: {upload.status}")
            validation_result = upload.start_validation()
            print(f"Validation result after: {validation_result}")
            print(f"Validation errors: {upload.validation_errors}")
            
            if validation_result:
                messages.success(request, 'File uploaded and validated successfully!')
            else:
                messages.warning(request, f'File uploaded but validation failed. Details: {upload.validation_errors}')
            
            return redirect('upload_list')
    else:
        form = DataUploadForm(template_type=template_type)

    context = {
        'form': form,
        'template_type': template_type,
        'template_name': dict(DataTemplate.TEMPLATE_TYPES)[template_type],
        'template_headers': template_headers,
    }
    return render(request, 'collection/upload.html', context)


@login_required
def upload_list(request):
    uploads = DataUpload.objects.filter(user=request.user).order_by('-created_at')
    
    # Debug: Print validation errors for each upload
    for upload in uploads:
        if upload.validation_errors:
            print(f"Upload ID {upload.id} validation errors: {upload.validation_errors}")
            print(f"Validation message: {upload.get_validation_message()}")
    
    context = {
        'uploads': uploads,
        'debug': settings.DEBUG  # Pass DEBUG setting to template
    }
    return render(request, 'collection/upload_list.html', context)



@login_required
def download_template(request, template_type):
    """
    Handle template downloads for different data types
    Returns a CSV template file for the specified type
    """
    template_files = {
        'vendor': 'vendor_master.csv',
        'item': 'item_master.csv',
        'purchase': 'purchase_history.csv',
        'invoice': 'invoice_data.csv',
        'contract': 'contracts.csv',
        'facility': 'facilities.csv',
        'department': 'departments.csv',
    }
   
    try:
        # Validate template type
        if template_type not in template_files:
            messages.error(request, f'Invalid template type requested: {template_type}')
            return redirect('home')
       
        file_path = Path(settings.STATIC_ROOT) / 'templates' / template_files[template_type]
       
        # Check if template file exists
        if not file_path.exists():
            messages.error(request, f'Template file not found: {template_files[template_type]}')
            return redirect('home')
       
        # Serve the file
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="{template_files[template_type]}"'
       
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading template: {str(e)}')
        return redirect('home')

@login_required
def upload_list(request):
    uploads = DataUpload.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'collection/upload_list.html', {
        'uploads': uploads,
        'page_title': 'Uploaded Files'
    })


@require_POST
def delete_upload(request, pk):
    try:
        upload = get_object_or_404(DataUpload, pk=pk)
        filename = upload.filename  # Get filename before deletion
        upload.delete()
        messages.success(request, f'File "{filename}" was successfully deleted.')
        return JsonResponse({
            'status': 'success',
            'message': 'File deleted successfully'
        })
    except DataUpload.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'File not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@login_required
def generic_upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        file_type = request.POST.get('file_type')
        notes = request.POST.get('notes', '')
       
        uploaded_files = []
        errors = []

        for file in files:
            # Check file size
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                errors.append(f"File {file.name} exceeds 10MB limit")
                continue

            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            filename_without_ext = os.path.splitext(file.name)[0]
            allowed_extensions = {
                'excel': ['.xlsx', '.xls'],
                'csv': ['.csv'],
                'text': ['.txt'],
                'pdf': ['.pdf']
            }

            if ext not in allowed_extensions.get(file_type, []):
                errors.append(f"File {file.name} has invalid extension for type {file_type}")
                continue

            try:
                # Generate data_type from notes or filename
                data_type = notes.split('\n')[0] if notes else filename_without_ext

                # Create upload record
                upload = DataUpload(
                    file=file,
                    file_type=file_type,
                    data_type=data_type[:100],  # Limit to 100 characters
                    template_type='generic',
                    status='pending',
                    user=request.user
                )
                if notes:
                    upload.notes = notes
                upload.save()
               
                uploaded_files.append({
                    'name': file.name,
                    'size': file.size,
                    'id': upload.id,
                    'type': data_type  # Include the data_type in response
                })
            except Exception as e:
                errors.append(f"Error uploading {file.name}: {str(e)}")

        return JsonResponse({
            'status': 'success' if not errors else 'partial',
            'uploaded_files': uploaded_files,
            'errors': errors
        })

    return render(request, 'collection/generic_upload.html')


@login_required
def download_file(request, upload_id):
    upload = get_object_or_404(DataUpload, id=upload_id)
    
    # Check if user owns the file or is superuser
    if upload.user != request.user and not request.user.is_superuser:
        raise Http404("File not found")
        
    # Your file serving logic here
    response = FileResponse(upload.file)
    return response


@login_required
def api_test(request):
    return render(request, 'collection/api_test.html')