from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from .models import Student, CR, CRAssignment, JoinSemesterRequest, SemesterEnrollment, SemesterReport
from .utils import TokenService
from academics.models import TimetableEntry, DailyClassReview, SemesterSubject, TopicProgress
from assignments.models import Assignment, AssignmentSubmission
from announcements.models import Announcement
from resources.models import ResourceLibrary

User = get_user_model()


class AuthService:
    @staticmethod
    def login(email, password):
        """
        Logins a student or CR using email/password. Returns signed Bearer token and user details.
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled')

        token = TokenService.generate_token(user)
        return {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }


class StudentService:
    @staticmethod
    def get_dashboard_data(student):
        """
        Compiles GPA, current class rank, recent assignments, timetable schedule, and counts.
        """
        # Active semester enrollment
        enrollment = SemesterEnrollment.objects.filter(student=student, is_active=True).first()
        gpa = enrollment.gpa if enrollment else 7.5
        rank = enrollment.rank if enrollment else 10
        completion = enrollment.completion_percentage if enrollment else 0.0

        # Schedule entries for today
        schedule = student.get_daily_schedule()
        
        # Recent assignments
        recent_assignments = Assignment.objects.filter(
            semester_subject__semester=student.semester
        ).order_by('-created_at')[:5]

        # Announcements count
        announcements_count = Announcement.objects.filter(
            semester=student.semester
        ).count()

        return {
            'gpa': gpa,
            'rank': rank,
            'completion_percentage': completion,
            'announcements_count': announcements_count,
            'today_schedule': [
                {
                    'period': entry.period_number,
                    'subject': entry.subject.subject_catalog.name,
                    'start_time': str(entry.start_time),
                    'end_time': str(entry.end_time),
                    'room': entry.room
                } for entry in schedule
            ],
            'recent_assignments': [
                {
                    'id': ass.id,
                    'title': ass.title,
                    'deadline': ass.deadline.isoformat()
                } for ass in recent_assignments
            ]
        }

    @staticmethod
    def update_profile(student, data):
        """
        Saves student profile modifications.
        """
        phone = data.get('phone')
        if phone:
            student.phone = phone
            student.save()
        return student


class CRService:
    @staticmethod
    def get_dashboard_data(cr):
        """
        CR Dashboard aggregator containing section requests and logs summaries.
        """
        # Find active class assignment for CR
        cr_assign = CRAssignment.objects.filter(student=cr.student, is_active=True).first()
        if not cr_assign:
            return {
                'pending_requests_count': 0,
                'total_reviews_submitted': 0
            }

        pending_requests = JoinSemesterRequest.objects.filter(
            semester=cr_assign.semester,
            section=cr_assign.section,
            status=JoinSemesterRequest.RequestStatus.PENDING
        ).count()

        total_reviews = DailyClassReview.objects.filter(
            cr_assignment=cr_assign
        ).count()

        return {
            'pending_requests_count': pending_requests,
            'total_reviews_submitted': total_reviews,
            'section': cr_assign.section.name,
            'semester': cr_assign.semester.semester_number
        }

    @staticmethod
    def approve_join_request(request_id, reviewer):
        """
        Transition request to approved and creates student enrollment mapping.
        """
        with transaction.atomic():
            req = JoinSemesterRequest.objects.get(id=request_id)
            if req.status != JoinSemesterRequest.RequestStatus.PENDING:
                raise exceptions.ValidationError("Request is already processed.")

            req.status = JoinSemesterRequest.RequestStatus.APPROVED
            req.reviewed_by = reviewer
            req.save()

            # Create or update Enrollment record
            enrollment, created = SemesterEnrollment.objects.get_or_create(
                student=req.student,
                semester=req.semester,
                defaults={
                    'is_active': True,
                    'gpa': 0.0,
                    'performance_score': 0.0,
                    'completion_percentage': 0.0
                }
            )
            if not created:
                enrollment.is_active = True
                enrollment.save()

            # Link student profile's semester details
            student = req.student
            student.semester = req.semester
            student.section = req.section
            student.branch = req.branch
            student.save()

            return req

    @staticmethod
    def reject_join_request(request_id, reviewer, remarks=""):
        """
        Rejects a student's join request.
        """
        req = JoinSemesterRequest.objects.get(id=request_id)
        if req.status != JoinSemesterRequest.RequestStatus.PENDING:
            raise exceptions.ValidationError("Request is already processed.")

        req.status = JoinSemesterRequest.RequestStatus.REJECTED
        req.reviewed_by = reviewer
        req.remarks = remarks
        req.save()
        return req
