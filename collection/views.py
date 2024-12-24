

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
        'total_uploads': DataUpload.objects.count(),
        'pending_count': DataUpload.objects.filter(status='pending').count(),
        'approved_count': DataUpload.objects.filter(status='approved').count(),
        'rejected_count': DataUpload.objects.filter(status='rejected').count(),
    }
    
    # Get recent uploads (last 5)
    recent_uploads = DataUpload.objects.all().order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_uploads': recent_uploads,
    }
    
    return render(request, 'collection/home.html', context)

@login_required
def upload_data(request):
    template_type = request.GET.get('type')
    if not template_type or template_type not in dict(DataTemplate.TEMPLATE_TYPES):
        return HttpResponseBadRequest("Invalid template type")
       
    try:
        # Get the template for this type
        template = DataTemplate.objects.get(template_type=template_type)
        template_headers = template.required_headers.get('headers', [])
    except DataTemplate.DoesNotExist:
        template_headers = []

    if request.method == 'POST':
        form = DataUploadForm(request.POST, request.FILES, template_type=template_type)
        if form.is_valid():
            upload = form.save()
            # Start validation process
            validation_result = upload.start_validation()
            
            if validation_result:
                messages.success(request, 'File uploaded and validated successfully!')
            else:
                messages.warning(request, 'File uploaded but validation failed. Check validation details.')
            
            return redirect('upload_list')
    else:
        form = DataUploadForm(template_type=template_type)

    context = {
        'form': form,
        'template_type': template_type,
        'template_name': dict(DataTemplate.TEMPLATE_TYPES)[template_type],
        'template_headers': template_headers,  # Add the headers to context
    }
    return render(request, 'collection/upload.html', context)


@login_required
def upload_list(request):
    uploads = DataUpload.objects.all().order_by('-created_at')
    
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
    uploads = DataUpload.objects.all().order_by('-created_at')
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