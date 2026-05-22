from fastapi import APIRouter, HTTPException
from app.ml.exercise_definitions import EXERCISE_SPECS

router = APIRouter()


@router.get("/health")
async def health():
    """Check if API is running"""
    return {"status": "ok"}


@router.get("/exercises")
async def get_exercises():
    """Get all available exercises"""
    exercises = [] 
    
    for exercise_id, spec in EXERCISE_SPECS.items():
        exercises.append({
            "id": exercise_id,
            "name": spec["name"],
            "description": spec["description"],
            "start": {
                "name": spec["start"]["name"],
                "angles": list(spec["start"]["angles"].keys())
            },
            "end": {
                "name": spec["end"]["name"],
                "angles": list(spec["end"]["angles"].keys())
            }
        })
    
    return {"exercises": exercises}


@router.get("/exercises/{exercise_id}")
async def get_exercise(exercise_id: str):
    """Get details of a specific exercise"""
    if exercise_id not in EXERCISE_SPECS:
        raise HTTPException(status_code=404, detail=f"Exercise '{exercise_id}' not found")
    
    spec = EXERCISE_SPECS[exercise_id]
    
    return {
        "id": exercise_id,
        "name": spec["name"],
        "description": spec["description"],
        "start": {
            "name": spec["start"]["name"],
            "angles": spec["start"]["angles"]
        },
        "end": {
            "name": spec["end"]["name"],
            "angles": spec["end"]["angles"]
        }
    }