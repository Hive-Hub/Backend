import logging
from ..models import Agent, AgentTask

logger = logging.getLogger(__name__)


class AgentTaskPlanner:
    """
    Manager class to assist with planning agent tasks and allocations.
    """

    @staticmethod
    def create_task_and_assign(title, description, priority, agent_slug, user):
        """
        Creates an AgentTask and assigns it to the designated agent.
        """
        agent = Agent.objects.filter(slug=agent_slug, is_active=True).first()
        task = AgentTask.objects.create(
            title=title,
            description=description,
            priority=priority,
            assigned_agent=agent,
            created_by=user
        )
        return task
