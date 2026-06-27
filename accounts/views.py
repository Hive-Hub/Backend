from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView

from .models import Student, CR, CRAssignment, SemesterEnrollment, JoinSemesterRequest, SemesterReport, SubjectProgress
from agents.models import StudentAnalytics, Alert
from .serializers import (
    LoginSerializer, StudentProfileSerializer, CRSerializer, 
    JoinSemesterRequestSerializer, SemesterReportSerializer, 
    SubjectProgressSerializer
)
from agents.serializers import AlertSerializer
from .permissions import IsStudent, IsCR, JWTAuthentication
from .services import AuthService, StudentService, CRService
from .utils import success_response, error_response
from .pagination import StandardResultsSetPagination


class LoginView(APIView):
    """
    POST /api/auth/login/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            res = AuthService.login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            return success_response(data=res, message="Login Successful")
        return error_response(errors=serializer.errors)


class StudentProfileView(APIView):
    """
    GET /api/student/profile/
    PATCH /api/student/profile/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentProfileSerializer(student)
        return success_response(data=serializer.data)

    def patch(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentProfileSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            updated = StudentService.update_profile(student, serializer.validated_data)
            return success_response(data=StudentProfileSerializer(updated).data, message="Profile Updated")
        return error_response(errors=serializer.errors)


class StudentDashboardView(APIView):
    """
    GET /api/student/dashboard/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)
            
        data = StudentService.get_dashboard_data(student)
        return success_response(data=data)


class StudentReportsView(APIView):
    """
    GET /api/student/reports/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)
            
        reports = SemesterReport.objects.filter(student=student).order_by('-generated_at')
        serializer = SemesterReportSerializer(reports, many=True)
        return success_response(data=serializer.data)


class StudentNotificationsView(ListAPIView):
    """
    GET /api/student/notifications/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    serializer_class = AlertSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return Alert.objects.none()
            
        return Alert.objects.filter(student=student).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class CRDashboardView(APIView):
    """
    GET /api/cr/dashboard/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def get(self, request):
        try:
            cr = CR.objects.get(student__user=request.user, is_active=True)
        except CR.DoesNotExist:
            return error_response(message="Active CR profile not found", status_code=status.HTTP_404_NOT_FOUND)
            
        data = CRService.get_dashboard_data(cr)
        return success_response(data=data)


class CRJoinRequestsView(APIView):
    """
    GET /api/cr/join-requests/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def get(self, request):
        try:
            cr = CR.objects.get(student__user=request.user, is_active=True)
            cr_assign = CRAssignment.objects.get(student=cr.student, is_active=True)
        except (CR.DoesNotExist, CRAssignment.DoesNotExist):
            return error_response(message="Active CR assignment not found", status_code=status.HTTP_404_NOT_FOUND)

        reqs = JoinSemesterRequest.objects.filter(
            semester=cr_assign.semester,
            section=cr_assign.section,
            status=JoinSemesterRequest.RequestStatus.PENDING
        ).order_by('-created_at')
        
        serializer = JoinSemesterRequestSerializer(reqs, many=True)
        return success_response(data=serializer.data)


class CRJoinRequestApproveView(APIView):
    """
    POST /api/cr/join-requests/<id>/approve/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def post(self, request, pk):
        try:
            req = CRService.approve_join_request(pk, request.user)
            return success_response(data=JoinSemesterRequestSerializer(req).data, message="Request Approved")
        except JoinSemesterRequest.DoesNotExist:
            return error_response(message="Join request not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(message=str(e))


class CRJoinRequestRejectView(APIView):
    """
    POST /api/cr/join-requests/<id>/reject/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def post(self, request, pk):
        remarks = request.data.get('remarks', '')
        try:
            req = CRService.reject_join_request(pk, request.user, remarks)
            return success_response(data=JoinSemesterRequestSerializer(req).data, message="Request Rejected")
        except JoinSemesterRequest.DoesNotExist:
            return error_response(message="Join request not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(message=str(e))


class CRStudentProgressView(APIView):
    """
    GET /api/cr/student-progress/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def get(self, request):
        try:
            cr = CR.objects.get(student__user=request.user, is_active=True)
            cr_assign = CRAssignment.objects.get(student=cr.student, is_active=True)
        except (CR.DoesNotExist, CRAssignment.DoesNotExist):
            return error_response(message="Active CR assignment not found", status_code=status.HTTP_404_NOT_FOUND)

        # Get subject progress for all students in section
        students = Student.objects.filter(section=cr_assign.section, semester=cr_assign.semester)
        progress = SubjectProgress.objects.filter(student__in=students)
        
        serializer = SubjectProgressSerializer(progress, many=True)
        return success_response(data=serializer.data)
