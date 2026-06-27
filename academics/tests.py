from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Student, CR, CRAssignment
from colleges.models import College
from academics.models import Department, Branch, Section, Semester, SubjectCatalog, SemesterSubject, SubjectUnit, SubjectTopic, DailyClassReview
from accounts.utils import TokenService

User = get_user_model()


class AcademicsAPITestCase(APITestCase):
    """
    Test suite for Academics syllabus details and Class Review API endpoints.
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

        # 2. Subjects and syllabus catalogs
        self.catalog = SubjectCatalog.objects.create(name="Database Management", code="DBMS", credits=4)
        self.subject = SemesterSubject.objects.create(semester=self.semester, subject_catalog=self.catalog)
        self.unit = SubjectUnit.objects.create(subject_catalog=self.catalog, unit_number=1, title="Unit 1 Introduction")
        self.topic = SubjectTopic.objects.create(subject_unit=self.unit, title="ER Diagrams", estimated_hours=2)

        # 3. Create CR User
        self.user_cr = User.objects.create_user(
            username="cr_user_acad", email="cracad@test.com", password="password123", role=User.Role.CR
        )
        self.student_cr = Student.objects.create(
            user=self.user_cr, register_number="STUCR01_ACAD", name="Test CR",
            email="cracad@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.cr = CR.objects.create(student=self.student_cr, is_active=True)
        self.cr_assignment = CRAssignment.objects.create(
            student=self.student_cr, semester=self.semester, branch=self.branch, section=self.section, is_active=True
        )

        # 4. Token credentials
        self.token = TokenService.generate_token(self.user_cr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_subjects(self):
        """
        Verify student can list semester subjects.
        """
        self.user_cr.role = User.Role.STUDENT
        self.user_cr.save()

        url = reverse('api-student-subjects')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"][0]["code"], "DBMS")

    def test_cr_post_daily_review(self):
        """
        Verify Class Representative can submit class reviews and topic progress coverage.
        """
        self.user_cr.role = User.Role.CR
        self.user_cr.save()

        url = reverse('api-cr-daily-reviews')
        payload = {
            "semester_subject": self.subject.id,
            "title": "DBMS Lecture 1",
            "class_date": "2026-06-27",
            "topics": [self.topic.id],
            "topics_covered": "ER diagrams introduced"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], "DBMS Lecture 1")
