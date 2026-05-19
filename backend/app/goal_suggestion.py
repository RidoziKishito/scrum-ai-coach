import os
import json
import re
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


VALID_SKILLS = [
    "Programming Fundamentals",
    "Python",
    "Web Development (Frontend)",
    "Backend Development",
    "Database & SQL",
    "Version Control (Git)",
    "Testing & QA",
    "System Design & Architecture",
    "DevOps & Deployment",
    "AI & Machine Learning Basics"
]


RATING_LEVELS = {
    1: {
        "label": "Beginner",
        "description": "New to the topic or only heard about it"
    },
    2: {
        "label": "Elementary",
        "description": "Understands basic concepts but still needs guidance"
    },
    3: {
        "label": "Intermediate",
        "description": "Can complete some tasks independently"
    },
    4: {
        "label": "Advanced",
        "description": "Performs well and can mentor others"
    },
    5: {
        "label": "Expert",
        "description": "Has deep knowledge and strong mastery"
    }
}


class SkillInput(BaseModel):
    skills_name: str
    rating_level: int = Field(..., ge=1, le=5)


class GoalSuggestRequest(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    skills: Optional[List[SkillInput]] = None


class GoalValidateRequest(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    goal_title: str
    goal_technique: str
    skills: Optional[List[SkillInput]] = None


class GoalCustomRefineRequest(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    custom_goal: str
    goal_technique: Optional[str] = None
    skills: Optional[List[SkillInput]] = None


class GoalConfirmRequest(BaseModel):
    user_id: str
    name: str
    goal_title: str
    goal_technique: str
    feasibility: str
    validation_response: Optional[dict] = None


def get_rating_info(rating_level: int) -> dict:
    return RATING_LEVELS.get(
        rating_level,
        {
            "label": "Unknown",
            "description": "Invalid rating level"
        }
    )


def extract_json_from_text(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)

    if not match:
        raise ValueError("No JSON object or array found in AI response.")

    return json.loads(match.group(1))


def get_user_skills_from_supabase(user_id: Optional[str]) -> List[dict]:
    if not user_id:
        return []

    response = (
        supabase
        .table("user_skills")
        .select("skills_name, rating_level")
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return []

    skills = []

    for item in response.data:
        rating_level = int(item.get("rating_level"))
        rating_info = get_rating_info(rating_level)

        skills.append({
            "skills_name": item.get("skills_name"),
            "rating_level": rating_level,
            "rating_label": rating_info["label"],
            "rating_description": rating_info["description"]
        })

    return skills


def normalize_input_skills(skills: Optional[List[SkillInput]]) -> List[dict]:
    if not skills:
        return []

    normalized_skills = []

    for skill in skills:
        rating_info = get_rating_info(skill.rating_level)

        normalized_skills.append({
            "skills_name": skill.skills_name,
            "rating_level": skill.rating_level,
            "rating_label": rating_info["label"],
            "rating_description": rating_info["description"]
        })

    return normalized_skills


def get_skill_context(
    user_id: Optional[str],
    skills: Optional[List[SkillInput]]
) -> List[dict]:
    input_skills = normalize_input_skills(skills)

    if input_skills:
        return input_skills

    return get_user_skills_from_supabase(user_id)


def format_skills_for_prompt(skills: List[dict]) -> str:
    if not skills:
        return "No skill assessment data found."

    lines = []

    for skill in skills:
        lines.append(
            f"- {skill['skills_name']}: "
            f"{skill['rating_level']}/5 "
            f"({skill['rating_label']} - {skill['rating_description']})"
        )

    return "\n".join(lines)


def normalize_feasibility(value: str) -> str:
    cleaned_value = value.strip().upper()

    if cleaned_value in ["HIGH"]:
        return "HIGH"

    if cleaned_value in ["MEDIUM"]:
        return "MEDIUM"

    if cleaned_value in ["LOW"]:
        return "LOW"

    if cleaned_value in ["IMPOSSIBLE", "IMPOSIBLE"]:
        return "IMPOSSIBLE"

    return "MEDIUM"


def fallback_suggested_goals(user_skills: List[dict]) -> List[dict]:
    if not user_skills:
        return [
            {
                "goal_title": "Build a strong foundation in programming fundamentals",
                "goal_description": "Review variables, conditions, loops, functions, arrays, and basic problem solving.",
                "goal_technique": "Programming Fundamentals",
                "target_skill_level": "Elementary",
                "duration_weeks": 2,
                "weekly_commitment_hours": 4,
                "feasibility": "HIGH",
                "reason": "This is a realistic starting point for a beginner learner."
            },
            {
                "goal_title": "Practice Python basics through small exercises",
                "goal_description": "Complete simple Python exercises covering input, output, control flow, functions, and lists.",
                "goal_technique": "Python",
                "target_skill_level": "Elementary",
                "duration_weeks": 2,
                "weekly_commitment_hours": 4,
                "feasibility": "HIGH",
                "reason": "Python is suitable for building early programming confidence."
            },
            {
                "goal_title": "Learn basic Git workflow",
                "goal_description": "Practice clone, branch, commit, push, pull, and pull request workflow.",
                "goal_technique": "Version Control (Git)",
                "target_skill_level": "Elementary",
                "duration_weeks": 1,
                "weekly_commitment_hours": 3,
                "feasibility": "HIGH",
                "reason": "Basic Git workflow can be learned quickly with practice."
            },
            {
                "goal_title": "Create a small personal learning project",
                "goal_description": "Build a simple project that combines basic programming, Git, and documentation.",
                "goal_technique": "Programming Fundamentals",
                "target_skill_level": "Intermediate",
                "duration_weeks": 3,
                "weekly_commitment_hours": 5,
                "feasibility": "MEDIUM",
                "reason": "This is achievable after practicing basic concepts."
            }
        ]

    weakest_skills = sorted(
        user_skills,
        key=lambda skill: skill["rating_level"]
    )[:4]

    goals = []

    for skill in weakest_skills:
        skill_name = skill["skills_name"]

        goals.append({
            "goal_title": f"Improve practical ability in {skill_name}",
            "goal_description": f"Complete guided exercises and one small task related to {skill_name}.",
            "goal_technique": skill_name,
            "target_skill_level": "Intermediate",
            "duration_weeks": 2,
            "weekly_commitment_hours": 4,
            "feasibility": "HIGH" if skill["rating_level"] <= 2 else "MEDIUM",
            "reason": f"This goal focuses on improving a weaker skill area: {skill_name}."
        })

    while len(goals) < 4:
        goals.append({
            "goal_title": "Practice core software development skills",
            "goal_description": "Complete small tasks that improve coding, debugging, and project organization.",
            "goal_technique": "Programming Fundamentals",
            "target_skill_level": "Intermediate",
            "duration_weeks": 2,
            "weekly_commitment_hours": 4,
            "feasibility": "MEDIUM",
            "reason": "This goal supports general improvement across technical skills."
        })

    return goals[:4]


def sanitize_goal_object(goal: dict, allow_impossible: bool = False) -> dict:
    feasibility = normalize_feasibility(str(goal.get("feasibility", "MEDIUM")))

    if feasibility == "IMPOSSIBLE" and not allow_impossible:
        feasibility = "LOW"

    return {
        "goal_title": str(goal.get("goal_title", "")).strip(),
        "goal_description": str(goal.get("goal_description", "")).strip(),
        "goal_technique": str(goal.get("goal_technique", "")).strip(),
        "target_skill_level": str(goal.get("target_skill_level", "Intermediate")).strip(),
        "duration_weeks": int(goal.get("duration_weeks", 2)),
        "weekly_commitment_hours": int(goal.get("weekly_commitment_hours", 4)),
        "feasibility": feasibility,
        "reason": str(goal.get("reason", "")).strip()
    }


def suggest_goals_by_ai(data: GoalSuggestRequest) -> List[dict]:
    user_skills = get_skill_context(data.user_id, data.skills)
    skills_text = format_skills_for_prompt(user_skills)

    prompt = f"""
You are an AI learning coach for IT students.

The user's assessed skills are:

{skills_text}

Rating scale:
1 - Beginner: New to the topic or only heard about it
2 - Elementary: Understands basic concepts but still needs guidance
3 - Intermediate: Can complete some tasks independently
4 - Advanced: Performs well and can mentor others
5 - Expert: Has deep knowledge and strong mastery

Generate exactly 4 achievable learning goals.

Each goal must be clear, realistic, and useful for the user's current skill level.

Return only valid JSON.
Return exactly a JSON array with 4 objects.

Each object must have exactly these fields:
- goal_title
- goal_description
- goal_technique
- target_skill_level
- duration_weeks
- weekly_commitment_hours
- feasibility
- reason

Rules:
- feasibility must be one of: HIGH, MEDIUM, LOW.
- goal_technique should match one of these skill names when possible:
{VALID_SKILLS}
- duration_weeks must be a number.
- weekly_commitment_hours must be a number.
- Do not return markdown.
- Do not explain outside JSON.

Example:
[
  {{
    "goal_title": "Master Python functions and data structures",
    "goal_description": "Practice functions, lists, dictionaries, and simple problem solving tasks.",
    "goal_technique": "Python",
    "target_skill_level": "Intermediate",
    "duration_weeks": 3,
    "weekly_commitment_hours": 5,
    "feasibility": "HIGH",
    "reason": "The user has enough foundation to improve this skill with structured practice."
  }}
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
        goals = extract_json_from_text(content)

        if isinstance(goals, list) and len(goals) >= 4:
            return [
                sanitize_goal_object(goal, allow_impossible=False)
                for goal in goals[:4]
            ]

        return fallback_suggested_goals(user_skills)

    except Exception as e:
        print("Groq suggest error:", e)
        return fallback_suggested_goals(user_skills)


def validate_goal_by_ai(data: GoalValidateRequest) -> dict:
    user_skills = get_skill_context(data.user_id, data.skills)
    skills_text = format_skills_for_prompt(user_skills)

    prompt = f"""
You are an AI learning coach for IT students.

The user's assessed skills are:

{skills_text}

Selected goal:
{data.goal_title}

Goal technique:
{data.goal_technique}

Validate whether this selected goal is achievable for the user.

Return only valid JSON with this structure:
{{
  "goal_title": "selected goal",
  "goal_description": "short description of the selected goal",
  "goal_technique": "selected skill or technique",
  "target_skill_level": "target level",
  "duration_weeks": 2,
  "weekly_commitment_hours": 4,
  "feasibility": "HIGH | MEDIUM | LOW",
  "reason": "short reason",
  "alternative_goals": []
}}

Rules:
- feasibility must be only HIGH, MEDIUM, or LOW.
- If feasibility is LOW, alternative_goals must contain at least 2 easier goals.
- Each alternative goal must contain goal_title, goal_description, goal_technique, target_skill_level, duration_weeks, weekly_commitment_hours, feasibility, and reason.
- If feasibility is HIGH or MEDIUM, alternative_goals can be empty.
- Do not return markdown.
- Do not explain outside JSON.
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
        result = extract_json_from_text(content)

        result["feasibility"] = normalize_feasibility(
            str(result.get("feasibility", "MEDIUM"))
        )

        if result["feasibility"] == "LOW":
            alternatives = result.get("alternative_goals", [])

            if len(alternatives) < 2:
                result["alternative_goals"] = [
                    {
                        "goal_title": f"Start with a basic task in {data.goal_technique}",
                        "goal_description": "Complete one beginner-friendly guided task before moving to a larger goal.",
                        "goal_technique": data.goal_technique,
                        "target_skill_level": "Elementary",
                        "duration_weeks": 1,
                        "weekly_commitment_hours": 3,
                        "feasibility": "HIGH",
                        "reason": "This is a simpler starting point for the current skill level."
                    },
                    {
                        "goal_title": f"Complete a small practice exercise in {data.goal_technique}",
                        "goal_description": "Practice the core concept with a small and measurable exercise.",
                        "goal_technique": data.goal_technique,
                        "target_skill_level": "Elementary",
                        "duration_weeks": 1,
                        "weekly_commitment_hours": 3,
                        "feasibility": "HIGH",
                        "reason": "This reduces complexity and improves the chance of success."
                    }
                ]

        return result

    except Exception as e:
        print("Groq validate error:", e)

        return {
            "goal_title": data.goal_title,
            "goal_description": "The selected goal could not be fully validated because the AI service is unavailable.",
            "goal_technique": data.goal_technique,
            "target_skill_level": "Intermediate",
            "duration_weeks": 2,
            "weekly_commitment_hours": 4,
            "feasibility": "MEDIUM",
            "reason": "The AI validation service is unavailable, so this goal is marked as MEDIUM by default.",
            "alternative_goals": []
        }


def refine_custom_goal_by_ai(data: GoalCustomRefineRequest) -> dict:
    user_skills = get_skill_context(data.user_id, data.skills)
    skills_text = format_skills_for_prompt(user_skills)
    goal_technique = data.goal_technique or "General Software Development"

    prompt = f"""
You are an AI learning coach for IT students.

The user's assessed skills are:

{skills_text}

Custom goal written by the user:
{data.custom_goal}

Preferred goal technique:
{goal_technique}

Rewrite this custom goal into exactly one clear, structured, and measurable learning goal.

Return only valid JSON with this structure:
{{
  "goal_title": "rewritten clear goal",
  "goal_description": "specific explanation of what the user should achieve",
  "goal_technique": "related skill or technique",
  "target_skill_level": "target level",
  "duration_weeks": 2,
  "weekly_commitment_hours": 4,
  "feasibility": "HIGH | MEDIUM | LOW | IMPOSSIBLE",
  "reason": "short reason"
}}

Rules:
- Return exactly one JSON object.
- feasibility must be one of: HIGH, MEDIUM, LOW, IMPOSSIBLE.
- Use IMPOSSIBLE only if the goal is unrealistic for the user's current skills, time, or scope.
- Do not return markdown.
- Do not explain outside JSON.
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
        refined_goal = extract_json_from_text(content)
        refined_goal = sanitize_goal_object(refined_goal, allow_impossible=True)

        if refined_goal["feasibility"] == "IMPOSSIBLE":
            return {
                "message": "Custom goal refined successfully",
                "status": "REJECTED",
                "can_save": False,
                "notification": {
                    "type": "warning",
                    "title": "Goal is too difficult",
                    "message": "This goal is too hard to achieve right now. Please select one of the suggested goals or simplify your custom goal."
                },
                "goal": refined_goal
            }

        return {
            "message": "Custom goal refined successfully",
            "status": "ACCEPTED",
            "can_save": True,
            "notification": {
                "type": "success",
                "title": "Custom goal is ready",
                "message": "Your custom goal has been refined and is ready to review."
            },
            "goal": refined_goal
        }

    except Exception as e:
        print("Groq custom goal refine error:", e)

        fallback_goal = {
            "goal_title": data.custom_goal,
            "goal_description": "The custom goal could not be refined because the AI service is unavailable.",
            "goal_technique": goal_technique,
            "target_skill_level": "Intermediate",
            "duration_weeks": 2,
            "weekly_commitment_hours": 4,
            "feasibility": "MEDIUM",
            "reason": "The AI service is unavailable, so this goal is returned with a default feasibility level."
        }

        return {
            "message": "Custom goal refinement fallback returned",
            "status": "FALLBACK",
            "can_save": True,
            "notification": {
                "type": "info",
                "title": "AI refinement unavailable",
                "message": "The AI service is currently unavailable, so the original custom goal was returned with default planning information."
            },
            "goal": fallback_goal
        }


def normalize_goal_technique(goal_technique: str) -> str:
    return goal_technique.strip()


def save_goal_to_supabase(data: GoalConfirmRequest) -> dict:
    record = {
        "user_id": data.user_id,
        "name": data.name,
        "goal_title": data.goal_title,
        "goal_technique": normalize_goal_technique(data.goal_technique),
        "feasibility": data.feasibility,
        "validation_response": data.validation_response
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