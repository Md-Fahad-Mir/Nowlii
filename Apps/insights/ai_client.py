"""
AI client for generating weekly reflections.
Auto-detects provider from settings (same pattern as subtasks app).
Priority: ANTHROPIC → OPENAI → GOOGLE
"""
import json
import anthropic
import openai
import google.generativeai as genai
from django.conf import settings


# ─────────────────────────────────────────────
#  Prompt
# ─────────────────────────────────────────────

REFLECTION_PROMPT = """
You are a personal productivity coach analyzing a user's quest/task completion data.

Based on the weekly analytics below, generate exactly 3 short, insightful reflection sentences.
Rules:
- Each sentence must be specific to the data provided (mention day names, percentages, zone types).
- Tone: encouraging, honest, motivating.
- Keep each sentence under 20 words.
- Do NOT use generic filler like "Great job!" or "Keep it up!".
- Return ONLY a clean JSON array of 3 strings. No explanation, no markdown, no code fences.

Weekly data:
{weekly_data}

Output format:
["Reflection 1", "Reflection 2", "Reflection 3"]
"""


def _build_prompt(weekly_data: dict) -> str:
    return REFLECTION_PROMPT.format(weekly_data=json.dumps(weekly_data, indent=2))


def _parse(raw: str) -> list:
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ─────────────────────────────────────────────
#  Provider auto-detection
# ─────────────────────────────────────────────

def get_active_provider() -> str:
    if getattr(settings, "ANTHROPIC_API_KEY", None):
        return "claude"
    if getattr(settings, "OPENAI_API_KEY", None):
        return "chatgpt"
    if getattr(settings, "GOOGLE_AI_API_KEY", None):
        return "gemini"
    raise EnvironmentError(
        "No AI provider API key found. "
        "Set one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_AI_API_KEY in your .env"
    )


# ─────────────────────────────────────────────
#  Provider callers
# ─────────────────────────────────────────────

def _call_claude(prompt: str) -> list:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(response.content[0].text)


def _call_chatgpt(prompt: str) -> list:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(response.choices[0].message.content)


def _call_gemini(prompt: str) -> list:
    genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt)
    return _parse(response.text)


_PROVIDERS = {
    "claude":  _call_claude,
    "chatgpt": _call_chatgpt,
    "gemini":  _call_gemini,
}


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def generate_weekly_reflections(weekly_data: dict) -> list[str]:
    """
    Calls the auto-detected AI provider and returns
    a list of 3 reflection strings.
    """
    provider = get_active_provider()
    prompt   = _build_prompt(weekly_data)
    return _PROVIDERS[provider](prompt)
