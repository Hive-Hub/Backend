import time
import logging
from django.utils import timezone
from ..models import Agent, AgentTask, AgentExecution, AgentLog, AgentWorkflow
from ..registry import AgentRegistry

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Workflow Service handles triggering tasks and orchestrating sequential execution of multi-agent workflows.
    """

    @staticmethod
    def run_task_in_workflow(task_id, workflow_id):
        """
        Executes a task against a given workflow, executing each step sequentially.
        """
        try:
            task = AgentTask.objects.get(id=task_id)
            workflow = AgentWorkflow.objects.get(id=workflow_id)
        except (AgentTask.DoesNotExist, AgentWorkflow.DoesNotExist) as e:
            return {"success": False, "error": str(e)}

        task.status = AgentTask.Status.IN_PROGRESS
        task.save()

        steps = workflow.steps
        if not steps:
            task.status = AgentTask.Status.FAILED
            task.save()
            return {"success": False, "error": "Workflow has no defined steps"}

        current_input = task.description
        execution_results = []
        
        # Ensure agents are loaded in DB
        AgentRegistry.setup_defaults()

        for step in steps:
            agent_slug = step.get("agent_slug")
            agent = Agent.objects.filter(slug=agent_slug, is_active=True).first()
            
            if not agent:
                error_msg = f"Agent '{agent_slug}' required for step {step.get('step_number')} is not found or inactive."
                task.status = AgentTask.Status.FAILED
                task.save()
                return {"success": False, "error": error_msg}

            try:
                from ..workflows import WorkflowEngine
                
                # Execute step using workflow engine
                result = WorkflowEngine.execute_step(task, agent, step, current_input)
                execution = result["execution"]

                if not result["success"]:
                    task.status = AgentTask.Status.FAILED
                    task.save()
                    return {
                        "success": False,
                        "error": f"Workflow failed at step {step.get('step_number')} ({agent.name}): {result['error']}",
                        "execution_results": execution_results
                    }

                # Build input for next step (accumulating outputs)
                current_input = (
                    f"--- Context from Step {step.get('step_number')} ({agent.name}) Output ---\n"
                    f"{result['output']}\n\n"
                    f"--- Previous Task Context ---\n"
                    f"{current_input}"
                )
                
                execution_results.append({
                    "step_number": step.get("step_number"),
                    "agent": agent.name,
                    "status": "SUCCESS",
                    "execution_id": execution.id
                })

            except Exception as e:
                logger.error(f"Error during step {step.get('step_number')} execution: {str(e)}")
                task.status = AgentTask.Status.FAILED
                task.save()
                
                return {
                    "success": False,
                    "error": f"Exception at step {step.get('step_number')}: {str(e)}",
                    "execution_results": execution_results
                }

        # Complete Task
        task.status = AgentTask.Status.COMPLETED
        task.completed_at = timezone.now()
        task.save()

        return {
            "success": True,
            "status": "COMPLETED",
            "execution_results": execution_results
        }
