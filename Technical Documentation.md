# MAP Technical Documentation

## Development Setup

### Environment Setup
```bash
# Required Python version
Python 3.11.6

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Development Dependencies
```txt
Django==5.0
pandas==2.1.3
django-import-export==3.3.1
django-crispy-forms==2.1
crispy-bootstrap5==2023.10
```

## Code Structure

### Models
```python
# DataTemplate Model
class DataTemplate(models.Model):
    """
    Stores data templates and their configurations
    """
    name = models.CharField(max_length=100)
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPES
    )
    description = models.TextField()
    required_headers = models.JSONField(default=dict)
    
    def validate_headers(self, headers):
        """
        Validates if provided headers match template requirements
        """
        required = set(self.required_headers.get('headers', []))
        provided = set(headers)
        return {
            'valid': required.issubset(provided),
            'missing': required - provided
        }

# DataUpload Model
class DataUpload(models.Model):
    """
    Handles file uploads and validation
    """
    template_type = models.CharField(
        max_length=20,
        choices=DataTemplate.TEMPLATE_TYPES
    )
    file = models.FileField(upload_to=get_upload_path)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
```

### Views
```python
class UploadView(View):
    """
    Handles file uploads and validation
    """
    def get(self, request):
        form = UploadForm()
        return render(request, 'upload.html', {'form': form})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save()
            upload.start_validation()
            return redirect('upload_list')
        return render(request, 'upload.html', {'form': form})
```

### Forms
```python
class UploadForm(forms.ModelForm):
    """
    Form for handling file uploads
    """
    class Meta:
        model = DataUpload
        fields = ['template_type', 'file']

    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('Only CSV files are allowed')
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size cannot exceed 10MB')
        return file
```

### URL Configuration
```python
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_data, name='upload_data'),
    path('uploads/', views.upload_list, name='upload_list'),
    path('template/<str:type>/', views.download_template, 
         name='download_template'),
]
```

## Data Validation Process

### Validation Steps
1. File Format Validation
```python
def validate_file_format(file):
    """
    Validates file format and structure
    """
    if not file.name.endswith('.csv'):
        return False, 'Invalid file format'
    try:
        df = pd.read_csv(file)
        return True, None
    except Exception as e:
        return False, str(e)
```

2. Header Validation
```python
def validate_headers(template, headers):
    """
    Validates CSV headers against template requirements
    """
    required = set(template.required_headers)
    provided = set(headers)
    missing = required - provided
    extra = provided - required
    return {
        'valid': len(missing) == 0,
        'missing': list(missing),
        'extra': list(extra)
    }
```

3. Data Validation
```python
def validate_data(df, template_type):
    """
    Validates data based on template type
    """
    validators = {
        'vendor': validate_vendor_data,
        'item': validate_item_data,
        'purchase': validate_purchase_data,
        'invoice': validate_invoice_data
    }
    validator = validators.get(template_type)
    return validator(df) if validator else (True, None)
```

## Testing

### Unit Tests
```python
class DataUploadTests(TestCase):
    def setUp(self):
        self.template = DataTemplate.objects.create(
            name='Test Template',
            template_type='vendor',
            required_headers=['id', 'name']
        )

    def test_file_upload(self):
        with open('test.csv', 'rb') as f:
            response = self.client.post('/upload/', {
                'template_type': 'vendor',
                'file': f
            })
        self.assertEqual(response.status_code, 302)
```

### Integration Tests
```python
class ValidationIntegrationTests(TestCase):
    def test_complete_validation_process(self):
        # Create test file
        # Upload file
        # Check validation status
        # Verify results
```

## Performance Considerations

### File Processing
- Use chunked reading for large files
- Process data in batches
- Implement background tasks for validation

### Database Optimization
- Index frequently queried fields
- Use select_related/prefetch_related
- Implement pagination

### Caching
```python
# Cache template configurations
@cached_property
def get_template_config(self):
    return self.required_headers
```

## Security Implementation

### File Upload Security
```python
ALLOWED_EXTENSIONS = {'csv'}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

def secure_upload(file):
    """
    Implements secure file upload
    """
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError('File too large')
    
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError('Invalid file type')
```

### Data Validation Security
```python
def sanitize_data(data):
    """
    Sanitizes input data
    """
    # Remove potentially harmful characters
    # Validate data types
    # Check for SQL injection patterns
```

## Deployment

### Production Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

### Server Configuration
- Use HTTPS
- Configure static/media files
- Set up proper permissions


## API Reference

### Internal APIs

#### File Management API
```python
class FileManager:
    """
    Handles file operations and management
    """
    def get_upload_path(instance, filename):
        """
        Generates custom upload path for files
        
        Args:
            instance: DataUpload instance
            filename: Original filename
            
        Returns:
            str: Path where file should be stored
        """
        ext = filename.split('.')[-1]
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{instance.template_type}_{timestamp}.{ext}"
        return os.path.join(
            'uploads',
            timezone.now().strftime('%Y'),
            timezone.now().strftime('%m'),
            timezone.now().strftime('%d'),
            new_filename
        )

    def process_file(file_path):
        """
        Process uploaded file
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            tuple: (success, data/error_message)
        """
        try:
            df = pd.read_csv(file_path)
            return True, df
        except Exception as e:
            return False, str(e)
