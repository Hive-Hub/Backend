from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from accounts.models import Student, CR, CRAssignment
from colleges.models import College
from academics.models import Department, Branch, Section, Semester, SubjectCatalog, SemesterSubject, DailyClassReview
from assignments.models import Assignment, AssignmentSubmission
from accounts.utils import TokenService

User = get_user_model()


class AssignmentsAPITestCase(APITestCase):
    """
    Test suite for Assignments submissions and AI generation endpoints.
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
            username="cr_user_assign", email="crassign@test.com", password="password123", role=User.Role.CR
        )
        self.student_cr = Student.objects.create(
            user=self.user_cr, register_number="STUCR01_ASSIGN", name="Test CR",
            email="crassign@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section, semester=self.semester
        )
        self.cr = CR.objects.create(student=self.student_cr, is_active=True)
        self.cr_assignment = CRAssignment.objects.create(
            student=self.student_cr, semester=self.semester, branch=self.branch, section=self.section, is_active=True
        )

        # 3. Create normal assignment
        self.assignment = Assignment.objects.create(
            title="DBMS HW 1",
            description="Normal HW details",
            deadline=timezone.now() + timezone.timedelta(days=2),
            semester_subject=self.subject,
            created_by=self.cr,
            assignment_type=Assignment.AssignmentType.COLLEGE
        )

        # 4. Daily class review for AI trigger
        self.review = DailyClassReview.objects.create(
            semester_subject=self.subject,
            cr_assignment=self.cr_assignment,
            title="Normal SQL class review",
            class_date="2026-06-27",
            topics_covered="Select statements"
        )

        self.token = TokenService.generate_token(self.user_cr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_student_submit_assignment(self):
        """
        Verify student can submit answers for assignment.
        """
        self.user_cr.role = User.Role.STUDENT
        self.user_cr.save()

        url = reverse('api-student-assignments-submit', kwargs={'pk': self.assignment.id})
        payload = {
            "answers": {
                "question1": "A"
            }
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["score"], 85)

    def test_cr_generate_ai_questions(self):
        """
        Verify CR can trigger AI questions from class review.
        """
        self.user_cr.role = User.Role.CR
        self.user_cr.save()

        url = reverse('api-cr-generate-questions')
        payload = {
            "review_id": self.review.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["assignment_type"], "AI_GENERATED")
