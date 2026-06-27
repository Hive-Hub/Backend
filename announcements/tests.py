from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Student, CR, CRAssignment
from colleges.models import College
from academics.models import Department, Branch, Section, Semester
from announcements.models import Announcement
from accounts.utils import TokenService

User = get_user_model()


class AnnouncementsAPITestCase(APITestCase):
    """
    Test suite for Announcements API endpoints.
    """

    def setUp(self):
        # 1. Setup metadata structure
        self.college = College.objects.create(name="QIS College", code="QISC")
        self.dept = Department.objects.create(college=self.college, name="Computer Science", code="CS")
        self.branch = Branch.objects.create(department=self.dept, name="Software Eng", code="SE")
        self.section = Section.objects.create(branch=self.branch, name="A")
        self.semester = Semester.objects.create(
            department=self.dept, section=self.section, semester_number=1,
            start_date="2026-01-01", end_date="2026-06-30"
        )

        # 2. Setup Student / CR
        self.user_cr = User.objects.create_user(
            username="cr_user_ann", email="crann@test.com", password="password123", role=User.Role.CR
        )
        self.student_cr = Student.objects.create(
            user=self.user_cr, register_number="STUCR01_ANN", name="Test CR",
            email="crann@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.cr = CR.objects.create(student=self.student_cr, is_active=True)
        self.cr_assignment = CRAssignment.objects.create(
            student=self.student_cr, semester=self.semester, branch=self.branch, section=self.section, is_active=True
        )

        self.token = TokenService.generate_token(self.user_cr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_cr_create_announcement(self):
        """
        Verify Class Representative can create announcements.
        """
        url = reverse('api-cr-announcements')
        payload = {
            "title": "Exam postposed",
            "message": "The exam is rescheduled to next week.",
            "semester": self.semester.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], "Exam postposed")

    def test_student_get_announcements(self):
        """
        Verify student can list announcements.
        """
        self.user_cr.role = User.Role.STUDENT
        self.user_cr.save()

        # create a dummy announcement
        Announcement.objects.create(
            title="Class Notice",
            message="No classes tomorrow.",
            created_by=self.cr,
            semester=self.semester
        )

        url = reverse('api-student-announcements')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(len(response.data["data"]["results"]) > 0)
