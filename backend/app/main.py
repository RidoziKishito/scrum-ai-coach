import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List
from dotenv import load_dotenv
from supabase import create_client

from app.goal_suggestion import (
    GoalSuggestRequest,
    GoalValidateRequest,
    GoalCustomRefineRequest,
    GoalConfirmRequest,
    suggest_goals_by_ai,
    validate_goal_by_ai,
    refine_custom_goal_by_ai,
    save_goal_to_supabase,
)

from app.action_plan import (
    ActionGenerateRequest,
    ActionStepStatusRequest,
    generate_action_steps_by_ai,
    save_action_steps_to_supabase,
    update_action_step_status
)

# =========================
# CONFIG
# =========================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================

class SkillRating(BaseModel):
    skill_name: str
    rating_level: int


class SkillAssessmentRequest(BaseModel):
    user_id: str
    ratings: List[SkillRating]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# =========================
# HELPER FUNCTIONS
# =========================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def get_level_from_rating(rating_level: int):
    level_mapping = {
        1: "Beginner",
        2: "Elementary",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert",
    }
    return level_mapping.get(rating_level, "Unknown")


# =========================
# ROOT API
# =========================

@app.get("/")
def read_root():
    return {
        "message": "Scrum AI Coach Backend is running"
    }


# =========================
# AUTHENTICATION API
# =========================

@app.post("/api/auth/register")
def register_user(data: RegisterRequest):
    try:
        email = str(data.email).strip()
        password = data.password.strip()

        if len(password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters"
            )

        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user = response.user

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Registration failed"
            )

        try:
            supabase.table("accounts").insert({
                "auth_uid": user.id,
                "email": email
            }).execute()

        except Exception as e:
            print("Insert accounts error:", e)

        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "email": email
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/api/auth/login")
def login(data: LoginRequest):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        return {
            "message": "Login successful",
            "user": {
                "id": result.user.id,
                "email": result.user.email
            },
            "access_token": result.session.access_token,
            "refresh_token": result.session.refresh_token,
            "token_type": "bearer"
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


@app.get("/api/auth/me")
def get_current_user(current_user=Depends(verify_token)):
    return {
        "message": "Token is valid",
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    }


# =========================
# SKILLS API
# =========================

@app.get("/api/skills")
def get_skills():
    result = (
        supabase
        .table("skills")
        .select("*")
        .execute()
    )

    return {
        "message": "Skills fetched successfully",
        "skills": result.data
    }


@app.post("/api/skills/assess")
def assess_skills(
    data: SkillAssessmentRequest,
    current_user=Depends(verify_token)
):
    rows = []
    summary_ratings = []

    for item in data.ratings:
        rows.append({
            "user_id": data.user_id,
            "skills_name": item.skill_name,
            "rating_level": item.rating_level
        })

        summary_ratings.append({
            "skill_name": item.skill_name,
            "rating_level": item.rating_level,
            "level": get_level_from_rating(item.rating_level)
        })

    supabase.table("user_skills").insert(rows).execute()

    return {
        "message": "Skill assessment saved successfully",
        "summary": {
            "user_id": data.user_id,
            "ratings": summary_ratings
        }
    }


@app.get("/api/skills/profile")
def get_skill_profile(
    user_id: str,
    current_user=Depends(verify_token)
):
    result = (
        supabase
        .table("user_skills")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    ratings = result.data

    if not ratings:
        return {
            "message": "No profile found",
            "summary": None
        }

    summary_ratings = []

    for item in ratings:
        summary_ratings.append({
            "skill_name": item["skills_name"],
            "rating_level": item["rating_level"],
            "level": get_level_from_rating(item["rating_level"])
        })

    return {
        "message": "Skill profile fetched successfully",
        "summary": {
            "user_id": user_id,
            "ratings": summary_ratings
        }
    }


# =========================
# GOALS API
# =========================

@app.post("/api/goals/suggest")
def suggest_goals(data: GoalSuggestRequest):
    goals = suggest_goals_by_ai(data.skills)

    return {
        "message": "Goal suggestions generated successfully",
        "user_id": data.user_id,
        "name": data.name,
        "goals": goals
    }


@app.post("/api/goals/validate")
def validate_goal(data: GoalValidateRequest):
    result = validate_goal_by_ai(
        goal_title=data.goal_title,
        goal_technique=data.goal_technique,
        skills=data.skills
    )

    return {
        "message": "Goal validation completed",
        "user_id": data.user_id,
        "name": data.name,
        "result": result
    }


@app.post("/api/goals/custom/refine")
def refine_custom_goal(data: GoalCustomRefineRequest):
    result = refine_custom_goal_by_ai(data)
    return result


@app.post("/api/goals/confirm")
def confirm_goal(data: GoalConfirmRequest):
    saved_goal = save_goal_to_supabase(data)

    return {
        "message": "Goal saved to Supabase successfully",
        "saved_goal": saved_goal
    }

# =========================
# ACTIONS API
# =========================

@app.post("/api/actions/generate")
def generate_action_plan(data: ActionGenerateRequest):
    steps = generate_action_steps_by_ai(data)

    saved_steps = save_action_steps_to_supabase(
        goal_id=data.goal_id,
        steps=steps
    )

    return {
        "message": "SMART action plan generated and saved successfully",
        "goal_id": data.goal_id,
        "steps": saved_steps
    }


@app.put("/api/actions/{step_id}/status")
def update_action_status(step_id: int, data: ActionStepStatusRequest):
    updated_step = update_action_step_status(
        step_id=step_id,
        is_completed=data.is_completed
    )

    return {
        "message": "Action step status updated successfully",
        "step": updated_step
    }