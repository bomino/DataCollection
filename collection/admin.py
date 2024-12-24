# collection/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django import forms
from django.contrib import messages
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import DataTemplate, DataUpload

class CustomAdminSite(AdminSite):
    site_title = "MAP Admin"
    site_header = "Data Collection Portal"
    index_title = "Portal Administration"
    
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Add counts to app titles
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            for model in app['models']:
                if model['object_name'] == 'DataUpload':
                    model['name'] = f"Data Uploads ({DataUpload.objects.count()})"
                elif model['object_name'] == 'DataTemplate':
                    model['name'] = f"Data Templates ({DataTemplate.objects.count()})"
        
        return app_list

admin_site = CustomAdminSite(name='custom_admin')

class DataTemplateResource(resources.ModelResource):
    class Meta:
        model = DataTemplate
        import_id_fields = ['name']
        fields = ('name', 'template_type', 'description', 'required_headers')

@admin.register(DataTemplate)
class DataTemplateAdmin(ImportExportModelAdmin):
    resource_class = DataTemplateResource
    list_display = ('name', 'template_type', 'header_count', 'created_at', 'updated_at')
    list_filter = ('template_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'header_preview')
    save_on_top = True
    
    fieldsets = (
        (None, {
            'fields': ('name', 'template_type', 'description')
        }),
        ('Configuration', {
            'fields': ('required_headers', 'header_preview'),
            'classes': ('collapse',),
            'description': 'Template configuration and header information'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Creation and modification timestamps'
        }),
    )

    def header_count(self, obj):
        count = len(obj.required_headers.get('headers', []))
        return format_html('<span class="badge bg-info">{}</span>', count)
    header_count.short_description = 'Required Headers'

    def header_preview(self, obj):
        headers = obj.required_headers.get('headers', [])
        if not headers:
            return "No headers defined"
        
        html = '<div class="header-preview">'
        for header in headers:
            html += f'<span class="badge bg-primary me-1 mb-1">{header}</span>'
        html += '</div>'
        return format_html(html)
    header_preview.short_description = 'Header Preview'

@admin.register(DataUpload)
class DataUploadAdmin(ImportExportModelAdmin):
    list_display = ('filename', 'template_type', 'status_badge', 'file_size', 'created_at')
    list_filter = ('template_type', 'status', 'created_at')
    search_fields = ('file', 'template_type')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'file_preview')
    save_on_top = True
    date_hierarchy = 'created_at'
    list_per_page = 20
    actions = ['validate_selected', 'mark_as_approved', 'mark_as_rejected']

    fieldsets = (
        (None, {
            'fields': ('template_type', 'file', 'status')
        }),
        ('File Information', {
            'fields': ('file_size', 'file_preview'),
            'classes': ('collapse',),
            'description': 'File details and preview'
        }),
        ('Validation', {
            'fields': ('validation_errors',),
            'classes': ('collapse',),
            'description': 'Validation results and error details'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Upload and modification timestamps'
        }),
    )

    def status_badge(self, obj):
        status_colors = {
            'approved': 'success',
            'rejected': 'danger',
            'validating': 'info',
            'pending': 'warning'
        }
        color = status_colors.get(obj.status, 'secondary')
        icon = {
            'approved': 'bi-check-circle',
            'rejected': 'bi-x-circle',
            'validating': 'bi-arrow-repeat',
            'pending': 'bi-clock'
        }.get(obj.status, 'bi-question-circle')
        
        return format_html(
            '<span class="badge bg-{} d-flex align-items-center gap-1" style="width: fit-content">'
            '<i class="bi {}"></i> {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def file_size(self, obj):
        return obj.get_file_size()
    file_size.short_description = 'File Size'

    def file_preview(self, obj):
        try:
            import pandas as pd
            df = pd.read_csv(obj.file.path, nrows=5)
            html = '<div class="file-preview"><small>First 5 rows preview:</small>'
            html += df.to_html(classes='table table-sm', index=False)
            html += '</div>'
            return format_html(html)
        except Exception as e:
            return "Unable to preview file"
    file_preview.short_description = 'File Preview'

    def validate_selected(self, request, queryset):
        success_count = 0
        for upload in queryset:
            if upload.start_validation():
                success_count += 1
        
        self.message_user(
            request,
            f'{success_count} out of {queryset.count()} files validated successfully.',
            messages.SUCCESS if success_count == queryset.count() else messages.WARNING
        )
    validate_selected.short_description = "Validate selected uploads"

    def mark_as_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} files marked as approved.', messages.SUCCESS)
    mark_as_approved.short_description = "Mark selected as approved"

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} files marked as rejected.', messages.WARNING)
    mark_as_rejected.short_description = "Mark selected as rejected"

    class Media:
        css = {
            'all': ['css/admin.css']
        }
        js = ['js/admin.js']