from rest_framework import serializers
from ..models import DataTemplate, DataUpload

class DataTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTemplate
        fields = ['id', 'name', 'template_type', 'description', 
                 'required_headers', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class DataUploadSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    validation_summary = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DataUpload
        fields = ['id', 'template_type', 'file_type', 'data_type', 
                 'file', 'status', 'notes', 'validation_errors', 
                 'file_size', 'validation_summary', 'user',
                 'created_at', 'updated_at']
        read_only_fields = ['status', 'validation_errors', 'created_at', 
                           'updated_at', 'file_size', 'validation_summary']

    def get_file_size(self, obj):
        return obj.get_file_size()

    def get_validation_summary(self, obj):
        return obj.get_validation_summary()

    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value

    def validate(self, data):
        file_type = data.get('file_type')
        if file_type:
            ext = str(data['file'].name).lower().split('.')[-1]
            allowed_extensions = {
                'excel': ['xlsx', 'xls'],
                'csv': ['csv'],
                'text': ['txt'],
                'pdf': ['pdf']
            }
            if ext not in allowed_extensions.get(file_type, []):
                raise serializers.ValidationError(
                    f"Invalid file type. Expected {allowed_extensions.get(file_type)}"
                )
        return data