import os
import json
import re
from config.settings import GEMINI_API_KEY, PRIMARY_MODEL, FALLBACK_MODEL

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def get_api_key():
    """Retrieves API key from environment, checking for dummy/placeholder keys."""
    key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    if not key or key in ["your_gemini_api_key_here", "your_api_key_here", ""]:
        return None
    return key

def is_api_key_configured():
    return bool(get_api_key())

def clean_json_response(raw_text: str) -> dict:
    try:
        return json.loads(raw_text)
    except Exception:
        pass
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass
    start_brace = raw_text.find('{')
    end_brace = raw_text.rfind('}')
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        try:
            return json.loads(raw_text[start_brace:end_brace+1])
        except Exception:
            pass
    return {}

def call_gemini(prompt: str, system_instruction: str = "", model_name: str = None, temperature: float = 0.4) -> str:
    api_key = get_api_key()
    if not api_key or not GENAI_AVAILABLE:
        return "[FALLBACK_MODE]"
    
    try:
        genai.configure(api_key=api_key)
        models = [model_name] if model_name else [PRIMARY_MODEL, FALLBACK_MODEL, "gemini-1.5-flash"]
        for m in models:
            if not m: continue
            try:
                model = genai.GenerativeModel(
                    model_name=m,
                    system_instruction=system_instruction if system_instruction else None,
                    generation_config={"temperature": temperature}
                )
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    return resp.text
            except Exception:
                continue
    except Exception:
        pass
    return "[FALLBACK_MODE]"

def call_gemini_json(prompt: str, system_instruction: str = "", model_name: str = None) -> dict:
    strict_instruction = (system_instruction + "\n" if system_instruction else "") + (
        "CRITICAL: Output ONLY valid JSON without conversational wrapper."
    )
    raw = call_gemini(prompt, system_instruction=strict_instruction, model_name=model_name, temperature=0.2)
    if raw == "[FALLBACK_MODE]" or not raw or raw.startswith("[GEMINI_ERROR]"):
        return {"_fallback": True}
    parsed = clean_json_response(raw)
    if not parsed:
        return {"_fallback": True}
    return parsed
