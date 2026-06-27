import os
import time
import logging
from django.conf import settings
from .base import BaseExecutor
from ..adapters import LLMAdapter
from ..models import AgentPrompt, AgentConfiguration, AgentContext, AgentMemory

logger = logging.getLogger(__name__)


class LLMExecutor(BaseExecutor):
    """
    Standard LLM Executor for agents. Retrieves prompt templates, loads configuration,
    and runs the unified call_llm helper.
    """

    def execute(self, task, input_data, context=None):
        start_time = time.time()
        agent = self.agent

        # 1. Retrieve configurations
        configs = {cfg.config_key: cfg.config_value for cfg in AgentConfiguration.objects.filter(agent=agent)}
        provider = configs.get('llm_provider', 'gemini')
        model_name = configs.get('llm_model', 'gemini-2.5-flash')
        api_key = configs.get('api_key', None)
        api_base = configs.get('api_base', None)
        try:
            temperature = float(configs.get('temperature', 0.7))
        except ValueError:
            temperature = 0.7

        # 2. Retrieve Prompt from DB (or fallback to disk)
        prompt_obj = AgentPrompt.objects.filter(agent=agent).first()
        if prompt_obj:
            system_prompt = prompt_obj.system_prompt
            developer_prompt = prompt_obj.developer_prompt
            user_template = prompt_obj.user_template
        else:
            # Fallback to local files if prompt not initialized in DB
            system_prompt = self._load_prompt_from_disk(agent.slug)
            developer_prompt = ""
            user_template = "Task: {task_title}\nDescription: {task_description}\nInput Context: {input_data}"

        # 3. Build context & memory
        memory_str = self._build_memory_context()
        context_str = self._build_shared_context_files()
        
        # Combine user prompt
        task_title = task.title if task else "Direct Execution"
        task_desc = task.description if task else ""
        formatted_user_prompt = user_template.format(
            task_title=task_title,
            task_description=task_desc,
            input_data=input_data
        ) if user_template else f"Task: {task_title}\nDescription: {task_desc}\nInput: {input_data}"

        # Build full system instruction
        full_system_prompt = (
            f"{system_prompt}\n\n"
            f"--- DEVELOPER INSTRUCTIONS ---\n"
            f"{developer_prompt}\n\n"
            f"--- SHARED ARCHITECTURE & RULES CONTEXT ---\n"
            f"{context_str}\n\n"
            f"--- AGENT MEMORY ---\n"
            f"{memory_str}"
        )

        # 4. Call LLM
        result = LLMAdapter.call(
            provider_name=provider,
            model_name=model_name,
            api_key=api_key,
            system_prompt=full_system_prompt,
            user_prompt=formatted_user_prompt,
            api_base=api_base,
            temperature=temperature
        )

        execution_time = time.time() - start_time
        return {
            "output": result.get("text", ""),
            "status": "SUCCESS" if result.get("success", False) else "FAILED",
            "tokens_used": result.get("tokens_used", 0),
            "execution_time": execution_time,
            "error_message": "" if result.get("success", False) else result.get("text", "")
        }

    def _load_prompt_from_disk(self, slug):
        """
        Helper to load prompt templates from local prompts/ directory if not found in database.
        """
        # Map agent slug to file names
        slug_to_file = {
            'project-manager': 'manager.md',
            'database-architect': 'database.md',
            'backend-api': 'backend.md',
            'storage': 'storage.md',
            'testing': 'testing.md',
            'review': 'review.md',
            'documentation': 'documentation.md',
            'authentication': 'authentication.md',
            'ai-learning': 'ai_learning.md',
        }
        filename = slug_to_file.get(slug, f"{slug.replace('-', '_')}.md")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, 'prompts', filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading prompt from disk {filepath}: {str(e)}")
        return f"You are the {slug} Agent."

    def _build_memory_context(self):
        memories = AgentMemory.objects.filter(agent=self.agent)
        if not memories.exists():
            return "No previous memories recorded."
        return "\n".join([f"- {mem.memory_key}: {mem.memory_value}" for mem in memories])

    def _build_shared_context_files(self):
        """
        Loads all generated shared context files from prompts/contexts/ directory.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        context_dir = os.path.join(base_dir, 'prompts', 'contexts')
        
        if not os.path.exists(context_dir):
            return ""
            
        context_contents = []
        for filename in os.listdir(context_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(context_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        context_contents.append(f"### Context File: {filename}\n{f.read()}")
                except Exception as e:
                    logger.error(f"Error reading context file {filename}: {str(e)}")
        return "\n\n".join(context_contents)
