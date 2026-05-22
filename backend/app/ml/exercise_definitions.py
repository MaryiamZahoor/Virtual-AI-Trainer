"""
Exercise specifications with START and END positions.
Angles are intentionally tolerant enough for webcam-based 2D pose estimation.
"""

EXERCISE_SPECS = {
    "squats": {
        "name": "Squats",
        "description": "Lower your body by bending at knees and hips with arms extended forward",

        "start": {
            "name": "Standing Position",
            "angles": {
                "left_hip": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "right_hip": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "left_knee": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "right_knee": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "left_shoulder": {"min": 70, "max": 110, "target": 90, "tolerance": 10},
                "right_shoulder": {"min": 70, "max": 110, "target": 90, "tolerance": 10},
                "left_elbow": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "right_elbow": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
            },
        },

        "end": {
            "name": "Bottom Position (Full Squat)",
            "angles": {
                "left_hip": {"min": 55, "max": 105, "target": 80, "tolerance": 10},
                "right_hip": {"min": 55, "max": 105, "target": 80, "tolerance": 10},
                "left_knee": {"min": 65, "max": 115, "target": 90, "tolerance": 10},
                "right_knee": {"min": 65, "max": 115, "target": 90, "tolerance": 10},
                "left_shoulder": {"min": 70, "max": 110, "target": 90, "tolerance": 10},
                "right_shoulder": {"min": 70, "max": 110, "target": 90, "tolerance": 10},
                "left_elbow": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "right_elbow": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
            },
        },
    },

    "downward_dog": {
        "name": "Downward Dog",
        "description": "Yoga pose with body forming inverted V shape, hands and feet on ground",

        "start": {
            "name": "Hands and Knees Position",
            "angles": {
                "left_shoulder": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_shoulder": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "left_elbow": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "right_elbow": {"min": 165, "max": 185, "target": 180, "tolerance": 8},
                "left_hip": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_hip": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "left_knee": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_knee": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
            },
        },

        "end": {
            "name": "Full Downward Dog",
            "angles": {
                "left_shoulder": {"min": 140, "max": 175, "target": 160, "tolerance": 10},
                "right_shoulder": {"min": 140, "max": 175, "target": 160, "tolerance": 10},
                "left_elbow": {"min": 160, "max": 185, "target": 175, "tolerance": 8},
                "right_elbow": {"min": 160, "max": 185, "target": 175, "tolerance": 8},
                "left_hip": {"min": 50, "max": 100, "target": 75, "tolerance": 12},
                "right_hip": {"min": 50, "max": 100, "target": 75, "tolerance": 12},
                "left_knee": {"min": 160, "max": 185, "target": 180, "tolerance": 8},
                "right_knee": {"min": 160, "max": 185, "target": 180, "tolerance": 8},
            },
        },
    },

    "bridge": {
        "name": "Bridge (Glute Bridge)",
        "description": "Lying on back, lifting hips to create straight line from knees to shoulders",

        "start": {
            "name": "Lying on Back Position",
            "angles": {
                "left_hip": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_hip": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "left_knee": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_knee": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "left_shoulder": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_shoulder": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
            },
        },

        "end": {
            "name": "Full Bridge Position",
            "angles": {
                "left_hip": {"min": 35, "max": 65, "target": 45, "tolerance": 8},
                "right_hip": {"min": 35, "max": 65, "target": 45, "tolerance": 8},
                "left_knee": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_knee": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "left_shoulder": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
                "right_shoulder": {"min": 75, "max": 105, "target": 90, "tolerance": 10},
            },
        },
    },
}


KEYPOINTS = {
    0: "nose",
    1: "left_eye",
    2: "right_eye",
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder",
    7: "left_elbow",
    8: "right_elbow",
    9: "left_wrist",
    10: "right_wrist",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle",
}