```

#### Validation API
```python
class ValidationManager:
    """
    Handles data validation processes
    """
    def validate_vendor_data(df):
        """
        Validates vendor data
        
        Args:
            df: pandas DataFrame containing vendor data
            
        Returns:
            dict: Validation results
        """
        errors = []
        
        # Check for required fields
        if 'Vendor ID' in df.columns:
            if df['Vendor ID'].isnull().any():
                errors.append('Vendor ID cannot be empty')
            if df['Vendor ID'].duplicated().any():
                errors.append('Duplicate Vendor IDs found')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def validate_invoice_data(df):
        """
        Validates invoice data
        
        Args:
            df: pandas DataFrame containing invoice data
            
        Returns:
            dict: Validation results
        """
        errors = []
        
        # Validate amount fields
        amount_fields = ['Invoice Amount', 'Total Amount']
        for field in amount_fields:
            if field in df.columns:
                if df[field].isnull().any():
                    errors.append(f'{field} cannot be empty')
                elif (df[field] <= 0).any():
                    errors.append(f'{field} must be greater than zero')

        # Validate date fields
        date_fields = ['Invoice Date', 'Due Date']
        for field in date_fields:
            if field in df.columns:
                try:
                    pd.to_datetime(df[field])
                except:
                    errors.append(f'{field} must be in valid date format')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
```

### Template Management

#### Template Configuration
```python
class TemplateConfig:
    """
    Manages template configurations
    """
    VENDOR_TEMPLATE = {
        'headers': [
            'Vendor ID',
            'Vendor Name',
            'Contact Person',
            'Email',
            'Phone',
            'Address',
            'Tax ID'
        ],
        'required': [
            'Vendor ID',
            'Vendor Name',
            'Tax ID'
        ],
        'data_types': {
            'Vendor ID': 'string',
            'Phone': 'string',
            'Tax ID': 'string'
        }
    }

    INVOICE_TEMPLATE = {
        'headers': [
            'Invoice Number',
            'Date',
            'Due Date',
            'Vendor ID',
            'Amount',
            'Tax',
            'Total'
        ],
        'required': [
            'Invoice Number',
            'Date',
            'Vendor ID',
            'Amount'
        ],
        'data_types': {
            'Amount': 'float',
            'Tax': 'float',
            'Total': 'float',
            'Date': 'datetime'
        }
    }
```

### Data Processing

#### CSV Processing
```python
class CSVProcessor:
    """
    Handles CSV file processing
    """
    def read_csv(file_path):
        """
        Reads and processes CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            pandas.DataFrame: Processed data
        """
        try:
            df = pd.read_csv(
                file_path,
                encoding='utf-8',
                dtype_backend='numpy_nullable'
            )
            return df
        except UnicodeDecodeError:
            # Try different encodings
            try:
                df = pd.read_csv(
                    file_path,
                    encoding='latin1',
                    dtype_backend='numpy_nullable'
                )
                return df
            except Exception as e:
                raise ValueError(f"Unable to read file: {str(e)}")

    def validate_data_types(df, template):
        """
        Validates data types against template specifications
        
        Args:
            df: pandas DataFrame
            template: Template configuration
            
        Returns:
            dict: Validation results
        """
        errors = []
        for column, dtype in template['data_types'].items():
            if column in df.columns:
                try:
                    if dtype == 'datetime':
                        pd.to_datetime(df[column])
                    elif dtype == 'float':
                        pd.to_numeric(df[column])
                    # Add more type validations as needed
                except Exception as e:
                    errors.append(f"Invalid data type in column {column}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
```

### Error Handling

#### Custom Exceptions
```python
class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or []

class FileProcessingError(Exception):
    """Custom exception for file processing errors"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}

class TemplateError(Exception):
    """Custom exception for template-related errors"""
    pass
```

#### Error Handlers
```python
def handle_upload_error(error):
    """
    Handles file upload errors
    
    Args:
        error: Exception object
        
    Returns:
        dict: Error details
    """
    if isinstance(error, ValidationError):
        return {
            'status': 'error',
            'message': str(error),
            'errors': error.errors
        }
    elif isinstance(error, FileProcessingError):
        return {
            'status': 'error',
            'message': 'File processing failed',
            'details': error.details
        }
    else:
        return {
            'status': 'error',
            'message': 'An unexpected error occurred',
            'error': str(error)
        }
```

### Background Tasks

#### Task Queue
```python
# Using Django's built-in async capabilities
async def process_upload(upload_id):
    """
    Process file upload asynchronously
    
    Args:
        upload_id: ID of DataUpload instance
    """
    try:
        upload = await sync_to_async(DataUpload.objects.get)(id=upload_id)
        await sync_to_async(upload.start_validation)()
    except Exception as e:
        # Log error
        logger.error(f"Error processing upload {upload_id}: {str(e)}")
```

Would you like me to continue with more sections or provide more detail on any specific area?