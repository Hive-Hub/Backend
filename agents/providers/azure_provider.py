import logging
import httpx
from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class AzureProvider(BaseLLMProvider):
    def call(self, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        url = api_base or ""
        if not url:
            return {
                "text": "Error: Azure OpenAI requires a valid api_base endpoint URL.",
                "tokens_used": 0,
                "success": False
            }
        
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key or ""
        }
        payload = {
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
            logger.error(f"Azure OpenAI Provider execution failed: {str(e)}")
            return {
                "text": f"Error calling Azure OpenAI: {str(e)}",
                "tokens_used": 0,
                "success": False
            }
        
