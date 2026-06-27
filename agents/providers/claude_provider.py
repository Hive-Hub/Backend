import logging
import httpx
from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class ClaudeProvider(BaseLLMProvider):
    def call(self, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        url = f"{api_base or 'https://api.anthropic.com/v1'}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key or "",
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": model_name or "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        try:
            r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
            r.raise_for_status()
            data = r.json()
            return {
                "text": data["content"][0]["text"],
                "tokens_used": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
                "success": True
            }
        except Exception as e:
            logger.error(f"ClaudeProvider execution failed: {str(e)}")
            return {
                "text": f"Error calling Claude: {str(e)}",
                "tokens_used": 0,
                "success": False
            }
