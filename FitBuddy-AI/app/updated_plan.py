from .config import get_settings
from .gemini_generator import _gemini_text, demo_workout


def update_workout_plan(
    username: str,
    age: int,
    goal: str,
    intensity: str,
    original_plan: str,
    feedback: str,
) -> tuple[str, str]:
    settings = get_settings()
    prompt = f'''
Revise this 7-day wellness/activity plan using the user's feedback.

User: {username}
Age: {age}
Goal: {goal}
Preferred intensity: {intensity}

Original plan:
{original_plan}

Feedback:
{feedback}

Return plain text with Day 1 through Day 7.
Keep activity age-appropriate, comfortable, gradual, and non-medical.
Do not add calorie targets, rapid weight-loss advice, dangerous challenges, or body-image judgments.
Preserve useful parts of the original plan and apply the feedback clearly.
'''
    try:
        revised = _gemini_text(prompt, settings.gemini_workout_model)
        return revised, "AI revision applied."
    except Exception:
        revised = (
            f"Updated 7-Day Wellness Plan for {username}\n"
            f"Goal: {goal.title()} | Intensity: {intensity.title()}\n\n"
            f"Feedback considered: {feedback}\n\n"
            f"{demo_workout(username, goal, intensity)}"
        )
        return revised, "Local demo revision applied."
