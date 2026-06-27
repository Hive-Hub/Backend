import logging
from google import genai
from google.genai import types
from django.conf import settings
from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def call(self, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        try:
            key = api_key or getattr(settings, 'GEMINI_API_KEY', None)
            if key:
                client = genai.Client(api_key=key)
            else:
                client = genai.Client()

            model = model_name or 'gemini-2.5-flash'
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            )
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config
            )
            return {
                "text": response.text,
                "tokens_used": response.usage_metadata.total_token_count if response.usage_metadata else 0,
                "success": True
            }
        except Exception as e:
            logger.error(f"GeminiProvider execution failed: {str(e)}")
            return {
                "text": f"Error calling Gemini: {str(e)}",
                "tokens_used": 0,
                "success": False
            }
