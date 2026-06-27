from rest_framework import serializers
from .models import Resource, StoredFile, ResourceLibrary


class StoredFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = '__all__'


class ResourceLibrarySerializer(serializers.ModelSerializer):
    file_name = serializers.ReadOnlyField(source='file.file_name')
    file_url = serializers.ReadOnlyField(source='file.file_url')
    size = serializers.ReadOnlyField(source='file.size')
    subject_name = serializers.ReadOnlyField(source='subject.subject_catalog.name')

    class Meta:
        model = ResourceLibrary
        fields = ['id', 'semester', 'subject', 'subject_name', 'file', 'file_name', 'file_url', 'size', 'resource_type']


class ResourceSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='subject.name')
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.student.name')

    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'file_url', 'subject', 'subject_name', 'uploaded_by', 'uploaded_by_name', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at']
