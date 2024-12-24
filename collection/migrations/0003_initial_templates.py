# collection/migrations/0002_initial_templates.py
from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration to create initial templates for data collection
    """

    dependencies = [
        ('collection', '0002_alter_datatemplate_template_type_and_more'),
    ]

    def create_initial_templates(apps, schema_editor):
        DataTemplate = apps.get_model('collection', 'DataTemplate')
        
        templates = [
            {
                'name': 'Vendor Master',
                'template_type': 'vendor',
                'description': 'Vendor information and details',
                'required_headers': {
                    'headers': [
                        'Vendor Number',
                        'Vendor Name',
                        'Contact Person',
                        'Email',
                        'Phone Number',
                        'Fax Number',
                        'Address',
                        'City',
                        'State',
                        'Zip Code',
                        'Country',
                        'Customer Account Number',
                        'Federal Tax ID',
                        'GHX Integration (Y/N)',
                        'Status'
                    ]
                }
            },
            {
                'name': 'Item Master',
                'template_type': 'item',
                'description': 'Product catalog and specifications',
                'required_headers': {
                    'headers': [
                        'Item Number',
                        'Item Description',
                        'Manufacturer Name',
                        'Manufacturer Catalog Number',
                        'Vendor Name',
                        'Vendor Catalog Number',
                        'Order Unit of Measure',
                        'Issue Unit of Measure',
                        'Conversion Quantity',
                        'Base Price',
                        'Currency',
                        'Category',
                        'Storeroom Indicator (Y/N)',
                        'Status'
                    ]
                }
            },
            {
                'name': 'Purchase History',
                'template_type': 'purchase',
                'description': 'Historical purchase transactions',
                'required_headers': {
                    'headers': [
                        'Purchase Order Number',
                        'Item Number',
                        'Item Description',
                        'Vendor Number',
                        'Vendor Name',
                        'Order Date',
                        'Delivery Date',
                        'Quantity',
                        'Order Unit of Measure',
                        'Unit Price',
                        'Currency',
                        'Total Amount',
                        'Freight Cost',
                        'Lead Time (Days)',
                        'Delivery Location',
                        'Cost Center Number',
                        'Payment Terms',
                        'Invoice Number',
                        'Invoice Date',
                        'Invoice Amount',
                        'Invoice Status',
                        'Status'
                    ]
                }
            },
            {
                'name': 'Invoice Data',
                'template_type': 'invoice',
                'description': 'Payment and invoice information',
                'required_headers': {
                    'headers': [
                        'Invoice Number',
                        'Invoice Date',
                        'Purchase Order Number',
                        'Vendor Number',
                        'Vendor Name',
                        'Invoice Amount',
                        'Currency',
                        'Payment Terms',
                        'Due Date',
                        'Payment Status',
                        'Payment Date',
                        'Payment Method',
                        'Payment Reference',
                        'Tax Amount',
                        'Freight Amount',
                        'Discount Amount',
                        'Total Amount',
                        'Cost Center Number',
                        'GL Account',
                        'Status'
                    ]
                }
            },
            {
                'name': 'Contracts',
                'template_type': 'contract',
                'description': 'Contract terms and conditions',
                'required_headers': {
                    'headers': [
                        'Contract Number',
                        'Vendor Name',
                        'Category',
                        'Start Date',
                        'End Date',
                        'Contract Type (Vizient/Local)',
                        'Payment Terms',
                        'Contract Value',
                        'Currency',
                        'Termination Terms',
                        'Status'
                    ]
                }
            },
            {
                'name': 'Facilities',
                'template_type': 'facility',
                'description': 'Facility locations and details',
                'required_headers': {
                    'headers': [
                        'Facility ID',
                        'Facility Name',
                        'Ship To Address',
                        'Ship To State',
                        'Ship To Zip',
                        'Ship To Phone',
                        'Ship To Fax',
                        'Bill To Address',
                        'Bill To State',
                        'Bill To Zip',
                        'Bill To Phone',
                        'Bill To Fax',
                        'Tax ID Number',
                        'State Sales Tax Rate',
                        'County Tax Rate',
                        'County Name',
                        'City Tax Rate',
                        'City Name',
                        'Status'
                    ]
                }
            },
            {
                'name': 'Departments',
                'template_type': 'department',
                'description': 'Department structure and hierarchy',
                'required_headers': {
                    'headers': [
                        'Department ID',
                        'Department Name',
                        'Parent Department',
                        'Cost Center Code',
                        'Manager',
                        'Location',
                        'GL Code',
                        'Expense Account',
                        'Status'
                    ]
                }
            }
        ]
        
        for template in templates:
            DataTemplate.objects.create(**template)

    def remove_initial_templates(apps, schema_editor):
        DataTemplate = apps.get_model('collection', 'DataTemplate')
        DataTemplate.objects.all().delete()

    operations = [
        migrations.RunPython(create_initial_templates, remove_initial_templates),
    ]