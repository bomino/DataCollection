

# collection/utils.py
import csv
import io
import pandas as pd

TEMPLATE_HEADERS = {
    'vendor': [
        'Vendor Number', 'Vendor Name', 'Contact Person', 'Email', 'Phone Number', 
        'Fax Number', 'Address', 'City', 'State', 'Zip Code', 'Country', 
        'Customer Account Number', 'Federal Tax ID', 'GHX Integration (Y/N)', 'Status'
    ],
    'item': [
        'Item Number', 'Item Description', 'Manufacturer Name', 'Manufacturer Catalog Number',
        'Vendor Name', 'Vendor Catalog Number', 'Order Unit of Measure', 
        'Issue Unit of Measure', 'Conversion Quantity', 'Base Price', 'Currency',
        'Category', 'Storeroom Indicator (Y/N)', 'Status'
    ],
    'purchase': [
        'Purchase Order Number', 'Item Number', 'Item Description', 'Vendor Number',
        'Vendor Name', 'Order Date', 'Delivery Date', 'Quantity', 'Order Unit of Measure',
        'Unit Price', 'Currency', 'Total Amount', 'Freight Cost', 'Lead Time (Days)',
        'Delivery Location', 'Cost Center Number', 'Payment Terms', 'Invoice Number',
        'Invoice Date', 'Invoice Amount', 'Invoice Status', 'Status'
    ],
    'invoice': [
        'Invoice Number', 'Invoice Date', 'Purchase Order Number', 'Vendor Number', 
        'Vendor Name', 'Invoice Amount', 'Currency', 'Payment Terms', 'Due Date',
        'Payment Status', 'Payment Date', 'Payment Method', 'Payment Reference',
        'Tax Amount', 'Freight Amount', 'Discount Amount', 'Total Amount',
        'Cost Center Number', 'GL Account', 'Status'
    ],
    'contract': [
        'Contract Number', 'Vendor Name', 'Category', 'Start Date', 'End Date',
        'Contract Type (Vizient/Local)', 'Payment Terms', 'Contract Value', 'Currency',
        'Termination Terms', 'Status'
    ],
    'facility': [
        'Facility ID', 'Facility Name', 'Ship To Address', 'Ship To State', 
        'Ship To Zip', 'Ship To Phone', 'Ship To Fax', 'Bill To Address', 
        'Bill To State', 'Bill To Zip', 'Bill To Phone', 'Bill To Fax',
        'Tax ID Number', 'State Sales Tax Rate', 'County Tax Rate', 'County Name',
        'City Tax Rate', 'City Name', 'Status'
    ],
    'department': [
        'Department ID', 'Department Name', 'Parent Department', 'Cost Center Code',
        'Manager', 'Location', 'GL Code', 'Expense Account', 'Status'
    ]
}

def validate_csv_file(file, template_type):
    """
    Validates a CSV file against the expected template structure.
    Returns (is_valid, errors)
    """
    try:
        # Read the first few lines of the file to check structure
        file.seek(0)
        df = pd.read_csv(file, nrows=0)  # Read only headers
        file_headers = list(df.columns)
        
        # Get expected headers for this template type
        expected_headers = TEMPLATE_HEADERS.get(template_type)
        if not expected_headers:
            return False, {"error": f"Unknown template type: {template_type}"}

        # Compare headers
        missing_headers = set(expected_headers) - set(file_headers)
        extra_headers = set(file_headers) - set(expected_headers)
        
        errors = {}
        if missing_headers:
            errors["missing_headers"] = list(missing_headers)
        if extra_headers:
            errors["extra_headers"] = list(extra_headers)
        
        # Return validation results
        is_valid = len(errors) == 0
        if not is_valid:
            errors["message"] = "File structure does not match the expected template"
            
        return is_valid, errors
        
    except pd.errors.EmptyDataError:
        return False, {"error": "The file is empty"}
    except pd.errors.ParserError:
        return False, {"error": "Invalid CSV file format"}
    except Exception as e:
        return False, {"error": f"Error validating file: {str(e)}"}