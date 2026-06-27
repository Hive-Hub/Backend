import logging
from django.utils import timezone
from ..models import AgentExecution, AgentLog, Agent

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    WorkflowEngine implements the low-level step execution logic, dependency resolving,
    and transitions of workflows.
    """

    @staticmethod
    def execute_step(task, agent, step, input_data):
        """
        Executes a single step of a workflow.
        """
        from ..registry import AgentRegistry

        # Set status
        agent.status = Agent.Status.BUSY
        agent.save()

        execution = AgentExecution.objects.create(
            task=task,
            agent=agent,
            input=input_data,
            status=AgentExecution.Status.RUNNING,
            started_at=timezone.now()
        )

        AgentLog.objects.create(
            execution=execution,
            agent=agent,
            level="INFO",
            message=f"Engine executing step {step.get('step_number')}: {step.get('description', '')}"
        )

        try:
            executor = AgentRegistry.get_executor(agent)
            result = executor.execute(task=task, input_data=input_data)

            execution.output = result.get("output", "")
            execution.status = AgentExecution.Status.SUCCESS if result.get("status") == "SUCCESS" else AgentExecution.Status.FAILED
            execution.execution_time = result.get("execution_time", 0.0)
            execution.tokens_used = result.get("tokens_used", 0)
            execution.error_message = result.get("error_message", "")
            execution.finished_at = timezone.now()
            execution.save()

            agent.status = Agent.Status.IDLE
            agent.save()

            return {
                "success": execution.status == AgentExecution.Status.SUCCESS,
                "execution": execution,
                "output": execution.output,
                "error": execution.error_message
            }
        except Exception as e:
            logger.error(f"Engine exception during execution of {agent.name}: {str(e)}")
            execution.status = AgentExecution.Status.FAILED
            execution.error_message = str(e)
            execution.finished_at = timezone.now()
            execution.save()

            agent.status = Agent.Status.ERROR
            agent.save()

            return {
                "success": False,
                "execution": execution,
                "output": "",
                "error": str(e)
            }
