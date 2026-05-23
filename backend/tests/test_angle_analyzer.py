from app.services.angle_analyzer import analyzer


def test_calculate_right_angle():
    angle = analyzer.calculate_angle(
        point1=(1, 0),
        point2=(0, 0),
        point3=(0, 1),
    )

    assert round(angle, 1) == 90.0


def test_calculate_straight_angle():
    angle = analyzer.calculate_angle(
        point1=(-1, 0),
        point2=(0, 0),
        point3=(1, 0),
    )

    assert round(angle, 1) == 180.0