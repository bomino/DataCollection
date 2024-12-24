# collection/models.py
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
import pandas as pd
import os

def get_upload_path(instance, filename):
    """Generate custom upload path for files"""
    # Get the file extension
    ext = filename.split('.')[-1]
    # Create filename format: template_type_YYYYMMDD_HHMMSS.extension
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{instance.template_type}_{timestamp}.{ext}"
    # Return the complete path including year/month/day structure
    return os.path.join('uploads', 
                       timezone.now().strftime('%Y'),
                       timezone.now().strftime('%m'),
                       timezone.now().strftime('%d'),
                       filename)

class DataTemplate(models.Model):
    """Model to store data templates and their configurations"""
    TEMPLATE_TYPES = [
        ('vendor', 'Vendor Master'),
        ('item', 'Item Master'),
        ('purchase', 'Purchase History'),
        ('invoice', 'Invoice Data'),
        ('contract', 'Contracts'),
        ('facility', 'Facilities'),
        ('department', 'Departments'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField()
    required_headers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Data Template'
        verbose_name_plural = 'Data Templates'

    def __str__(self):
        return f"{self.get_template_type_display()}"

class DataUpload(models.Model):
    """Model to handle file uploads and validation"""

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploads',
        help_text="User who uploaded the file"
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('validating', 'Validating'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    

    FILE_TYPES = [
        ('excel', 'Excel File'),
        ('csv', 'CSV File'),
        ('text', 'Text File'),
        ('pdf', 'PDF Document'),
        ('generic', 'Generic File'),  # Added generic as default
    ]
    
    template_type = models.CharField(
        max_length=20, 
        choices=DataTemplate.TEMPLATE_TYPES,
        default='vendor'
    )
    
    # Updated field with default
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default='generic',  # Set default value
        help_text="Type of file being uploaded"
    )
    
    data_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Descriptive name for generic uploads"
    )


    file = models.FileField(
        upload_to=get_upload_path,
        max_length=255
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    notes = models.TextField(
            null=True, 
            blank=True,
            help_text="Optional notes about the upload"
        )

    validation_errors = models.JSONField(
        null=True, 
        blank=True,
        help_text="Stores validation errors if any"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Data Upload'
        verbose_name_plural = 'Data Uploads'

    def __str__(self):
        if self.template_type:
            return f"{self.get_template_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        return f"{self.data_type or 'Generic Upload'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def filename(self):
        """Returns the base filename without the path"""
        return os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        """Override delete method to ensure file is deleted from storage"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def get_file_size(self):
        """Returns the file size in a human-readable format"""
        try:
            size_bytes = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.2f} TB"
        except:
            return "Unknown"
        
    def start_validation(self):
        """Initiates the validation process for the uploaded file"""
        self.status = 'validating'
        self.save()
        
        try:
            # Perform validation
            is_valid, errors = self.validate_file()
            
            if is_valid:
                self.status = 'approved'
                self.validation_errors = None
            else:
                self.status = 'rejected'
                self.validation_errors = errors
            
        except Exception as e:
            self.status = 'rejected'
            self.validation_errors = {'error': str(e)}
        
        self.save()
        return self.status == 'approved'

    def validate_file(self):
        """Validates the uploaded file structure and content"""
        try:
            # For generic file types, only validate basic file properties
            if self.template_type in ['excel', 'csv', 'text', 'pdf', 'generic']:
                # Check file extension
                ext = os.path.splitext(self.file.name)[1].lower()
                allowed_extensions = {
                    'excel': ['.xlsx', '.xls'],
                    'csv': ['.csv'],
                    'text': ['.txt'],
                    'pdf': ['.pdf'],
                    'generic': ['.xlsx', '.xls', '.csv', '.txt', '.pdf']
                }
                
                if ext not in allowed_extensions.get(self.template_type, []):
                    return False, {'error': f'Invalid file extension for type {self.template_type}'}
                
                # For CSV files, try to validate structure
                if self.template_type == 'csv':
                    try:
                        pd.read_csv(self.file.path)
                    except pd.errors.EmptyDataError:
                        return False, {'error': 'The CSV file is empty'}
                    except pd.errors.ParserError:
                        return False, {'error': 'Invalid CSV format'}
                
                # For Excel files, try to validate structure
                if self.template_type == 'excel':
                    try:
                        pd.read_excel(self.file.path)
                    except Exception as e:
                        return False, {'error': f'Invalid Excel file: {str(e)}'}
                
                return True, None
                
            # For template-based files, use standard validation
            try:
                # Read CSV file
                df = pd.read_csv(self.file.path)
                
                # Get template for this type
                try:
                    template = DataTemplate.objects.get(template_type=self.template_type)
                    expected_headers = template.required_headers.get('headers', [])
                except DataTemplate.DoesNotExist:
                    return False, {'error': f'No template found for type: {self.template_type}'}
                
                # Normalize headers for comparison (case-insensitive)
                file_headers = [col.lower().strip() for col in df.columns]
                expected_headers_normalized = [header.lower().strip() for header in expected_headers]
                
                # Find missing and extra headers
                missing_headers = [
                    header for header in expected_headers
                    if header.lower().strip() not in file_headers
                ]
                extra_headers = [
                    col for col in df.columns
                    if col.lower().strip() not in expected_headers_normalized
                ]
                
                errors = {}
                if missing_headers:
                    errors['missing_headers'] = missing_headers
                
                if extra_headers:
                    errors['extra_headers'] = extra_headers
                
                # If headers are valid, perform data validation
                if len(missing_headers) == 0:
                    data_errors = self.validate_data(df)
                    if data_errors:
                        errors.update(data_errors)
                
                return len(errors) == 0, errors
                
            except pd.errors.EmptyDataError:
                return False, {'error': 'The file is empty'}
            except pd.errors.ParserError:
                return False, {'error': 'Invalid CSV format'}
            except Exception as e:
                return False, {'error': f'Error validating file: {str(e)}'}
                
        except Exception as e:
            return False, {'error': f'Error validating file: {str(e)}'}

    def validate_data(self, df):
        """Validates data content based on template type"""
        errors = {}
        try:
            if self.template_type == 'vendor':
                # Validate vendor data
                if 'Vendor Number' in df.columns:
                    if df['Vendor Number'].isnull().any():
                        errors['empty_vendor_number'] = 'Vendor Number cannot be empty'
                    if df['Vendor Number'].duplicated().any():
                        errors['duplicate_vendors'] = 'Duplicate vendor numbers found'
                
                if 'Vendor Name' in df.columns and df['Vendor Name'].isnull().any():
                    errors['empty_vendor_name'] = 'Vendor Name cannot be empty'

            elif self.template_type == 'item':
                # Validate item data
                if 'Item Number' in df.columns:
                    if df['Item Number'].isnull().any():
                        errors['empty_item_number'] = 'Item Number cannot be empty'
                    if df['Item Number'].duplicated().any():
                        errors['duplicate_items'] = 'Duplicate item numbers found'
                
                if 'Item Description' in df.columns and df['Item Description'].isnull().any():
                    errors['empty_item_description'] = 'Item Description cannot be empty'

            elif self.template_type == 'invoice':
                # Validate invoice data
                amount_fields = ['Invoice Amount', 'Total Amount']
                for field in amount_fields:
                    if field in df.columns:
                        if df[field].isnull().any():
                            errors[f'empty_{field.lower().replace(" ", "_")}'] = f'{field} cannot be empty'
                        elif (df[field] <= 0).any():
                            errors[f'invalid_{field.lower().replace(" ", "_")}'] = f'{field} must be greater than zero'

                # Validate date fields
                date_fields = ['Invoice Date', 'Due Date']
                for field in date_fields:
                    if field in df.columns:
                        try:
                            pd.to_datetime(df[field])
                        except:
                            errors[f'invalid_{field.lower().replace(" ", "_")}'] = f'{field} must be in valid date format'
            
        except Exception as e:
            errors['validation_error'] = f'Error during data validation: {str(e)}'
        
        return errors
    

    def get_validation_summary(self):
        """Returns a human-readable validation summary"""
        if not self.validation_errors:
            return "No validation errors found"
            
        summary = []
        for key, value in self.validation_errors.items():
            if key == 'missing_headers':
                summary.append(f"Missing required columns: {', '.join(value)}")
            elif key == 'extra_headers':
                summary.append(f"Extra columns found: {', '.join(value)}")
            elif key == 'error':
                summary.append(f"Error: {value}")
            elif key.startswith('empty_'):
                field = key.replace('empty_', '').replace('_', ' ').title()
                summary.append(f"Error: {value}")
            elif key.startswith('invalid_'):
                field = key.replace('invalid_', '').replace('_', ' ').title()
                summary.append(f"Error: {value}")
            else:
                summary.append(f"{key}: {value}")
                
        return "\n".join(summary)

    def get_validation_message(self):
        """
        Returns a formatted validation message with detailed error information
        """
        # Success case
        if self.status == 'approved':
            return {
                'type': 'success',
                'title': 'File Validated Successfully',
                'message': 'All required columns are present and data format is correct.',
                'messages': [{
                    'type': 'success',
                    'title': 'Ready for Processing',
                    'details': f'The {self.get_template_type_display()} file has been validated and is ready for processing.'
                }]
            }
        
        # Pending case
        if not self.validation_errors:
            return {
                'type': 'info',
                'title': 'Validation Status',
                'message': 'Validation has not been performed yet.',
                'messages': [{
                    'type': 'info',
                    'title': 'Pending Validation',
                    'details': 'The file is awaiting validation.'
                }]
            }

        # Error case
        messages = []

        # Handle missing headers
        if 'missing_headers' in self.validation_errors:
            messages.append({
                'type': 'error',
                'title': 'Missing Required Columns',
                'details': self.validation_errors['missing_headers'],
                'is_list': True,
                'note': 'Please ensure all required columns are present in your CSV file.'
            })

        # Handle extra headers
        if 'extra_headers' in self.validation_errors:
            messages.append({
                'type': 'warning',
                'title': 'Additional Columns Found',
                'details': self.validation_errors['extra_headers'],
                'is_list': True,
                'note': 'These additional columns will not be processed.'
            })

        # Handle data validation errors
        for key, value in self.validation_errors.items():
            if key.startswith('empty_'):
                messages.append({
                    'type': 'error',
                    'title': 'Empty Required Field',
                    'details': value
                })
            elif key.startswith('invalid_'):
                messages.append({
                    'type': 'error',
                    'title': 'Invalid Data',
                    'details': value
                })
            elif key == 'duplicate_vendors':
                messages.append({
                    'type': 'error',
                    'title': 'Duplicate Vendor Numbers',
                    'details': value,
                    'note': 'Each vendor number must be unique.'
                })
            elif key == 'duplicate_items':
                messages.append({
                    'type': 'error',
                    'title': 'Duplicate Item Numbers',
                    'details': value,
                    'note': 'Each item number must be unique.'
                })
            elif key == 'error':
                messages.append({
                    'type': 'error',
                    'title': 'Validation Error',
                    'details': value
                })

        return {
            'type': 'error' if self.status == 'rejected' else 'warning',
            'title': f'Validation Issues Found - {self.get_template_type_display()}',
            'messages': messages
        }

        

# Signal to handle file deletion when model is deleted
@receiver(models.signals.post_delete, sender=DataUpload)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Delete file from filesystem when DataUpload object is deleted"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

# Signal to handle file update/replacement
@receiver(models.signals.pre_save, sender=DataUpload)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Delete old file from filesystem when DataUpload file is updated"""
    if not instance.pk:
        return False

    try:
        old_file = DataUpload.objects.get(pk=instance.pk).file
        if old_file and not old_file == instance.file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except DataUpload.DoesNotExist:
        return False