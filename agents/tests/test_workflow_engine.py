from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from ..models import Agent, AgentWorkflow, WorkflowStep, AgentTask, TaskResult, AgentCapability
from ..registry import AgentRegistry
from ..workflow_engine import WorkflowEngine
from ..orchestrator import Orchestrator

User = get_user_model()

class WorkflowEngineTestCase(TestCase):
    """
    Unit tests asserting Sequential, Parallel, and Conditional engine flows.
    """
    
    def setUp(self):
        AgentRegistry.setup_defaults()
        
        self.wf = AgentWorkflow.objects.create(
            name="Test Engine Workflow",
            description="Workflow testing engine components",
            active=True
        )
        
        self.agent_pm = Agent.objects.get(slug="project-manager")
        self.agent_db = Agent.objects.get(slug="database-architect")
        
        self.step1 = WorkflowStep.objects.create(
            workflow=self.wf,
            step_number=1,
            name="First Step",
            agent=self.agent_pm,
            status=WorkflowStep.StepStatus.PENDING,
            is_critical=True
        )
        self.step2 = WorkflowStep.objects.create(
            workflow=self.wf,
            step_number=2,
            name="Second Step",
            agent=self.agent_db,
            status=WorkflowStep.StepStatus.PENDING,
            is_critical=True,
            depends_on_steps=[1]
        )

    @patch('agents.executors.llm_executor.LLMExecutor.execute')
    def test_sequential_execution(self, mock_execute):
        mock_execute.return_value = {
            "status": "SUCCESS",
            "output": "Mock output data",
            "tokens_used": 15,
            "execution_time": 0.05
        }
        
        engine = WorkflowEngine(self.wf.id)
        status_res = engine.execute("Start Task")
        
        self.assertEqual(status_res, "COMPLETED")
        self.step1.refresh_from_db()
        self.step2.refresh_from_db()
        
        self.assertEqual(self.step1.status, WorkflowStep.StepStatus.COMPLETED)
        self.assertEqual(self.step2.status, WorkflowStep.StepStatus.COMPLETED)

    @patch('agents.executors.llm_executor.LLMExecutor.execute')
    def test_retry_on_failure(self, mock_execute):
        mock_execute.side_effect = [
            {"status": "FAILED", "error_message": "Transient LLM Failure"},
            {"status": "SUCCESS", "output": "Recovered output", "tokens_used": 10, "execution_time": 0.01}
        ]
        
        self.step1.max_retries = 3
        self.step1.save()
        self.step2.delete()
        
        engine = WorkflowEngine(self.wf.id)
        status_res = engine.execute("Start Task")
        
        self.assertEqual(status_res, "COMPLETED")
        self.step1.refresh_from_db()
        self.assertEqual(self.step1.status, WorkflowStep.StepStatus.COMPLETED)
        self.assertEqual(self.step1.retry_count, 1)

    @patch('agents.executors.llm_executor.LLMExecutor.execute')
    def test_conditional_skip_logic(self, mock_execute):
        mock_execute.return_value = {
            "status": "SUCCESS",
            "output": "Contains error in schema definition",
            "tokens_used": 5
        }
        
        self.step3 = WorkflowStep.objects.create(
            workflow=self.wf,
            step_number=3,
            name="Conditional Step",
            agent=self.agent_pm,
            status=WorkflowStep.StepStatus.PENDING,
            input_mapping={"skip_if": {"previous_step": 1, "contains": "error"}},
            depends_on_steps=[1, 2]
        )
        
        engine = WorkflowEngine(self.wf.id)
        status_res = engine.execute("Start Task")
        
        self.assertEqual(status_res, "COMPLETED")
        self.step3.refresh_from_db()
        self.assertEqual(self.step3.status, WorkflowStep.StepStatus.SKIPPED)


class OrchestrationTestCase(APITestCase):
    """
    Test suite for the Orchestrator request parsing and endpoint triggers.
    """

    def setUp(self):
        AgentRegistry.setup_defaults()
        self.admin = User.objects.create_user(
            username="admin_orchestrator", email="ao@test.com", password="pwd", role="ADMIN"
        )
        
    def test_capability_discovery(self):
        matches = AgentRegistry.discover_capabilities("orchestration")
        self.assertTrue(matches.exists())
        self.assertEqual(matches.first().slug, "orchestrator")

    @patch('agents.adapters.llm_adapter.LLMAdapter.call')
    def test_workflow_run_endpoint(self, mock_llm):
        mock_llm.return_value = {
            "success": True,
            "text": '{"workflow_name": "Mock Dynamic Workflow", "description": "Dynamic testing", "steps": [{"step_number": 1, "name": "Dynamic task step", "agent_type": "PROJECT_MANAGER", "depends_on": []}]}'
        }
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('workflow-run')
        response = self.client.post(url, {"user_request": "Create database schema for student tracking"}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "COMPLETED")
        self.assertTrue(len(response.data["results"]) > 0)
