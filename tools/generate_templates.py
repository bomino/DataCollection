# tools/generate_templates.py
import os
import csv
from pathlib import Path

TEMPLATES = {
    'vendor_master.csv': {
        'headers': [
            'Vendor Number', 'Vendor Name', 'Contact Person', 'Email', 'Phone Number', 
            'Fax Number', 'Address', 'City', 'State', 'Zip Code', 'Country', 
            'Customer Account Number', 'Federal Tax ID', 'GHX Integration (Y/N)', 'Status'
        ],
        'examples': [
            ['78186', 'National Building Supply', 'John Smith', 'john.smith@nbs.com', '865-485-1965',
             '865-485-5656', '1234 Elm Street Unit 6', 'Knoxville', 'TN', '37919', 'USA',
             '23AE25', '54-2049200', 'Y', 'Active'],
            ['78187', 'Southern Paint Supplies', 'Mary Johnson', 'mary.j@sps.com', '865-487-1234',
             '865-487-5678', '567 Oak Avenue', 'Knoxville', 'TN', '37920', 'USA',
             '45BE89', '54-3089201', 'N', 'Active']
        ]
    },
    
    'item_master.csv': {
        'headers': [
            'Item Number', 'Item Description', 'Manufacturer Name', 'Manufacturer Catalog Number',
            'Vendor Name', 'Vendor Catalog Number', 'Order Unit of Measure', 
            'Issue Unit of Measure', 'Conversion Quantity', 'Base Price', 'Currency',
            'Category', 'Storeroom Indicator (Y/N)', 'Status'
        ],
        'examples': [
            ['10021', 'Drywall 5/8 X 8 FT', 'International Gypsum', '1061A',
             'National Building Supply', '3280001061', 'CS', 'EA', '50',
             '42.23', 'USD', 'Construction Materials', 'Y', 'Active'],
            ['10022', 'Paint Roller 9"', 'Premier Tools', '2089B',
             'Southern Paint Supplies', '4570002089', 'BX', 'EA', '12',
             '24.99', 'USD', 'Paint Supplies', 'Y', 'Active']
        ]
    },
    
    'purchase_history.csv': {
        'headers': [
            'Purchase Order Number', 'Item Number', 'Item Description', 'Vendor Number',
            'Vendor Name', 'Order Date', 'Delivery Date', 'Quantity', 'Order Unit of Measure',
            'Unit Price', 'Currency', 'Total Amount', 'Freight Cost', 'Lead Time (Days)',
            'Delivery Location', 'Cost Center Number', 'Payment Terms', 'Invoice Number',
            'Invoice Date', 'Invoice Amount', 'Invoice Status', 'Status'
        ],
        'examples': [
            ['PO-124678', '10021', 'Drywall 5/8 X 8 FT', '78186', 'National Building Supply',
             '2024-01-15', '2024-01-18', '20', 'CS', '42.23', 'USD', '844.60', '75.00', '3',
             'Building A Warehouse', '7170-065', 'Net 30', 'INV-89012', '2024-01-18',
             '919.60', 'Paid', 'Completed'],
            ['PO-124679', '10022', 'Paint Roller 9"', '78187', 'Southern Paint Supplies',
             '2024-01-16', '2024-01-19', '10', 'BX', '24.99', 'USD', '249.90', '25.00', '3',
             'Building B Storage', '7170-066', 'Net 30', 'INV-89013', '2024-01-19',
             '274.90', 'Pending', 'Delivered']
        ]
    },
    
    'invoice_data.csv': {
        'headers': [
            'Invoice Number', 'Invoice Date', 'Purchase Order Number', 'Vendor Number', 
            'Vendor Name', 'Invoice Amount', 'Currency', 'Payment Terms', 'Due Date',
            'Payment Status', 'Payment Date', 'Payment Method', 'Payment Reference',
            'Tax Amount', 'Freight Amount', 'Discount Amount', 'Total Amount',
            'Cost Center Number', 'GL Account', 'Status'
        ],
        'examples': [
            ['INV-89012', '2024-01-18', 'PO-124678', '78186', 'National Building Supply',
             '844.60', 'USD', 'Net 30', '2024-02-17', 'Paid', '2024-02-15', 'ACH',
             'ACH-78901', '0.00', '75.00', '0.00', '919.60', '7170-065', '5001', 'Closed'],
            ['INV-89013', '2024-01-19', 'PO-124679', '78187', 'Southern Paint Supplies',
             '249.90', 'USD', 'Net 30', '2024-02-18', 'Pending', '', '',
             '', '0.00', '25.00', '0.00', '274.90', '7170-066', '5001', 'Open']
        ]
    },
    
    'contracts.csv': {
        'headers': [
            'Contract Number', 'Vendor Name', 'Category', 'Start Date', 'End Date',
            'Contract Type (Vizient/Local)', 'Payment Terms', 'Contract Value', 'Currency',
            'Termination Terms', 'Status'
        ],
        'examples': [
            ['K-011', 'National Building Supply', 'Construction Materials',
             '2024-01-01', '2024-12-31', 'Local', 'Net 30', '100000.00', 'USD',
             '30-Day Notice', 'Active'],
            ['K-012', 'Southern Paint Supplies', 'Paint Supplies',
             '2024-01-01', '2024-12-31', 'Vizient', 'Net 30', '50000.00', 'USD',
             '60-Day Notice', 'Active']
        ]
    },
    
    'facilities.csv': {
        'headers': [
            'Facility ID', 'Facility Name', 'Ship To Address', 'Ship To State', 
            'Ship To Zip', 'Ship To Phone', 'Ship To Fax', 'Bill To Address', 
            'Bill To State', 'Bill To Zip', 'Bill To Phone', 'Bill To Fax',
            'Tax ID Number', 'State Sales Tax Rate', 'County Tax Rate', 'County Name',
            'City Tax Rate', 'City Name', 'Status'
        ],
        'examples': [
            ['F001', 'Main Hospital', '789 Healthcare Drive', 'TN', '37919',
             '865-555-0100', '865-555-0101', '789 Healthcare Drive', 'TN', '37919',
             '865-555-0100', '865-555-0101', '62-1234567', '7.00', '2.25',
             'Knox', '2.25', 'Knoxville', 'Active'],
            ['F002', 'West Wing', '790 Healthcare Drive', 'TN', '37919',
             '865-555-0200', '865-555-0201', '789 Healthcare Drive', 'TN', '37919',
             '865-555-0100', '865-555-0101', '62-1234567', '7.00', '2.25',
             'Knox', '2.25', 'Knoxville', 'Active']
        ]
    },
    
    'departments.csv': {
        'headers': [
            'Department ID', 'Department Name', 'Parent Department', 'Cost Center Code',
            'Manager', 'Location', 'GL Code', 'Expense Account', 'Status'
        ],
        'examples': [
            ['D001', 'Facilities Management', 'Operations', '7170-065',
             'Robert Wilson', 'Main Hospital', '5001', '6010', 'Active'],
            ['D002', 'Building Maintenance', 'Facilities Management', '7170-066',
             'Sarah Davis', 'Main Hospital', '5001', '6020', 'Active']
        ]
    }
}

def create_template_directory():
    """Create templates directory if it doesn't exist"""
    base_dir = Path(__file__).resolve().parent.parent
    template_dir = base_dir / 'static' / 'templates'
    template_dir.mkdir(parents=True, exist_ok=True)
    return template_dir

def generate_templates():
    """Generate all CSV templates with example data"""
    template_dir = create_template_directory()
    
    for template_name, template_data in TEMPLATES.items():
        template_path = template_dir / template_name
        
        with open(template_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write headers
            writer.writerow(template_data['headers'])
            # Write example rows
            writer.writerows(template_data['examples'])
            
        print(f"Created template with examples: {template_path}")

if __name__ == "__main__":
    print("Generating CSV templates with example data...")
    generate_templates()
    print("Template generation complete!")