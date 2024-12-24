# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('admin', 'Administrator'),
        ('collector', 'Data Collector'),
        ('validator', 'Data Validator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)

    class Meta:
        permissions = [
            ("can_upload_data", "Can upload data files"),
            ("can_validate_data", "Can validate data"),
            ("can_manage_users", "Can manage users"),
        ]

# collection/models.py
from django.db import models
from django.conf import settings

class DataTemplate(models.Model):
    TEMPLATE_TYPES = (
        ('vendor', 'Vendor Master'),
        ('item', 'Item Master'),
        ('purchase', 'Purchase History'),
        ('contract', 'Contracts'),
        ('facility', 'Facilities'),
        ('department', 'Departments'),
    )
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField()
    template_file = models.FileField(upload_to='templates/')
    required_headers = models.JSONField()
    validation_rules = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"

class DataUpload(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('validating', 'Validating'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    template = models.ForeignKey(DataTemplate, on_delete=models.PROTECT)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    validation_results = models.JSONField(null=True, blank=True)
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"