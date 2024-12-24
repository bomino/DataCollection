from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import DataTemplate, DataUpload
from .serializers import DataTemplateSerializer, DataUploadSerializer

class DataTemplateViewSet(viewsets.ModelViewSet):
    queryset = DataTemplate.objects.all()
    serializer_class = DataTemplateSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'template_type']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download template file"""
        template = self.get_object()
        # Implement template download logic
        return Response({'message': 'Template download endpoint'})

class DataUploadViewSet(viewsets.ModelViewSet):
    serializer_class = DataUploadSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['template_type', 'file_type', 'status']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        return DataUpload.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        upload = serializer.save()
        upload.start_validation()

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Trigger validation for an upload"""
        upload = self.get_object()
        success = upload.start_validation()
        
        if success:
            return Response({
                'status': 'success',
                'message': 'File validated successfully'
            })
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': upload.validation_errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download uploaded file"""
        upload = self.get_object()
        # Implement file download logic
        return Response({'message': 'File download endpoint'})