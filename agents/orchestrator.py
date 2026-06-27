import json
import logging
from .models import Agent, AgentWorkflow, WorkflowStep
from .workflow_engine import WorkflowEngine
from .adapters import LLMAdapter

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrator Layer: Receives user queries, decomposes them into workflows,
    registers the sequence tasks in the database, and starts the Workflow Engine.
    """
    def __init__(self):
        self.agent = Agent.objects.filter(slug='orchestrator').first()
        if not self.agent:
            self.agent = Agent.objects.filter(agent_type=Agent.AgentType.ORCHESTRATOR).first()

    def handle_request(self, user_request: str) -> dict:
        logger.info(f"Orchestrator received request: {user_request}")
        
        configs = {}
        if self.agent:
            configs = {cfg.config_key: cfg.config_value for cfg in self.agent.configurations.all()}
            
        provider = configs.get('llm_provider', 'gemini')
        model = configs.get('llm_model', 'gemini-2.5-flash')
        api_key = configs.get('api_key', None)
        
        system_instruction = (
            "You are the QISHub Orchestrator Agent.\n"
            "Your task is to analyze user queries and break them down into dynamic workflow steps.\n"
            "Respond ONLY in valid JSON format with the following schema:\n"
            "{\n"
            "  \"workflow_name\": \"Name of the workflow\",\n"
            "  \"description\": \"Description of what the workflow is accomplishing\",\n"
            "  \"steps\": [\n"
            "    {\n"
            "      \"step_number\": 1,\n"
            "      \"name\": \"Name/purpose of this step\",\n"
            "      \"agent_type\": \"One of: DATABASE_ARCHITECT, BACKEND_API, AI_LEARNING, STORAGE, TESTING, DOCUMENTATION, REVIEW\",\n"
            "      \"depends_on\": []\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        user_prompt = f"User request: {user_request}"
        
        res = LLMAdapter.call(
            provider_name=provider,
            model_name=model,
            api_key=api_key,
            system_prompt=system_instruction,
            user_prompt=user_prompt,
            temperature=0.2
        )
        
        text = res.get("text", "")
        try:
            clean_text = text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            workflow_data = json.loads(clean_text)
        except Exception as e:
            logger.warning(f"Failed to parse LLM intent analysis: {str(e)}. Creating fallback workflow.")
            workflow_data = {
                "workflow_name": "General Request Execution",
                "description": "Fulfills the user request using the Project Manager Agent",
                "steps": [
                    {
                        "step_number": 1,
                        "name": "Analyze and Execute Request",
                        "agent_type": "PROJECT_MANAGER",
                        "depends_on": []
                    }
                ]
            }

        wf = AgentWorkflow.objects.create(
            name=workflow_data.get("workflow_name", "Dynamic OS Workflow"),
            description=workflow_data.get("description", ""),
            active=True
        )
        
        for step_data in workflow_data.get("steps", []):
            agent_type = step_data.get("agent_type", "PROJECT_MANAGER")
            
            target_agent = Agent.objects.filter(agent_type=agent_type, is_active=True).first()
            if not target_agent:
                target_agent = Agent.objects.filter(agent_type=Agent.AgentType.PROJECT_MANAGER).first()
                
            WorkflowStep.objects.create(
                workflow=wf,
                step_number=step_data.get("step_number", 1),
                name=step_data.get("name", "Task Step"),
                agent=target_agent,
                depends_on_steps=step_data.get("depends_on", []),
                status=WorkflowStep.StepStatus.PENDING
            )

        engine = WorkflowEngine(wf.id)
        status_res = engine.execute(user_request)
        
        results_list = []
        for step in wf.steps_list.all().order_by('step_number'):
            from .models import AgentTask
            task_obj = AgentTask.objects.filter(assigned_agent=step.agent, description=step.name).order_by('-id').first()
            output = ""
            if task_obj and hasattr(task_obj, 'result'):
                output = task_obj.result.output_data
                
            results_list.append({
                "step": step.step_number,
                "name": step.name,
                "agent": step.agent.name if step.agent else "None",
                "status": step.status,
                "output": output
            })

        return {
            "workflow_id": wf.id,
            "status": status_res,
            "results": results_list
        }
