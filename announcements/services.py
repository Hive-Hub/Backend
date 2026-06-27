from django.core.exceptions import ValidationError
from rest_framework import exceptions

from .models import Announcement
from accounts.models import Student, CR, CRAssignment
from academics.models import Semester
from .validators import validate_announcement_length


class AnnouncementService:
    @staticmethod
    def create_announcement(cr_user, data):
        """
        Creates a section announcement inside the system.
        """
        title = data.get('title')
        message = data.get('message')
        semester_id = data.get('semester')

        try:
            student = Student.objects.get(user=cr_user)
            cr = CR.objects.get(student=student, is_active=True)
            cr_assign = CRAssignment.objects.get(student=student, is_active=True)
        except (Student.DoesNotExist, CR.DoesNotExist, CRAssignment.DoesNotExist):
            raise exceptions.ValidationError("User is not an active CR.")

        try:
            sem = Semester.objects.get(id=semester_id)
        except Semester.DoesNotExist:
            raise exceptions.ValidationError("Invalid Semester.")

        validate_announcement_length(message)

        return Announcement.objects.create(
            title=title,
            message=message,
            created_by=cr,
            semester=sem
        )
