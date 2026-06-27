from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from .models import Announcement
from accounts.models import Student, CR
from .serializers import AnnouncementSerializer
from accounts.permissions import IsStudent, IsCR, JWTAuthentication
from accounts.utils import success_response, error_response
from accounts.pagination import StandardResultsSetPagination
from .services import AnnouncementService


class StudentAnnouncementsView(ListAPIView):
    """
    GET /api/student/announcements/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    serializer_class = AnnouncementSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return Announcement.objects.none()
            
        return Announcement.objects.filter(
            semester=student.semester
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class CRAnnouncementsView(APIView):
    """
    POST /api/cr/announcements/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def post(self, request):
        try:
            announcement = AnnouncementService.create_announcement(request.user, request.data)
            return success_response(
                data=AnnouncementSerializer(announcement).data, 
                message="Announcement Created Successfully", 
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(message=str(e))
