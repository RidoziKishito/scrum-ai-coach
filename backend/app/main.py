from fastapi import FastAPI
from app.goal_suggestion import (
    GoalSuggestRequest,
    GoalValidateRequest,
    GoalCustomRefineRequest,
    GoalConfirmRequest,
    suggest_goals_by_ai,
    validate_goal_by_ai,
    refine_custom_goal_by_ai,
    save_goal_to_supabase
)

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "message": "Scrum AI Coach Backend is running"
    }


@app.post("/api/goals/suggest")
def suggest_goals(data: GoalSuggestRequest):
    goals = suggest_goals_by_ai(data)

    return {
        "message": "Goal suggestions generated successfully",
        "user_id": data.user_id,
        "name": data.name,
        "goals": goals
    }


@app.post("/api/goals/validate")
def validate_goal(data: GoalValidateRequest):
    result = validate_goal_by_ai(data)

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
