from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import SemesterSubject, SubjectUnit, SubjectTopic, TimetableEntry, DailyClassReview
from accounts.models import Student, CR, CRAssignment, SubjectProgress
from .serializers import (
    SemesterSubjectSerializer, SubjectUnitSerializer, SubjectTopicSerializer, 
    TimetableEntrySerializer, DailyClassReviewSerializer, TopicProgressSerializer
)
from accounts.permissions import IsStudent, IsCR, JWTAuthentication
from accounts.utils import success_response, error_response
from .services import AcademicsService


class StudentSubjectsView(APIView):
    """
    GET /api/student/subjects/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)

        subjects = SemesterSubject.objects.filter(semester=student.semester)
        serializer = SemesterSubjectSerializer(subjects, many=True)
        return success_response(data=serializer.data)


class SubjectUnitsView(APIView):
    """
    GET /api/student/subjects/<id>/units/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request, pk):
        try:
            student = Student.objects.get(user=request.user)
            sem_subj = SemesterSubject.objects.get(id=pk, semester=student.semester)
        except (Student.DoesNotExist, SemesterSubject.DoesNotExist):
            return error_response(message="Semester Subject not found", status_code=status.HTTP_404_NOT_FOUND)

        units = SubjectUnit.objects.filter(subject_catalog=sem_subj.subject_catalog).order_by('unit_number')
        serializer = SubjectUnitSerializer(units, many=True)
        return success_response(data=serializer.data)


class UnitTopicsView(APIView):
    """
    GET /api/student/units/<id>/topics/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request, pk):
        try:
            unit = SubjectUnit.objects.get(id=pk)
        except SubjectUnit.DoesNotExist:
            return error_response(message="Subject Unit not found", status_code=status.HTTP_404_NOT_FOUND)

        topics = SubjectTopic.objects.filter(subject_unit=unit)
        serializer = SubjectTopicSerializer(topics, many=True)
        return success_response(data=serializer.data)


class StudentScheduleView(APIView):
    """
    GET /api/student/schedule/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)

        entries = student.get_daily_schedule()
        serializer = TimetableEntrySerializer(entries, many=True)
        return success_response(data=serializer.data)


class StudentProgressView(APIView):
    """
    GET /api/student/progress/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return error_response(message="Student profile not found", status_code=status.HTTP_404_NOT_FOUND)

        progress = SubjectProgress.objects.filter(student=student)
        serializer = SubjectProgressSerializer(progress, many=True)
        return success_response(data=serializer.data)


class CRSubjectsView(APIView):
    """
    GET /api/cr/subjects/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def get(self, request):
        try:
            cr = CR.objects.get(student__user=request.user, is_active=True)
            cr_assign = CRAssignment.objects.get(student=cr.student, is_active=True)
        except (CR.DoesNotExist, CRAssignment.DoesNotExist):
            return error_response(message="Active CR assignment not found", status_code=status.HTTP_404_NOT_FOUND)

        subjects = SemesterSubject.objects.filter(semester=cr_assign.semester)
        serializer = SemesterSubjectSerializer(subjects, many=True)
        return success_response(data=serializer.data)


class CRDailyClassReviewsView(APIView):
    """
    GET /api/cr/daily-reviews/
    POST /api/cr/daily-reviews/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCR]

    def get(self, request):
        try:
            cr = CR.objects.get(student__user=request.user, is_active=True)
            cr_assign = CRAssignment.objects.get(student=cr.student, is_active=True)
        except (CR.DoesNotExist, CRAssignment.DoesNotExist):
            return error_response(message="Active CR assignment not found", status_code=status.HTTP_404_NOT_FOUND)

        reviews = DailyClassReview.objects.filter(cr_assignment=cr_assign).order_by('-class_date')
        serializer = DailyClassReviewSerializer(reviews, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        try:
            review = AcademicsService.create_daily_review(request.user, request.data)
            return success_response(
                data=DailyClassReviewSerializer(review).data, 
                message="Daily Class Review Submitted", 
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(message=str(e))
