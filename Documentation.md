# Material Acquisitions Portal Documentation

## Table of Contents
1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Installation and Setup](#3-installation-and-setup)
4. [User Guide](#4-user-guide)
5. [Admin Guide](#5-admin-guide)
6. [Technical Reference](#6-technical-reference)
7. [API Documentation](#7-api-documentation)
8. [Security Considerations](#8-security-considerations)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)

## 1. Introduction

### 1.1 About MAP
The Material Acquisitions Portal (MAP) is a comprehensive data management system designed to streamline the process of collecting, validating, and managing various types of material acquisition data. The system handles multiple data templates, provides robust validation, and offers an intuitive interface for both users and administrators.

### 1.2 Key Features
- Secure file upload and validation system
- Multiple data template support
- Automated validation processes
- Enhanced admin interface
- Role-based access control
- File preview and management
- Comprehensive error reporting

### 1.3 Target Users
- Data Entry Personnel
- Department Managers
- System Administrators
- Data Analysts
- Procurement Teams

## 2. System Architecture

### 2.1 Technology Stack
- **Backend Framework**: Django 5.0
- **Database**: SQLite (default)
- **Frontend**: Bootstrap 5.3.2
- **Additional Libraries**:
  - django-import-export
  - django-crispy-forms
  - crispy-bootstrap5
  - pandas

### 2.2 System Components
```
MAP Architecture
├── Frontend Layer
│   ├── Templates (Django Templates)
│   ├── Static Files (CSS/JS)
│   └── User Interface Components
├── Application Layer
│   ├── Views
│   ├── Forms
│   └── Validators
├── Data Layer
│   ├── Models
│   ├── Database
│   └── File Storage
└── Security Layer
    ├── Authentication
    ├── Authorization
    └── Data Validation
```

### 2.3 Data Flow
1. User uploads file
2. System validates file format
3. Data validation process
4. Status update
5. Admin review
6. Final approval/rejection

## 3. Installation and Setup

### 3.1 Prerequisites
- Python 3.11.6 or higher
- pip package manager
- Virtual environment tool
- Git (for version control)

### 3.2 Installation Steps
```bash
# Clone repository
git clone <repository-url>
cd data_collection_portal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

### 3.3 Configuration
Key settings in `settings.py`:
```python
# File upload settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Template configuration
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

## 4. User Guide

### 4.1 Getting Started
1. Access the system at `http://your-domain/`
2. Log in with provided credentials
3. Navigate to the home dashboard

### 4.2 File Upload Process
1. Select data template type
2. Download template (if needed)
3. Prepare CSV file according to template
4. Upload file
5. Review validation results

### 4.3 Template Types
- **Vendor Master**
  - Vendor information
  - Contact details
  - Tax information
  
- **Item Master**
  - Product details
  - Specifications
  - Pricing information

- **Purchase History**
  - Transaction records
  - Order details
  - Pricing data

- **Invoice Data**
  - Invoice details
  - Payment information
  - Due dates

### 4.4 File Requirements
- Format: CSV
- Encoding: UTF-8
- Size limit: 10MB
- Required headers must match template

## 5. Admin Guide

### 5.1 Admin Interface
Access the admin interface at `/admin` with superuser credentials.

### 5.2 Managing Templates
```python
class DataTemplate:
    fields = [
        'name',
        'template_type',
        'description',
        'required_headers'
    ]
```

### 5.3 User Management
- Create new users
- Assign roles
- Manage permissions
- Monitor activity

### 5.4 Data Management
- View uploaded files
- Validate data
- Export reports
- Archive records

## 6. Technical Reference

### 6.1 Models
```python
class DataUpload:
    """
    Handles file uploads and validation
    """
    template_type = models.CharField(choices=TEMPLATE_TYPES)
    file = models.FileField(upload_to=get_upload_path)
    status = models.CharField(choices=STATUS_CHOICES)
    validation_errors = models.JSONField(null=True)
```

### 6.2 Views
```python
class UploadView:
    """
    Handles file upload and validation
    """
    def post(self, request):
        # File upload logic
        # Validation process
        # Status update
```

### 6.3 Validation Process
1. File format validation
2. Header validation
3. Data type validation
4. Business logic validation
5. Error reporting

## 7. API Documentation

### 7.1 Internal APIs
```python
def validate_file(file_path):
    """
    Validates uploaded file
    
    Args:
        file_path (str): Path to uploaded file
        
    Returns:
        dict: Validation results
    """
```

### 7.2 External APIs
Document any external API integrations here.

## 8. Security Considerations

### 8.1 Authentication
- Django authentication system
- Session management
- Password policies

### 8.2 File Security
- File type validation
- Size limitations
- Secure storage
- Access control

### 8.3 Data Protection
- Input sanitization
- CSRF protection
- XSS prevention
- SQL injection prevention

## 9. Troubleshooting

### 9.1 Common Issues
1. File Upload Errors
   - Check file format
   - Verify file size
   - Validate headers

2. Validation Failures
   - Review error messages
   - Check data format
   - Verify required fields

### 9.2 Error Messages
```python
VALIDATION_ERRORS = {
    'missing_headers': 'Required headers are missing',
    'invalid_format': 'Invalid file format',
    'data_type_error': 'Invalid data type in column'
}
```

## 10. Best Practices

### 10.1 File Preparation
- Use provided templates
- Follow naming conventions
- Verify data formats
- Check for required fields

### 10.2 Data Entry
- Consistent formatting
- Complete all required fields
- Verify data accuracy
- Regular backups

### 10.3 System Usage
- Regular password updates
- Session management
- Data verification
- Regular monitoring

## Appendices

### Appendix A: Glossary
- **Template**: Predefined format for data upload
- **Validation**: Process of verifying data accuracy
- **CSV**: Comma-Separated Values file format
- **UTF-8**: Character encoding standard

### Appendix B: Quick Reference
- Upload Limits: 10MB
- Supported Format: CSV
- Encoding: UTF-8
- Template Types: 7

### Appendix C: Version History
- Version 1.0: Initial release
- Version 1.1: Enhanced validation
- Version 1.2: Added file preview
- Version 1.3: Improved admin interface