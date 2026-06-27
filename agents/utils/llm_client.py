import json
import logging
import httpx
from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def get_default_gemini_client():
    """
    Resolve and initialize GenAI client using GEMINI_API_KEY from settings.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return genai.Client()
    return genai.Client(api_key=api_key)


def call_llm(provider, model_name, api_key=None, system_prompt="", user_prompt="", api_base=None, temperature=0.7):
    """
    Unified LLM calling wrapper supporting multiple backends.
    - provider: 'gemini', 'openai', 'claude', 'ollama', 'lm_studio'
    - model_name: specific model to call (e.g. 'gemini-2.5-flash', 'gpt-4o')
    - api_key: auth token for the target provider
    - api_base: optional custom endpoint URL
    """
    provider = provider.lower().strip()
    
    # 1. GEMINI
    if provider == 'gemini':
        try:
            # Use provided API key or fall back to default client
            if api_key:
                client = genai.Client(api_key=api_key)
            else:
                client = get_default_gemini_client()
            
            model = model_name or 'gemini-2.5-flash'
            
            # Combine system and developer prompts into context or config
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
            logger.error(f"Gemini LLM Call failed: {str(e)}")
            return {
                "text": f"Error calling Gemini: {str(e)}",
                "tokens_used": 0,
                "success": False
            }

    # 2. OPENAI
    elif provider == 'openai':
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
            logger.error(f"OpenAI LLM Call failed: {str(e)}")
            return {
                "text": f"Error calling OpenAI: {str(e)}",
                "tokens_used": 0,
                "success": False
            }

    # 3. CLAUDE (Anthropic)
    elif provider == 'claude':
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
            logger.error(f"Claude LLM Call failed: {str(e)}")
            return {
                "text": f"Error calling Claude: {str(e)}",
                "tokens_used": 0,
                "success": False
            }

    # 4. OLLAMA
    elif provider == 'ollama':
        url = f"{api_base or 'http://localhost:11434'}/api/chat"
        headers = {"Content-Type": "application/json"}
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
            r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
            r.raise_for_status()
            data = r.json()
            return {
                "text": data["message"]["content"],
                "tokens_used": 0,
                "success": True
            }
        except Exception as e:
            logger.error(f"Ollama LLM Call failed: {str(e)}")
            return {
                "text": f"Error calling Ollama: {str(e)}",
                "tokens_used": 0,
                "success": False
            }

    # 5. LM STUDIO
    elif provider == 'lm_studio':
        url = f"{api_base or 'http://localhost:1234/v1'}/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model_name or "local-model",
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
            logger.error(f"LM Studio LLM Call failed: {str(e)}")
            return {
                "text": f"Error calling LM Studio: {str(e)}",
                "tokens_used": 0,
                "success": False
            }

    # UNKNOWN PROVIDER
    else:
        return {
            "text": f"Unsupported LLM provider: {provider}",
            "tokens_used": 0,
            "success": False
        }
