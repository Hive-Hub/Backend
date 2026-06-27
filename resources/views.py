from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ResourceLibrary, StoredFile
from accounts.models import Student, CR
from .serializers import ResourceLibrarySerializer
from accounts.permissions import IsStudent, IsCR, JWTAuthentication
from accounts.utils import success_response, error_response
from .services import ResourcesService


class ResourcesListView(APIView):
    """
    GET /api/resources/?semester=3&subject=DBMS
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        semester_id = request.query_params.get('semester')
        subject_id = request.query_params.get('subject')

        queryset = ResourceLibrary.objects.all()

        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        if subject_id:
            # Matches subject catalouge ID or subject catalog code
            if subject_id.isdigit():
                queryset = queryset.filter(subject_id=subject_id)
            else:
                queryset = queryset.filter(subject__subject_catalog__code__iexact=subject_id)

        # Order by newest
        queryset = queryset.order_by('-file__uploaded_at')

        serializer = ResourceLibrarySerializer(queryset, many=True)
        return success_response(data=serializer.data)


class CRResourceUploadView(APIView):
    """
    POST /api/cr/resources/upload/
    Accepts multipart/form-data
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description', '')
        semester = request.data.get('semester')
        subject = request.data.get('subject')
        resource_type = request.data.get('resource_type')
        file_obj = request.FILES.get('file')

        if not file_obj or not semester or not subject or not resource_type:
            return error_response(message="Please provide 'file', 'semester', 'subject', and 'resource_type'.")

        try:
            lib_entry = ResourcesService.upload_resource(
                cr_user=request.user,
                title=title,
                description=description,
                semester_id=semester,
                subject_id=subject,
                resource_type=resource_type,
                file_obj=file_obj
            )
            return success_response(
                data=ResourceLibrarySerializer(lib_entry).data,
                message="Resource Uploaded and Cataloged Successfully",
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(message=str(e))
