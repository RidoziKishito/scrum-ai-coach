import os
import json
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from supabase import create_client, Client


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY. Please check backend/.env file.")

if not SUPABASE_URL:
    raise ValueError("Missing SUPABASE_URL. Please check backend/.env file.")

if not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_KEY. Please check backend/.env file.")


groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class UserSkillProfile(BaseModel):
    programming_tec: int = Field(..., ge=1, le=5)
    oop_score: int = Field(..., ge=1, le=5)
    sql_score: int = Field(..., ge=1, le=5)


class GoalSuggestRequest(BaseModel):
    user_id: str
    name: str
    skills: UserSkillProfile


class GoalValidateRequest(BaseModel):
    user_id: str
    name: str
    goal_title: str
    goal_technique: str
    skills: UserSkillProfile


class GoalConfirmRequest(BaseModel):
    user_id: str
    name: str
    goal_title: str
    goal_technique: str
    feasibility: str
    programming_tec: int = Field(..., ge=1, le=5)
    oop_score: int = Field(..., ge=1, le=5)
    sql_score: int = Field(..., ge=1, le=5)


def fallback_goals(skills: UserSkillProfile) -> List[dict]:
    weakest_score = min(
        skills.programming_tec,
        skills.oop_score,
        skills.sql_score
    )

    if weakest_score == skills.programming_tec:
        return [
            {
                "goal_title": "Practice array, string, and function exercises",
                "goal_technique": "KTLT"
            },
            {
                "goal_title": "Solve 5 basic programming technique problems",
                "goal_technique": "KTLT"
            },
            {
                "goal_title": "Refactor simple code into reusable functions",
                "goal_technique": "KTLT"
            }
        ]

    if weakest_score == skills.oop_score:
        return [
            {
                "goal_title": "Build a small OOP management application",
                "goal_technique": "OOP"
            },
            {
                "goal_title": "Practice encapsulation, inheritance, and polymorphism",
                "goal_technique": "OOP"
            },
            {
                "goal_title": "Design classes for a real-world system",
                "goal_technique": "OOP"
            }
        ]

    return [
        {
            "goal_title": "Practice SQL SELECT, JOIN, GROUP BY, and subqueries",
            "goal_technique": "Database"
        },
        {
            "goal_title": "Design an ERD for a simple management system",
            "goal_technique": "Database"
        },
        {
            "goal_title": "Normalize a database schema to 3NF",
            "goal_technique": "Database"
        }
    ]


def suggest_goals_by_ai(skills: UserSkillProfile) -> List[dict]:
    prompt = f"""
You are an AI learning coach for IT students.

The user's skill scores are:
- Programming Techniques / KTLT: {skills.programming_tec}/5
- OOP: {skills.oop_score}/5
- Database / SQL: {skills.sql_score}/5

Suggest exactly 3 achievable learning goals.

Rules:
- Return only valid JSON.
- Return exactly a JSON array with 3 objects.
- Each object must have:
  - goal_title
  - goal_technique
- goal_technique must be one of: KTLT, OOP, Database.
- Goals must be realistic and useful for the user's current skill level.
- Do not return markdown.

Example:
[
  {{"goal_title": "Build a small OOP management application", "goal_technique": "OOP"}},
  {{"goal_title": "Practice SQL JOIN queries", "goal_technique": "Database"}},
  {{"goal_title": "Solve array and string exercises", "goal_technique": "KTLT"}}
]
"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI learning coach. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content
        goals = json.loads(content)

        if isinstance(goals, list) and len(goals) >= 3:
            return goals[:3]

        return fallback_goals(skills)

    except Exception as e:
        print("Groq suggest error:", e)
        return fallback_goals(skills)


def validate_goal_by_ai(goal_title: str, goal_technique: str, skills: UserSkillProfile) -> dict:
    prompt = f"""
You are an AI learning coach for IT students.

User skills:
- Programming Techniques / KTLT: {skills.programming_tec}/5
- OOP: {skills.oop_score}/5
- Database / SQL: {skills.sql_score}/5

Selected goal:
{goal_title}

Goal technique:
{goal_technique}

Validate whether this goal is achievable.

Return only valid JSON with this structure:
{{
  "goal_title": "selected goal",
  "goal_technique": "KTLT | OOP | Database",
  "feasibility": "High | Medium | Low",
  "reason": "short reason",
  "alternative_goals": []
}}

Rules:
- feasibility must be only High, Medium, or Low.
- If feasibility is Low, alternative_goals must contain at least 2 easier goals.
- Each alternative goal must be an object with goal_title and goal_technique.
- If feasibility is High or Medium, alternative_goals can be empty.
"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI learning coach. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        if result.get("feasibility") == "Low":
            alternatives = result.get("alternative_goals", [])
            if len(alternatives) < 2:
                result["alternative_goals"] = [
                    {
                        "goal_title": "Start with a smaller beginner-level task",
                        "goal_technique": goal_technique
                    },
                    {
                        "goal_title": "Complete one guided practice exercise first",
                        "goal_technique": goal_technique
                    }
                ]

        return result

    except Exception as e:
        print("Groq validate error:", e)

        return {
            "goal_title": goal_title,
            "goal_technique": goal_technique,
            "feasibility": "Medium",
            "reason": "The AI validation service is unavailable, so this goal is marked as Medium by default.",
            "alternative_goals": []
        }

def normalize_goal_technique(goal_technique: str) -> str:
    value = goal_technique.strip().lower()

    if value in ["ktlt", "programming technique", "programming techniques"]:
        return "Programming Technique"

    if value in ["oop", "object-oriented programming", "object oriented programming"]:
        return "Object-Oriented Programming"

    if value in ["database", "sql", "database system and sql"]:
        return "Database System and SQL"

    return goal_technique

def save_goal_to_supabase(data: GoalConfirmRequest) -> dict:
    record = {
        "user_id": data.user_id,
        "name": data.name,
        "goal_title": data.goal_title,
        "goal_technique": normalize_goal_technique(data.goal_technique),
        "feasibility": data.feasibility,
        "programming_technique_score": data.programming_tec,
        "oop_score": data.oop_score,
        "sql_score": data.sql_score
    }

    response = (
        supabase
        .table("user_goals")
        .insert(record)
        .execute()
    )

    if not response.data:
        raise Exception("Failed to save goal to Supabase")

    return response.data[0]