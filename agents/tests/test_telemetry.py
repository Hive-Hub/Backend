from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Agent, AgentTask, AgentWorkflow, AgentPrompt, StudentAnalytics, Alert, Recommendation
from ..registry import AgentRegistry
from ..services.monitoring_service import MonitoringService
from colleges.models import College
from academics.models import Department, Branch, Section, Semester
from accounts.models import Student, CR

User = get_user_model()


class AgentModelTestCase(TestCase):
    """
    Test suite for Agent models and Registry setup.
    """

    def setUp(self):
        # Clear out existing agents to avoid unique-constraint collisions in registry test
        Agent.objects.all().delete()

    def test_registry_setup_defaults(self):
        """
        Verify setup_defaults creates 11 distinct agents and the Developer Workflow.
        """
        created = AgentRegistry.setup_defaults()
        self.assertEqual(len(created), 11)
        self.assertEqual(Agent.objects.count(), 11)
        
        workflow = AgentWorkflow.objects.filter(name="Developer Workflow").first()
        self.assertIsNotNone(workflow)
        self.assertTrue(len(workflow.steps) > 0)
        
        agent_pm = Agent.objects.get(slug="project-manager")
        self.assertTrue(AgentPrompt.objects.filter(agent=agent_pm).exists())


class AgentPermissionTestCase(APITestCase):
    """
    Verify agent management safety controls.
    """

    def setUp(self):
        AgentRegistry.setup_defaults()
        self.student_user = User.objects.create_user(
            username="student_user", email="student@test.com", password="pwd", role="STUDENT"
        )
        self.admin_user = User.objects.create_user(
            username="admin_user", email="admin@test.com", password="pwd", role="ADMIN"
        )

    def test_student_no_access(self):
        """
        Verify Students have no access to listing or writing agents.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('agent-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MonitoringTelemetryTestCase(APITestCase):
    """
    Test suite for Student score calculations, role filtering, and export views.
    """

    def setUp(self):
        AgentRegistry.setup_defaults()
        
        # 1. Create College, Department, Branch, Section, and Semester
        self.college = College.objects.create(name="Engineering College", code="EC")
        self.dept = Department.objects.create(college=self.college, name="Computer Science", code="CS_DEPT")
        self.branch = Branch.objects.create(department=self.dept, name="AI Engineering", code="AI_BR")
        self.section_a = Section.objects.create(branch=self.branch, name="A")
        self.section_b = Section.objects.create(branch=self.branch, name="B")
        self.sem_a = Semester.objects.create(department=self.dept, section=self.section_a, semester_number=1, start_date="2026-01-01", end_date="2026-06-30")
        self.sem_b = Semester.objects.create(department=self.dept, section=self.section_b, semester_number=1, start_date="2026-01-01", end_date="2026-06-30")

        # 2. Create Student users
        self.user_s1 = User.objects.create_user(username="student1", email="s1@test.com", password="pwd", role="STUDENT")
        self.user_s2 = User.objects.create_user(username="student2", email="s2@test.com", password="pwd", role="STUDENT")
        
        # Student profiles
        self.student1 = Student.objects.create(
            user=self.user_s1, register_number="REG01", name="Student One",
            email="s1@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section_a, semester=self.sem_a
        )
        self.student2 = Student.objects.create(
            user=self.user_s2, register_number="REG02", name="Student Two",
            email="s2@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section_b, semester=self.sem_b
        )

        # 3. Create CR user
        self.user_cr = User.objects.create_user(username="cr1", email="cr1@test.com", password="pwd", role="CR")
        self.student_cr = Student.objects.create(
            user=self.user_cr, register_number="REGCR", name="CR Name",
            email="cr1@test.com", college=self.college, department=self.dept,
            branch=self.branch, section=self.section_a, semester=self.sem_a
        )
        self.cr = CR.objects.create(student=self.student_cr, is_active=True)

        # 4. Create Admin user
        self.user_admin = User.objects.create_user(username="admin1", email="admin1@test.com", password="pwd", role="ADMIN")

        # 5. Populate analytics for both students
        self.sa1 = StudentAnalytics.objects.create(student=self.student1, experience_score=85, progress_status="ON_TRACK")
        self.sa2 = StudentAnalytics.objects.create(student=self.student2, experience_score=45, progress_status="AT_RISK")

    def test_monitoring_agent_registered(self):
        """
        Verify that the Monitoring Agent is registered and loadable.
        """
        agent = Agent.objects.filter(slug="monitoring-intelligence").first()
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_type, Agent.AgentType.MONITORING)

    def test_experience_score_calculation(self):
        """
        Verify calculation returns a baseline score between 0 and 100.
        """
        score = MonitoringService.calculate_student_experience_score(self.student1)
        self.assertTrue(0 <= score <= 100)

    def test_student_row_level_filtering(self):
        """
        Asserts Student role can only see their own analytics logs.
        """
        self.client.force_authenticate(user=self.user_s1)
        response = self.client.get(reverse('student-analytics-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student'], self.student1.id)

    def test_cr_row_level_filtering(self):
        """
        Asserts CR can only see analytics of students within their assigned section A.
        """
        self.client.force_authenticate(user=self.user_cr)
        response = self.client.get(reverse('student-analytics-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student'], self.student1.id)

    def test_admin_row_level_filtering(self):
        """
        Asserts Admin can view all student records.
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(reverse('student-analytics-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_reports_export_formats(self):
        """
        Verifies exporting views for CSV, Excel, and PDF formats return correct headers.
        """
        self.client.force_authenticate(user=self.user_admin)
        
        # Test CSV export
        url = reverse('report-export') + "?export_format=csv&metric=student_analytics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')

        # Test Excel export
        url = reverse('report-export') + "?export_format=excel&metric=student_analytics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.ms-excel')

        # Test PDF (HTML layout) export
        url = reverse('report-export') + "?export_format=pdf&metric=student_analytics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html')
