from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

from app.action_plan import (
    ActionGenerateRequest,
    ActionStepStatusRequest,
    generate_action_steps_by_ai,
    save_action_steps_to_supabase,
    update_action_step_status
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
    allow_headers=["*"],
)


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