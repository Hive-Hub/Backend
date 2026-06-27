import logging
import httpx
from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def call(self, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        url = f"{api_base or 'https://api.openai.com/v1'}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key or ''}"
        }
        payload = {
            "model": model_name or "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        try:
            r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
            r.raise_for_status()
            data = r.json()
            return {
                "text": data["choices"][0]["message"]["content"],
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "success": True
            }
        except Exception as e:
            logger.error(f"OpenAIProvider execution failed: {str(e)}")
            return {
                "text": f"Error calling OpenAI: {str(e)}",
                "tokens_used": 0,
                "success": False
            }
