import asyncio
import json
import time

import websockets


SQUAT_START_LANDMARKS = [
    [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],

    [100, 100],  # left_shoulder
    [200, 100],  # right_shoulder

    [160, 100],  # left_elbow
    [260, 100],  # right_elbow

    [220, 100],  # left_wrist
    [320, 100],  # right_wrist

    [100, 250],  # left_hip
    [200, 250],  # right_hip

    [100, 400],  # left_knee
    [200, 400],  # right_knee

    [100, 550],  # left_ankle
    [200, 550],  # right_ankle
]


SQUAT_END_LANDMARKS = [
    [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],

    [100, 100],  # left_shoulder
    [200, 100],  # right_shoulder

    [160, 100],  # left_elbow
    [260, 100],  # right_elbow

    [220, 100],  # left_wrist
    [320, 100],  # right_wrist

    [100, 250],  # left_hip
    [200, 250],  # right_hip

    [250, 224],  # left_knee
    [350, 224],  # right_knee

    [276, 374],  # left_ankle
    [376, 374],  # right_ankle
]


async def send_frame(websocket, landmarks):
    await websocket.send(json.dumps({
        "exercise_id": "squats",
        "landmarks": landmarks,
        "timestamp": int(time.time() * 1000),
    }))

    response = await websocket.recv()
    data = json.loads(response)

    print(
        f"detected={data.get('detected_position')} "
        f"score={data.get('position_scores')} "
        f"state={data.get('session_state')} "
        f"hold={data.get('hold_progress')} "
        f"event={data.get('event')} "
        f"reps={data.get('rep_count')}"
    )


async def send_pose_for_seconds(websocket, landmarks, seconds, fps=30):
    frame_count = int(seconds * fps)

    for _ in range(frame_count):
        await send_frame(websocket, landmarks)
        await asyncio.sleep(1 / fps)


async def main():
    uri = "ws://localhost:8000/ws/analyze"

    async with websockets.connect(uri) as websocket:
        print("Holding squat start...")
        await send_pose_for_seconds(websocket, SQUAT_START_LANDMARKS, seconds=1.2)

        print("Holding squat end...")
        await send_pose_for_seconds(websocket, SQUAT_END_LANDMARKS, seconds=1.2)

        print("Returning to squat start...")
        await send_pose_for_seconds(websocket, SQUAT_START_LANDMARKS, seconds=1.2)


if __name__ == "__main__":
    asyncio.run(main())