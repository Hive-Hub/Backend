from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Assignment, AssignmentSubmission, QuestionBank
from accounts.models import Student, CR
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer, QuestionBankSerializer
from accounts.permissions import IsStudent, IsCR, JWTAuthentication
from accounts.utils import success_response, error_response
from accounts.pagination import StandardResultsSetPagination
from .services import AssignmentService


class StudentAssignmentsListView(ListAPIView):
    """
    GET /api/student/assignments/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    serializer_class = AssignmentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return Assignment.objects.none()
            
        return Assignment.objects.filter(
            semester_subject__semester=student.semester,
            assignment_type=Assignment.AssignmentType.COLLEGE
        ).order_by('-deadline')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class StudentAssignmentDetailView(RetrieveAPIView):
    """
    GET /api/student/assignments/<id>/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return Assignment.objects.none()
        return Assignment.objects.filter(semester_subject__semester=student.semester)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


class StudentAssignmentSubmitView(APIView):
    """
    POST /api/student/assignments/<id>/submit/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def post(self, request, pk):
        try:
            submission = AssignmentService.submit_assignment(request.user, pk, request.data)
            return success_response(
                data=AssignmentSubmissionSerializer(submission).data, 
                message="Assignment Submitted Successfully", 
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(message=str(e))


class StudentAIAssignmentsListView(ListAPIView):
    """
    GET /api/student/ai-assignments/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    serializer_class = AssignmentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return Assignment.objects.none()
            
        return Assignment.objects.filter(
            semester_subject__semester=student.semester,
            assignment_type=Assignment.AssignmentType.AI_GENERATED
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class StudentQuestionBankListView(ListAPIView):
    """
    GET /api/student/question-bank/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    serializer_class = QuestionBankSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return QuestionBank.objects.none()
            
        return QuestionBank.objects.filter(
            subject__semester=student.semester
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class CRAssignmentsView(APIView):
    """
    POST /api/cr/assignments/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def post(self, request):
        try:
            assignment = AssignmentService.create_assignment(request.user, request.data)
            return success_response(
                data=AssignmentSerializer(assignment).data, 
                message="College Assignment Created Successfully", 
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(message=str(e))


class CRGenerateAIQuestionsView(APIView):
    """
    POST /api/cr/generate-questions/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def post(self, request):
        review_id = request.data.get('review_id')
        if not review_id:
            return error_response(message="Please provide 'review_id'.")
            
        try:
            assignment = AssignmentService.generate_ai_questions(request.user, review_id)
            return success_response(
                data=AssignmentSerializer(assignment).data, 
                message="AI Questions and Quiz generated successfully", 
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(message=str(e))
