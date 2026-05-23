from app.ml.exercise_definitions import EXERCISE_SPECS


def test_squats_exist():
    assert "squats" in EXERCISE_SPECS


def test_exercises_have_start_and_end_positions():
    for exercise in EXERCISE_SPECS.values():
        assert "start" in exercise
        assert "end" in exercise
        assert "angles" in exercise["start"]
        assert "angles" in exercise["end"]


def test_squat_has_elbow_angles():
    squat = EXERCISE_SPECS["squats"]

    assert "left_elbow" in squat["start"]["angles"]
    assert "right_elbow" in squat["start"]["angles"]
    assert "left_elbow" in squat["end"]["angles"]
    assert "right_elbow" in squat["end"]["angles"]