import json
import re
from typing import Any

from .config import get_settings

DEMO_DAYS = [
    ("Day 1", "Full-body mobility", ["Easy warm-up", "Bodyweight squat", "Wall push-up", "Gentle cool-down"]),
    ("Day 2", "Light cardio", ["Brisk walk", "Easy marching", "Mobility stretches", "Breathing cool-down"]),
    ("Day 3", "Upper-body basics", ["Shoulder circles", "Wall push-up", "Band or towel row", "Gentle stretches"]),
    ("Day 4", "Recovery & flexibility", ["Easy walk", "Gentle stretching", "Mobility flow", "Relaxed breathing"]),
    ("Day 5", "Lower-body basics", ["Warm-up walk", "Bodyweight squat to chair", "Calf raises", "Cool-down"]),
    ("Day 6", "Fun movement", ["Walk, cycle, dance, or another comfortable activity", "Light mobility", "Cool-down"]),
    ("Day 7", "Rest & reflection", ["Rest", "Optional gentle stretching", "Reflect on energy and comfort"]),
]


def demo_workout(username: str, goal: str, intensity: str) -> str:
    lines = [
        f"Personalized 7-Day Wellness Plan for {username}",
        f"Goal: {goal.title()} | Intensity: {intensity.title()}",
        "",
        "Use comfortable effort, stop if something hurts, and adjust activity to your ability.",
        "",
    ]
    for day, focus, exercises in DEMO_DAYS:
        lines.append(day)
        lines.append(f"Focus: {focus}")
        for item in exercises:
            lines.append(f"- {item}")
        lines.append("Suggested effort: comfortable and controlled.")
        lines.append("")
    return "\n".join(lines)


def demo_tip(goal: str) -> str:
    tips = {
        "general wellness": "Build regular meals around a variety of foods, stay hydrated, and include enjoyable movement and adequate rest.",
        "strength": "Include a variety of protein-containing foods in regular meals and allow recovery between challenging sessions.",
        "flexibility": "Pair gentle mobility with regular meals, hydration, and enough rest. Never force a stretch into pain.",
        "endurance": "Increase activity gradually, stay hydrated, eat regular balanced meals, and include recovery days.",
    }
    return tips.get(goal, tips["general wellness"])


def _extract_json(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _gemini_text(prompt: str, model: str) -> str:
    settings = get_settings()
    if settings.demo_mode or not settings.gemini_api_key:
        raise RuntimeError("Gemini is disabled; using demo mode.")

    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()


def generate_workout_gemini(
    username: str, age: int, weight: float, goal: str, intensity: str
) -> tuple[str, str]:
    settings = get_settings()
    prompt = f'''
Create a safe, age-appropriate 7-day general wellness/activity plan.

User name: {username}
Age: {age}
Weight kg: {weight}
Goal: {goal}
Preferred intensity: {intensity}

Return JSON with exactly two fields:
{{
  "workout_plan": "plain text plan covering Day 1 through Day 7",
  "nutrition_tip": "one concise practical nutrition or recovery tip"
}}

Rules:
- Do not diagnose or prescribe treatment.
- Do not recommend extreme dieting or rapid weight-loss targets.
- Do not use body-image judgments.
- Include rest/recovery.
- Do not require gym equipment.
- Use comfortable, gradual activity.
'''
    try:
        raw = _gemini_text(prompt, settings.gemini_workout_model)
        data = _extract_json(raw)
        if data and data.get("workout_plan") and data.get("nutrition_tip"):
            return str(data["workout_plan"]), str(data["nutrition_tip"])
    except Exception:
        pass

    return demo_workout(username, goal, intensity), demo_tip(goal)


def generate_nutrition_tip_with_flash(goal: str) -> str:
    settings = get_settings()
    prompt = f'''
Give one concise, practical nutrition/recovery tip for a person whose wellness goal is "{goal}".
Avoid calorie restriction, extreme dieting, supplements, medical claims, and body-image language.
Return plain text only.
'''
    try:
        return _gemini_text(prompt, settings.gemini_tip_model)
    except Exception:
        return demo_tip(goal)
