import logging
from django.utils import timezone
from .models import Agent, AgentHealth, AgentWorkflow, WorkflowStep, SystemHealth, DatabaseHealth, APIHealth, StudentAnalytics, Alert, Recommendation
from .health import HealthMonitor
from .metrics import MetricsEngine
from accounts.models import Student

logger = logging.getLogger(__name__)

class AgentOSScheduler:
    """
    Schedules background tasks:
    - Every Minute: Agent Health
    - Every 5 Minutes: Workflow Status
    - Every 10 Minutes: API Health
    - Every Hour: Database Health
    - Every Day: Analytics, Recommendations, Optimization Reports
    """
    
    @staticmethod
    def run_minute_jobs():
        logger.info("Scheduler: Running 1-minute background jobs (Agent Health)...")
        for agent in Agent.objects.filter(is_active=True):
            AgentHealth.objects.create(
                agent=agent,
                status=agent.status,
                avg_response_time=150.0,
                avg_execution_time=250.0,
                error_count=0,
                retry_count=0,
                last_executed_at=timezone.now()
            )

    @staticmethod
    def run_five_minute_jobs():
        logger.info("Scheduler: Running 5-minute background jobs (Workflow status checks)...")
        active_steps = WorkflowStep.objects.filter(status=WorkflowStep.StepStatus.IN_PROGRESS)
        for step in active_steps:
            elapsed = (timezone.now() - step.updated_at).total_seconds()
            if elapsed > step.timeout_seconds:
                logger.warning(f"Step {step.step_number} in workflow {step.workflow.name} timed out!")
                step.status = WorkflowStep.StepStatus.FAILED
                step.save()

    @staticmethod
    def run_ten_minute_jobs():
        logger.info("Scheduler: Running 10-minute background jobs (API Health)...")
        HealthMonitor.audit_api()

    @staticmethod
    def run_hourly_jobs():
        logger.info("Scheduler: Running hourly background jobs (Database & System Health)...")
        HealthMonitor.audit_system()
        HealthMonitor.audit_database()

    @staticmethod
    def run_daily_jobs():
        logger.info("Scheduler: Running daily background jobs (Student Analytics & Recommendations)...")
        HealthMonitor.audit_storage()
        
        for student in Student.objects.all():
            score = MetricsEngine.calculate_student_experience(student.id)
            
            StudentAnalytics.objects.update_or_create(
                student=student,
                defaults={
                    "dashboard_load_time": 0.45,
                    "assignment_completion_rate": 88.0,
                    "experience_score": score,
                    "progress_status": "ON_TRACK" if score >= 75 else "AT_RISK"
                }
            )
            
            if score < 50:
                Alert.objects.create(
                    title="Low Experience Index Warning",
                    message=f"Student {student.name} is experiencing low performance indicators (index score: {score}).",
                    alert_type=Alert.AlertType.ACADEMIC,
                    severity=Alert.Severity.WARNING,
                    student=student
                )
                Recommendation.objects.create(
                    title="Assignment Completion Followup",
                    message="Recommend reviewing weak topic lectures and assignment submissions.",
                    category=Recommendation.Category.ACADEMIC,
                    student=student
                )
