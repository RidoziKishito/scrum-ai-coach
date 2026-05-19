import os
from fastapi import FastAPI
from pydantic import BaseModel
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

# =========================
# POST API
# =========================

@app.post("/api/skills/assess")
def assess_skills(data: SkillAssessmentRequest):
    rows = []

    # Chuẩn bị data insert
    for item in data.ratings:
        rows.append({
            "user_id": data.user_id,
            "skills_name": item.skill_name,
            "rating_level": item.rating_level
        })

    # Insert vào Supabase
    supabase.table("user_skills").insert(rows).execute()

    # Tính average score
    average_score = (
        sum(item.rating_level for item in data.ratings)
        / len(data.ratings)
    )

    # Xác định level
    if average_score <= 2:
        level = "Beginner"
    elif average_score <= 3.5:
        level = "Intermediate"
    else:
        level = "Advanced"

    return {
        "message": "Skill assessment saved successfully",
        "summary": {
            "user_id": data.user_id,
            "average_score": round(average_score, 2),
            "level": level,
            "ratings": rows
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

    average_score = (
        sum(item["rating_level"] for item in ratings)
        / len(ratings)
    )

    if average_score <= 2:
        level = "Beginner"
    elif average_score <= 3:
        level = "Intermediate"
    else:
        level = "Advanced"

    return {
        "message": "Skill profile fetched successfully",
        "summary": {
            "user_id": user_id,
            "average_score": round(average_score, 2),
            "level": level,
            "ratings": ratings
        }
    } # Đã thêm dấu ngoặc nhọn bị thiếu ở đây!


@app.get("/")
def read_root():
    return {
        "message": "Scrum AI Coach Backend is running"
    }


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