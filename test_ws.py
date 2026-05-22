import asyncio
import json
import time

import websockets


SQUAT_START_LANDMARKS = [
    [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],

    [100, 100],  # 5 left_shoulder
    [200, 100],  # 6 right_shoulder

    [160, 100],  # 7 left_elbow
    [260, 100],  # 8 right_elbow

    [220, 100],  # 9 left_wrist
    [320, 100],  # 10 right_wrist

    [100, 250],  # 11 left_hip
    [200, 250],  # 12 right_hip

    [100, 400],  # 13 left_knee
    [200, 400],  # 14 right_knee

    [100, 550],  # 15 left_ankle
    [200, 550],  # 16 right_ankle
]


async def main():
    uri = "ws://localhost:8000/ws/analyze"

    async with websockets.connect(uri) as websocket:
        for _ in range(40):
            await websocket.send(json.dumps({
                "exercise_id": "squats",
                "landmarks": SQUAT_START_LANDMARKS,
                "timestamp": int(time.time() * 1000),
            }))

            response = await websocket.recv()
            print(response)

            await asyncio.sleep(1 / 30)


if __name__ == "__main__":
    asyncio.run(main())