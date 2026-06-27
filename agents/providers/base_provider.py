from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for LLM Provider implementations.
    """
    @abstractmethod
    def call(self, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        """
        Executes raw LLM requests.
        Returns:
            dict: {
                "text": str,
                "tokens_used": int,
                "success": bool
            }
        """
        pass
