from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .gemini_generator import generate_nutrition_tip_with_flash, generate_workout_gemini
from .models import User
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()
api_router = APIRouter(prefix="/api")


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "user_id": user.user_id,
        "username": user.username,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "original_plan": user.original_plan,
        "updated_plan": user.updated_plan,
        "nutrition_tip": user.nutrition_tip,
        "last_feedback": user.last_feedback,
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_page(
    request: Request,
    user_id: str = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = UserInput(
            user_id=user_id, username=username, age=age, weight=weight,
            goal=goal, intensity=intensity
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": f"Please check your input: {exc}"},
            status_code=422,
        )

    existing = db.scalar(select(User).where(User.user_id == payload.user_id))
    plan, tip = generate_workout_gemini(
        payload.username, payload.age, payload.weight, payload.goal, payload.intensity
    )

    if existing:
        existing.username = payload.username
        existing.age = payload.age
        existing.weight = payload.weight
        existing.goal = payload.goal
        existing.intensity = payload.intensity
        existing.original_plan = plan
        existing.updated_plan = None
        existing.nutrition_tip = tip
        existing.last_feedback = None
        user = existing
    else:
        user = User(
            user_id=payload.user_id, username=payload.username, age=payload.age,
            weight=payload.weight, goal=payload.goal, intensity=payload.intensity,
            original_plan=plan, nutrition_tip=tip
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"user": user, "plan": user.original_plan, "message": "Plan generated successfully."},
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_page(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.user_id == user_id))
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "User ID was not found. Generate a plan first."},
            status_code=404,
        )

    revised, message = update_workout_plan(
        user.username, user.age, user.goal, user.intensity,
        user.updated_plan or user.original_plan, feedback.strip()
    )
    user.updated_plan = revised
    user.last_feedback = feedback.strip()
    user.nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"user": user, "plan": user.updated_plan, "message": message},
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, key: str = "", db: Session = Depends(get_db)):
    settings = get_settings()
    if key != settings.admin_key:
        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={"users": [], "protected": True},
            status_code=401,
        )
    users = list(db.scalars(select(User).order_by(User.id.desc())).all())
    return templates.TemplateResponse(
        request=request, name="all_users.html",
        context={"users": users, "protected": False}
    )


@api_router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "demo_mode": settings.demo_mode,
    }


@api_router.post("/generate")
def api_generate(payload: UserInput, db: Session = Depends(get_db)):
    plan, tip = generate_workout_gemini(
        payload.username, payload.age, payload.weight, payload.goal, payload.intensity
    )
    user = db.scalar(select(User).where(User.user_id == payload.user_id))

    if user:
        user.username = payload.username
        user.age = payload.age
        user.weight = payload.weight
        user.goal = payload.goal
        user.intensity = payload.intensity
        user.original_plan = plan
        user.updated_plan = None
        user.nutrition_tip = tip
        user.last_feedback = None
    else:
        user = User(
            user_id=payload.user_id, username=payload.username, age=payload.age,
            weight=payload.weight, goal=payload.goal, intensity=payload.intensity,
            original_plan=plan, nutrition_tip=tip
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    settings = get_settings()
    ai_mode = "gemini" if not settings.demo_mode and settings.gemini_api_key else "demo"

    return {"user": serialize_user(user), "plan": plan, "nutrition_tip": tip, "ai_mode": ai_mode}


@api_router.post("/feedback")
def api_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User ID not found.")

    revised, message = update_workout_plan(
        user.username, user.age, user.goal, user.intensity,
        user.updated_plan or user.original_plan, payload.feedback.strip()
    )
    user.updated_plan = revised
    user.last_feedback = payload.feedback.strip()
    user.nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    db.commit()
    db.refresh(user)

    return {"user": serialize_user(user), "message": message}


@api_router.get("/users")
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id.desc())).all()
    return {"users": [serialize_user(u) for u in users]}
