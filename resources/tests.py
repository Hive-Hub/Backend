from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import Student, CR, CRAssignment
from colleges.models import College
from academics.models import Department, Branch, Section, Semester, SubjectCatalog, SemesterSubject
from accounts.utils import TokenService

User = get_user_model()


class ResourcesAPITestCase(APITestCase):
    """
    Test suite for Resources API uploads and filtering.
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

        self.catalog = SubjectCatalog.objects.create(name="Database Management", code="DBMS", credits=4)
        self.subject = SemesterSubject.objects.create(semester=self.semester, subject_catalog=self.catalog)

        # 2. Setup Student / CR
        self.user_cr = User.objects.create_user(
            username="cr_user_res", email="crres@test.com", password="password123", role=User.Role.CR
        )
        self.student_cr = Student.objects.create(
            user=self.user_cr, register_number="STUCR01_RES", name="Test CR",
            email="crres@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.cr = CR.objects.create(student=self.student_cr, is_active=True)
        self.cr_assignment = CRAssignment.objects.create(
            student=self.student_cr, semester=self.semester, branch=self.branch, section=self.section, is_active=True
        )

        self.token = TokenService.generate_token(self.user_cr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_cr_upload_file_resource(self):
        """
        Verify Class Representative can upload files using multipart content type.
        """
        # Create a mock PDF file
        mock_file = SimpleUploadedFile(
            "test_notes.pdf",
            b"Mock pdf file bytes contents",
            content_type="application/pdf"
        )

        url = reverse('api-cr-resources-upload')
        payload = {
            "title": "DBMS Reference Notes",
            "description": "Important reference queries notes",
            "semester": self.semester.id,
            "subject": self.subject.id,
            "resource_type": "NOTES",
            "file": mock_file
        }
        
        response = self.client.post(url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["file_name"], "test_notes.pdf")

    def test_get_resources_filter(self):
        """
        Verify filtering resources by semester and subject works.
        """
        url = reverse('api-resources-list') + f"?semester={self.semester.id}&subject=DBMS"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
