import os
import uuid
from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
from dotenv import load_dotenv
from supabase import create_client
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load biến môi trường
load_dotenv()
security = HTTPBearer()

# Kết nối Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
DEV_REGISTERED_EMAILS = set()

# Import từ main
from .goal_suggestion import (
    GoalSuggestRequest,
    GoalValidateRequest,
    GoalConfirmRequest,
    suggest_goals_by_ai,
    validate_goal_by_ai,
    save_goal_to_supabase
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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

# Giữ cả RegisterRequest của bạn và LoginRequest của Triệu
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


def map_register_error(error: Exception) -> HTTPException:
    status_code = getattr(error, "status", None) or getattr(error, "status_code", None)
    raw_message = (
        getattr(error, "message", None)
        or getattr(error, "detail", None)
        or str(error)
    )
    message = raw_message.lower()

    if status_code == 429 or "rate limit" in message:
        return HTTPException(
            status_code=429,
            detail="Too many registration attempts. Please try again later."
        )

    if (
        status_code == 409
        or "already registered" in message
        or "already been registered" in message
        or "user already registered" in message
        or "already in use" in message
    ):
        return HTTPException(
            status_code=409,
            detail="Email already in use"
        )

    return HTTPException(
        status_code=500,
        detail=raw_message or "Registration failed"
    )


# =========================
# POST API
# =========================
def get_level_from_rating(rating_level: int):
    level_mapping = {
        1: "Beginner",
        2: "Elementary",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }

    return level_mapping.get(rating_level, "Unknown")


@app.post("/api/auth/register")
def register_user(data: RegisterRequest):
    try:
        email = str(data.email).strip()
        password = data.password.strip()

        if len(password) < 6:
            raise HTTPException(400, "Password must be at least 6 characters")

        if DEV_AUTH_BYPASS:
            if email.lower() in DEV_REGISTERED_EMAILS:
                raise HTTPException(409, "Email already in use")

            DEV_REGISTERED_EMAILS.add(email.lower())

            return {
                "message": "User registered successfully (dev bypass)",
                "user_id": f"dev-{uuid.uuid4()}",
                "email": email
            }

        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user = response.user

        if not user:
            raise HTTPException(400, "Registration failed")

        try:
            supabase.table("accounts").insert({
                "auth_uid": user.id,
                "email": email
            }).execute()
        except Exception as error:
            print("Insert accounts error:", error)

        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "email": email
        }

    except HTTPException:
        raise
    except Exception as error:
        raise map_register_error(error)

@app.post("/api/skills/assess")
def assess_skills(data: SkillAssessmentRequest):
    rows = []

    for item in data.ratings:
        level = get_level_from_rating(item.rating_level)

        rows.append({
            "user_id": data.user_id,
            "skills_name": item.skill_name,
            "rating_level": item.rating_level
        })

    supabase.table("user_skills").insert(rows).execute()

    summary = []

    for item in data.ratings:
        summary.append({
            "skill_name": item.skill_name,
            "rating_level": item.rating_level,
            "level": get_level_from_rating(item.rating_level)
        })

    return {
        "message": "Skill assessment saved successfully",
        "summary": {
            "user_id": data.user_id,
            "ratings": summary
        }
    }
# =========================
# GET API
# =========================

@app.get("/api/skills/profile")
def get_skill_profile(user_id: str):
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

    summary = []

    for item in ratings:
        summary.append({
            "skill_name": item["skills_name"],
            "rating_level": item["rating_level"],
            "level": get_level_from_rating(item["rating_level"])
        })

    return {
        "message": "Skill profile fetched successfully",
        "summary": {
            "user_id": user_id,
            "ratings": summary
        }
    }

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


@app.get("/")
def read_root():
    return {
        "message": "Scrum AI Coach Backend is running"
    }

def verify_token(authorization: str = Header(...)):
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )

    token = authorization.replace("Bearer ", "")

    try:
        user = supabase.auth.get_user(token)

        return user.user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


@app.get("/api/auth/me")
def get_current_user(current_user = Depends(verify_token)):
    return {
        "message": "Token is valid",
        "user": {
            "id": current_user.id,
            "email": current_user.email
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


@app.post("/api/goals/confirm")
def confirm_goal(data: GoalConfirmRequest):
    saved_goal = save_goal_to_supabase(data)

    return {
        "message": "Goal saved to Supabase successfully",
        "saved_goal": saved_goal
    }
