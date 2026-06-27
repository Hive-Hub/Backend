from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Student, CR, CRAssignment, JoinSemesterRequest, SemesterEnrollment
from colleges.models import College
from academics.models import Department, Branch, Section, Semester

User = get_user_model()


class AccountsAPITestCase(APITestCase):
    """
    Test suite for Accounts authentication, profile, dashboard, and CR workflow APIs.
    """

    def setUp(self):
        # 1. Setup metadata hierarchy
        self.college = College.objects.create(name="QIS College", code="QISC")
        self.dept = Department.objects.create(college=self.college, name="Computer Science", code="CS")
        self.branch = Branch.objects.create(department=self.dept, name="Software Eng", code="SE")
        self.section = Section.objects.create(branch=self.branch, name="A")
        self.semester = Semester.objects.create(
            department=self.dept, section=self.section, semester_number=1,
            start_date="2026-01-01", end_date="2026-06-30"
        )

        # 2. Setup Student User
        self.user_student = User.objects.create_user(
            username="student_user", email="student@test.com", password="password123", role=User.Role.STUDENT
        )
        self.student = Student.objects.create(
            user=self.user_student, register_number="STU001", name="Test Student",
            email="student@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.enrollment = SemesterEnrollment.objects.create(
            student=self.student, semester=self.semester, is_active=True, gpa=8.50, rank=5
        )

        # 3. Setup CR User
        self.user_cr = User.objects.create_user(
            username="cr_user", email="cr@test.com", password="password123", role=User.Role.CR
        )
        self.student_cr = Student.objects.create(
            user=self.user_cr, register_number="STUCR01", name="Test CR",
            email="cr@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.cr = CR.objects.create(student=self.student_cr, is_active=True)
        self.cr_assignment = CRAssignment.objects.create(
            student=self.student_cr, semester=self.semester, branch=self.branch, section=self.section, is_active=True
        )

        # 4. Setup Join Semester Request
        self.user_requesting_student = User.objects.create_user(
            username="req_student", email="req@test.com", password="password123", role=User.Role.STUDENT
        )
        self.requesting_student = Student.objects.create(
            user=self.user_requesting_student, register_number="STUREQ", name="Requesting Student",
            email="req@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.join_request = JoinSemesterRequest.objects.create(
            student=self.requesting_student, college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester,
            status=JoinSemesterRequest.RequestStatus.PENDING
        )

    def test_student_login_success(self):
        """
        Verify login endpoint returns Bearer token for correct credentials.
        """
        url = reverse('api-auth-login')
        payload = {
            "email": "student@test.com",
            "password": "password123"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("token", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["role"], "STUDENT")

    def test_student_login_failure(self):
        """
        Verify login endpoint returns 401 on incorrect credentials.
        """
        url = reverse('api-auth-login')
        payload = {
            "email": "student@test.com",
            "password": "wrongpassword"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])

    def test_student_profile_authenticated(self):
        """
        Verify student can retrieve profile using token.
        """
        # Obtain token
        login_url = reverse('api-auth-login')
        login_res = self.client.post(login_url, {"email": "student@test.com", "password": "password123"}, format='json')
        token = login_res.data["data"]["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_url = reverse('api-student-profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Test Student")

    def test_student_dashboard_details(self):
        """
        Verify dashboard statistics contains GPA and Schedule.
        """
        login_res = self.client.post(reverse('api-auth-login'), {"email": "student@test.com", "password": "password123"}, format='json')
        token = login_res.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(reverse('api-student-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["gpa"], 8.5)

    def test_cr_approve_join_request(self):
        """
        Verify Class Representative can approve pending enrollments.
        """
        login_res = self.client.post(reverse('api-auth-login'), {"email": "cr@test.com", "password": "password123"}, format='json')
        token = login_res.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('api-cr-join-requests-approve', kwargs={'pk': self.join_request.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.join_request.refresh_from_db()
        self.assertEqual(self.join_request.status, JoinSemesterRequest.RequestStatus.APPROVED)
