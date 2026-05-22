from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.exercise_validator import validator
from app.services.workout_session import WorkoutSession

router = APIRouter()


class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as exc:
                print(f"Error broadcasting: {exc}")


manager = ConnectionManager()


@router.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    Analyze pose landmarks for one workout session.

    Expected client message:
    {
        "exercise_id": "squats",
        "landmarks": [[x, y], [x, y], ...],
        "timestamp": 1234567890
    }
    """
    await manager.connect(websocket)
    session = WorkoutSession()

    try:
        while True:
            data = await websocket.receive_json()

            exercise_id = data.get("exercise_id")
            landmarks = data.get("landmarks")

            if not exercise_id or not landmarks:
                await manager.send_personal(websocket, {
                    "error": "Missing exercise_id or landmarks"
                })
                continue

            analysis = validator.analyze_pose(exercise_id, landmarks)

            if "error" in analysis:
                await manager.send_personal(websocket, analysis)
                continue

            session_update = session.update(exercise_id, analysis)

            response = {
                **analysis,
                **session_update,
            }

            if "timestamp" in data:
                response["timestamp"] = data["timestamp"]

            await manager.send_personal(websocket, response)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as exc:
        print(f"WebSocket error: {exc}")
        await manager.disconnect(websocket)