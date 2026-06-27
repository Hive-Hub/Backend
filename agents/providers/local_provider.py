import logging
import httpx
from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class LocalProvider(BaseLLMProvider):
    def call(self, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7) -> dict:
        # Determine if it's Ollama or LM Studio by parsing the api_base or checking provider style
        # Default fallback is Ollama if port 11434, else LM Studio / OpenAI compatible format
        base_url = api_base or "http://localhost:11434"
        
        if "11434" in base_url or "ollama" in base_url:
            # Ollama API format
            url = f"{base_url}/api/chat"
            payload = {
                "model": model_name or "llama3",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "options": {"temperature": temperature},
                "stream": False
            }
            try:
                r = httpx.post(url, json=payload, timeout=60.0)
                r.raise_for_status()
                data = r.json()
                return {
                    "text": data["message"]["content"],
                    "tokens_used": 0,
                    "success": True
                }
            except Exception as e:
                logger.error(f"Ollama execution failed: {str(e)}")
                return {
                    "text": f"Error calling Ollama: {str(e)}",
                    "tokens_used": 0,
                    "success": False
                }
        else:
            # LM Studio / Local OpenAI compatible
            url = f"{base_url}/chat/completions"
            payload = {
                "model": model_name or "local-model",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
            }
            try:
                r = httpx.post(url, json=payload, timeout=60.0)
                r.raise_for_status()
                data = r.json()
                return {
                    "text": data["choices"][0]["message"]["content"],
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "success": True
                }
            except Exception as e:
                logger.error(f"LM Studio execution failed: {str(e)}")
                return {
                    "text": f"Error calling LM Studio: {str(e)}",
                    "tokens_used": 0,
                    "success": False
                }
