import logging
from ..providers import GeminiProvider, OpenAIProvider, ClaudeProvider, LocalProvider, AzureProvider

logger = logging.getLogger(__name__)

class LLMAdapter:
    """
    Adapter pattern to unify LLM requests. Dynamically resolves the provider based on configuration.
    """
    @staticmethod
    def call(provider_name, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        p_name = (provider_name or 'gemini').lower().strip()
        
        if p_name == 'gemini':
            provider = GeminiProvider()
        elif p_name == 'openai':
            provider = OpenAIProvider()
        elif p_name == 'claude':
            provider = ClaudeProvider()
        elif p_name in ['ollama', 'lm_studio', 'local']:
            provider = LocalProvider()
        elif p_name == 'azure':
            provider = AzureProvider()
        else:
            logger.warning(f"Unknown provider '{provider_name}'. Defaulting to Gemini.")
            provider = GeminiProvider()
            
        return provider.call(
            model_name=model_name,
            api_key=api_key,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_base=api_base,
            temperature=temperature
        )
