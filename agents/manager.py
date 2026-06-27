import logging
from .models import Agent, AgentTask, TaskResult
from .executors.llm_executor import LLMExecutor

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    Project Manager Layer: Coordinates specific worker executions and aggregates results.
    Workers communicate strictly with Project Manager, never directly with each other.
    """
    def __init__(self):
        self.agent = Agent.objects.filter(slug='project-manager').first()
        if not self.agent:
            self.agent = Agent.objects.filter(agent_type=Agent.AgentType.PROJECT_MANAGER).first()

    def run_worker_task(self, worker_agent_slug: str, task_title: str, task_description: str, input_data: str) -> dict:
        worker = Agent.objects.filter(slug=worker_agent_slug).first()
        if not worker:
            return {
                "status": "FAILED",
                "error_message": f"Worker agent '{worker_agent_slug}' not found."
            }

        logger.info(f"PM assigning task '{task_title}' to worker '{worker.name}'")

        task = AgentTask.objects.create(
            title=task_title,
            description=task_description,
            status=AgentTask.Status.IN_PROGRESS,
            assigned_agent=worker
        )

        executor = LLMExecutor(agent=worker)
        res = executor.execute(task, input_data)

        status_res = res.get("status", "FAILED")
        output = res.get("output", "")
        error_msg = res.get("error_message", "")

        if status_res == "SUCCESS":
            task.status = AgentTask.Status.COMPLETED
            task.save()
            TaskResult.objects.create(
                task=task,
                output_data=output,
                execution_time=res.get("execution_time", 0.0),
                tokens_used=res.get("tokens_used", 0),
                status="SUCCESS"
            )
        else:
            task.status = AgentTask.Status.FAILED
            task.save()
            TaskResult.objects.create(
                task=task,
                output_data=error_msg,
                execution_time=res.get("execution_time", 0.0),
                tokens_used=res.get("tokens_used", 0),
                status="FAILED",
                error_message=error_msg
            )

        return {
            "task_id": task.id,
            "status": status_res,
            "output": output,
            "error_message": error_msg
        }

    def aggregate_results(self, task_outputs: list) -> str:
        """
        PM aggregates inputs and writes summary of execution results.
        """
        logger.info("PM aggregating task outputs")
        if not self.agent:
            return "\n\n".join(task_outputs)
            
        configs = {cfg.config_key: cfg.config_value for cfg in self.agent.configurations.all()}
        provider = configs.get('llm_provider', 'gemini')
        model = configs.get('llm_model', 'gemini-2.5-flash')
        api_key = configs.get('api_key', None)

        system_instruction = (
            "You are the QISHub Project Manager Agent.\n"
            "Analyze the given execution results from various specialist agents, merge them into a single, cohesive, enterprise-ready final report, and describe the implementation details clearly."
        )
        
        user_prompt = f"Outputs to aggregate:\n" + "\n---\n".join([str(o) for o in task_outputs])
        from .adapters import LLMAdapter
        res = LLMAdapter.call(
            provider_name=provider,
            model_name=model,
            api_key=api_key,
            system_prompt=system_instruction,
            user_prompt=user_prompt,
            temperature=0.3
        )
        return res.get("text", "Aggregation completed.")
