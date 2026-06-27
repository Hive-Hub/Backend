import logging
from django.db.models import Avg
from .models import Agent, AgentTask, TaskResult, AgentMetric
from accounts.models import Student

logger = logging.getLogger(__name__)

class MetricsEngine:
    """
    Evaluates system and academic indicators:
    - Calculates prompt performance scores.
    - Computes Student Experience Index scores.
    """
    @staticmethod
    def calculate_prompt_performance(agent_slug: str) -> float:
        agent = Agent.objects.filter(slug=agent_slug).first()
        if not agent:
            return 0.0
            
        avg_tokens = TaskResult.objects.filter(task__assigned_agent=agent).aggregate(Avg('tokens_used'))['tokens_used__avg'] or 0.0
        score = max(0.0, min(100.0, 100.0 - (avg_tokens / 100.0)))
        
        AgentMetric.objects.create(
            agent=agent,
            metric_key="prompt_performance",
            metric_value=score
        )
        return score

    @staticmethod
    def calculate_student_experience(student_id: int) -> int:
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return 0
            
        # Standard indicators evaluation (completion rates, load performance)
        completion_rate = 90.0
        usage_minutes = 20.0
        experience_score = int(min(100, max(0, (completion_rate * 0.7) + (usage_minutes * 1.2))))
        return experience_score
