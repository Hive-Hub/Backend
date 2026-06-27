from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.student.name')

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'created_by', 'created_by_name', 'semester', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']
