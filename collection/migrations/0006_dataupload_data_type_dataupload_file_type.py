# Generated by Django 5.0 on 2024-12-24 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0005_dataupload_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataupload',
            name='data_type',
            field=models.CharField(blank=True, help_text='Descriptive name for generic uploads', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dataupload',
            name='file_type',
            field=models.CharField(choices=[('excel', 'Excel File'), ('csv', 'CSV File'), ('text', 'Text File'), ('pdf', 'PDF Document'), ('generic', 'Generic File')], default='generic', help_text='Type of file being uploaded', max_length=20),
        ),
    ]