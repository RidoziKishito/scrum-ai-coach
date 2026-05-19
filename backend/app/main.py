import os
from fastapi import FastAPI, HTTPException, status, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import List
from dotenv import load_dotenv
from supabase import create_client

# Load biến môi trường
load_dotenv()

# Kết nối Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Import từ main
from app.goal_suggestion import (
    GoalSuggestRequest,
    GoalValidateRequest,
    GoalConfirmRequest,
    suggest_goals_by_ai,
    validate_goal_by_ai,
    save_goal_to_supabase
)

app = FastAPI()

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


# =========================
# POST API
# =========================
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
def get_level_from_rating(rating_level: int):
    level_mapping = {
        1: "Beginner",
        2: "Elementary",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }

    return level_mapping.get(rating_level, "Unknown")

@app.post("/api/skills/assess")
def assess_skills(data: SkillAssessmentRequest, current_user = Depends(verify_token)):
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
def get_skill_profile(user_id: str, current_user = Depends(verify_token)):
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