from typing import Dict, List, Literal, Optional, Sequence, Tuple

from app.ml.exercise_definitions import EXERCISE_SPECS
from app.services.angle_analyzer import analyzer


class ExerciseValidator:
    """Analyze exercise landmarks against start and end pose specifications."""

    POSITION_THRESHOLD = 75.0
    AMBIGUITY_MARGIN = 10.0
    KEYPOINT_CONFIDENCE_THRESHOLD = 0.35

    ANGLE_KEYPOINT_MAPPING = {
        "left_knee": (11, 13, 15),
        "right_knee": (12, 14, 16),
        "left_hip": (5, 11, 13),
        "right_hip": (6, 12, 14),
        "left_elbow": (5, 7, 9),
        "right_elbow": (6, 8, 10),
        "left_shoulder": (11, 5, 7),
        "right_shoulder": (12, 6, 8),
    }

    SIDE_ANGLES = {
        "left": {"left_knee", "left_hip", "left_elbow", "left_shoulder"},
        "right": {"right_knee", "right_hip", "right_elbow", "right_shoulder"},
    }

    def analyze_pose(self, exercise_id: str, landmarks: List[Sequence[float]]) -> Dict:
        if exercise_id not in EXERCISE_SPECS:
            return {"error": f"Unknown exercise: {exercise_id}"}

        exercise = EXERCISE_SPECS[exercise_id]
        all_angles = self._calculate_exercise_angles(exercise_id, landmarks)
        visible_side = self._select_visible_side(all_angles)

        if visible_side == "unknown":
            detection = {
                "detected_position": "unknown",
                "closest_position": "unknown",
                "position_scores": {"start": 0.0, "end": 0.0},
            }
            return self._unknown_pose_response(exercise_id, all_angles, detection, visible_side)

        angles_found = self._filter_angles_for_side(all_angles, visible_side)
        detection = self._detect_position(exercise, angles_found, visible_side)

        if detection["detected_position"] == "unknown":
            return self._unknown_pose_response(exercise_id, angles_found, detection, visible_side)

        return self._validate_detected_position(
            exercise_id=exercise_id,
            detected_position=detection["detected_position"],
            detection=detection,
            angles_found=angles_found,
            visible_side=visible_side,
        )

    def validate_pose(
        self,
        exercise_id: str,
        landmarks: List[Sequence[float]],
        position: Literal["start", "end"] = "end",
    ) -> Dict:
        if exercise_id not in EXERCISE_SPECS:
            return {"error": f"Unknown exercise: {exercise_id}"}

        if position not in ("start", "end"):
            return {"error": f"Position must be 'start' or 'end', got '{position}'"}

        all_angles = self._calculate_exercise_angles(exercise_id, landmarks)
        visible_side = self._select_visible_side(all_angles)
        angles_found = self._filter_angles_for_side(all_angles, visible_side)

        return self._validate_against_position(
            exercise_id=exercise_id,
            position=position,
            angles_found=angles_found,
            visible_side=visible_side,
        )

    def _validate_detected_position(
        self,
        exercise_id: str,
        detected_position: Literal["start", "end"],
        detection: Dict,
        angles_found: Dict[str, float],
        visible_side: str,
    ) -> Dict:
        results = self._validate_against_position(
            exercise_id=exercise_id,
            position=detected_position,
            angles_found=angles_found,
            visible_side=visible_side,
        )

        results["detected_position"] = detection["detected_position"]
        results["closest_position"] = detection["closest_position"]
        results["position_scores"] = detection["position_scores"]
        results["visible_side"] = visible_side

        return results

    def _unknown_pose_response(
        self,
        exercise_id: str,
        angles_found: Dict[str, float],
        detection: Dict,
        visible_side: str,
    ) -> Dict:
        return {
            "exercise_id": exercise_id,
            "position": "unknown",
            "position_name": "Unknown",
            "correct_joints": [],
            "warning_joints": [],
            "wrong_joints": [],
            "feedback": ["Move your full body into view or hold the pose more clearly."],
            "angles": angles_found,
            "accuracy_score": 0.0,
            "is_valid": False,
            "detected_position": "unknown",
            "closest_position": detection["closest_position"],
            "position_scores": detection["position_scores"],
            "visible_side": visible_side,
        }

    def _calculate_exercise_angles(
        self,
        exercise_id: str,
        landmarks: List[Sequence[float]],
    ) -> Dict[str, float]:
        exercise = EXERCISE_SPECS[exercise_id]
        angle_names = set(exercise["start"]["angles"]) | set(exercise["end"]["angles"])

        angles_found = {}

        for angle_name in angle_names:
            angle_value = self._calculate_angle(angle_name, landmarks)

            if angle_value is not None:
                angles_found[angle_name] = round(angle_value, 1)

        return angles_found

    def _select_visible_side(self, angles_found: Dict[str, float]) -> str:
        left_count = len(self.SIDE_ANGLES["left"] & set(angles_found))
        right_count = len(self.SIDE_ANGLES["right"] & set(angles_found))

        if left_count == 0 and right_count == 0:
            return "unknown"

        if left_count >= right_count:
            return "left"

        return "right"

    def _filter_angles_for_side(self, angles_found: Dict[str, float], visible_side: str) -> Dict[str, float]:
        if visible_side not in self.SIDE_ANGLES:
            return {}

        allowed_angles = self.SIDE_ANGLES[visible_side]

        return {
            angle_name: angle_value
            for angle_name, angle_value in angles_found.items()
            if angle_name in allowed_angles
        }

    def _detect_position(self, exercise: Dict, angles_found: Dict[str, float], visible_side: str) -> Dict:
        start_score = self._calculate_position_score(angles_found, exercise["start"], visible_side)
        end_score = self._calculate_position_score(angles_found, exercise["end"], visible_side)

        if start_score == 0 and end_score == 0:
            closest_position = "unknown"
            detected_position = "unknown"
        else:
            closest_position = "start" if start_score >= end_score else "end"
            best_score = max(start_score, end_score)
            score_gap = abs(start_score - end_score)

            if best_score < self.POSITION_THRESHOLD or score_gap < self.AMBIGUITY_MARGIN:
                detected_position = "unknown"
            else:
                detected_position = closest_position

        return {
            "detected_position": detected_position,
            "closest_position": closest_position,
            "position_scores": {
                "start": round(start_score, 1),
                "end": round(end_score, 1),
            },
        }

    def _calculate_position_score(
        self,
        angles_found: Dict[str, float],
        position_spec: Dict,
        visible_side: str,
    ) -> float:
        total = 0.0
        score = 0.0
        allowed_angles = self.SIDE_ANGLES.get(visible_side, set())

        for angle_name, angle_spec in position_spec["angles"].items():
            if angle_name not in allowed_angles:
                continue

            if angle_name not in angles_found:
                continue

            current = angles_found[angle_name]
            min_angle = angle_spec["min"]
            max_angle = angle_spec["max"]
            tolerance = angle_spec.get("tolerance", 5)

            total += 1

            if min_angle <= current <= max_angle:
                score += 1.0
            elif (min_angle - tolerance) <= current <= (max_angle + tolerance):
                score += 0.5

        if total == 0:
            return 0.0

        return (score / total) * 100

    def _validate_against_position(
        self,
        exercise_id: str,
        position: Literal["start", "end"],
        angles_found: Dict[str, float],
        visible_side: str,
    ) -> Dict:
        exercise = EXERCISE_SPECS[exercise_id]
        position_spec = exercise[position]
        allowed_angles = self.SIDE_ANGLES.get(visible_side, set())

        results = {
            "exercise_id": exercise_id,
            "position": position,
            "position_name": position_spec.get("name", position),
            "correct_joints": [],
            "warning_joints": [],
            "wrong_joints": [],
            "feedback": [],
            "angles": angles_found,
            "visible_side": visible_side,
        }

        missing_angles = []

        for angle_name, angle_spec in position_spec["angles"].items():
            if angle_name not in allowed_angles:
                continue

            if angle_name not in angles_found:
                missing_angles.append(angle_name)
                continue

            angle_value = angles_found[angle_name]
            min_angle = angle_spec["min"]
            max_angle = angle_spec["max"]
            tolerance = angle_spec.get("tolerance", 5)

            if min_angle <= angle_value <= max_angle:
                results["correct_joints"].append(angle_name)
            elif (min_angle - tolerance) <= angle_value <= (max_angle + tolerance):
                results["warning_joints"].append(angle_name)
                results["feedback"].append(
                    self._build_coaching_message(
                        exercise_id=exercise_id,
                        position=position,
                        angle_name=angle_name,
                        angle_value=angle_value,
                        min_angle=min_angle,
                        max_angle=max_angle,
                        severity="warning",
                    )
                )
            else:
                results["wrong_joints"].append(angle_name)
                results["feedback"].append(
                    self._build_coaching_message(
                        exercise_id=exercise_id,
                        position=position,
                        angle_name=angle_name,
                        angle_value=angle_value,
                        min_angle=min_angle,
                        max_angle=max_angle,
                        severity="wrong",
                    )
                )

        if missing_angles:
            readable_joints = ", ".join(self._format_joint_name(angle) for angle in missing_angles)
            results["feedback"].append(
                f"I cannot clearly see your {readable_joints}. Turn slightly or step back so the visible side is clearer."
            )

        total_angles = (
            len(results["correct_joints"])
            + len(results["warning_joints"])
            + len(results["wrong_joints"])
        )

        if total_angles > 0:
            accuracy = (len(results["correct_joints"]) / total_angles) * 100
        else:
            accuracy = 0.0

        results["accuracy_score"] = round(accuracy, 1)
        results["is_valid"] = len(results["wrong_joints"]) == 0 and not missing_angles

        return results

    def _build_coaching_message(
        self,
        exercise_id: str,
        position: str,
        angle_name: str,
        angle_value: float,
        min_angle: float,
        max_angle: float,
        severity: str,
    ) -> str:
        if angle_value < min_angle:
            direction = "increase"
        elif angle_value > max_angle:
            direction = "decrease"
        else:
            direction = "adjust"

        cue = self._get_exercise_specific_cue(
            exercise_id=exercise_id,
            position=position,
            angle_name=angle_name,
            direction=direction,
        )

        prefix = "Almost there. " if severity == "warning" else ""
        joint_label = self._format_joint_name(angle_name)

        return f"{prefix}{cue} ({joint_label}: {angle_value:.1f} deg)"

    def _get_exercise_specific_cue(
        self,
        exercise_id: str,
        position: str,
        angle_name: str,
        direction: str,
    ) -> str:
        joint_type = self._joint_type(angle_name)
        side = self._joint_side(angle_name)

        exercise_cues = {
            "squats": {
                "knee": {
                    "increase": f"Straighten your {side} knee slightly.",
                    "decrease": f"Bend your {side} knee more.",
                },
                "hip": {
                    "increase": f"Stand taller through your {side} hip.",
                    "decrease": "Sit your hips back and lower your body more.",
                },
                "shoulder": {
                    "increase": f"Raise your {side} arm closer to shoulder height.",
                    "decrease": f"Lower your {side} arm slightly toward shoulder height.",
                },
                "elbow": {
                    "increase": f"Straighten your {side} elbow more.",
                    "decrease": f"Relax the bend in your {side} elbow.",
                },
            },
            "downward_dog": {
                "knee": {
                    "increase": f"Straighten your {side} leg more.",
                    "decrease": f"Soften your {side} knee slightly.",
                },
                "hip": {
                    "increase": "Push your hips higher and lengthen your back.",
                    "decrease": "Bring your hips slightly lower and avoid overfolding.",
                },
                "shoulder": {
                    "increase": "Push your chest back between your arms.",
                    "decrease": "Bring your shoulders slightly forward over your hands.",
                },
                "elbow": {
                    "increase": f"Straighten your {side} arm more.",
                    "decrease": f"Soften your {side} elbow slightly.",
                },
            },
            "bridge": {
                "knee": {
                    "increase": f"Move your {side} foot slightly farther from your hips.",
                    "decrease": f"Bring your {side} foot slightly closer to your hips.",
                },
                "hip": {
                    "increase": "Lower your hips slightly.",
                    "decrease": "Lift your hips higher.",
                },
                "shoulder": {
                    "increase": f"Keep your {side} arm flat beside your body.",
                    "decrease": f"Relax your {side} shoulder and keep the arm on the ground.",
                },
                "elbow": {
                    "increase": f"Keep your {side} arm straighter on the ground.",
                    "decrease": f"Relax your {side} elbow and keep the arm flat.",
                },
            },
        }

        cue_group = exercise_cues.get(exercise_id, {})
        joint_cues = cue_group.get(joint_type)

        if joint_cues and direction in joint_cues:
            return joint_cues[direction]

        return self._get_general_cue(angle_name, direction)

    def _get_general_cue(self, angle_name: str, direction: str) -> str:
        joint_type = self._joint_type(angle_name)
        side = self._joint_side(angle_name)

        if joint_type in ("knee", "elbow"):
            if direction == "increase":
                return f"Straighten your {side} {joint_type} slightly."
            if direction == "decrease":
                return f"Bend your {side} {joint_type} more."

        if joint_type == "hip":
            if direction == "increase":
                return f"Open your {side} hip angle slightly."
            if direction == "decrease":
                return f"Close your {side} hip angle slightly."

        if joint_type == "shoulder":
            if direction == "increase":
                return f"Raise your {side} arm slightly."
            if direction == "decrease":
                return f"Lower your {side} arm slightly."

        return f"Adjust your {self._format_joint_name(angle_name)}."

    def _format_joint_name(self, angle_name: str) -> str:
        return angle_name.replace("_", " ")

    def _joint_side(self, angle_name: str) -> str:
        if angle_name.startswith("left_"):
            return "left"

        if angle_name.startswith("right_"):
            return "right"

        return ""

    def _joint_type(self, angle_name: str) -> str:
        return angle_name.replace("left_", "").replace("right_", "")

    def _calculate_angle(
        self,
        angle_name: str,
        landmarks: List[Sequence[float]],
    ) -> Optional[float]:
        if angle_name not in self.ANGLE_KEYPOINT_MAPPING:
            return None

        p1_idx, p2_idx, p3_idx = self.ANGLE_KEYPOINT_MAPPING[angle_name]

        try:
            p1 = landmarks[p1_idx]
            p2 = landmarks[p2_idx]
            p3 = landmarks[p3_idx]
        except (IndexError, TypeError):
            return None

        if not self._keypoints_visible(p1, p2, p3):
            return None

        return analyzer.calculate_angle(
            self._point_xy(p1),
            self._point_xy(p2),
            self._point_xy(p3),
        )

    def _keypoints_visible(self, *points: Sequence[float]) -> bool:
        for point in points:
            if len(point) >= 3 and point[2] < self.KEYPOINT_CONFIDENCE_THRESHOLD:
                return False

        return True

    def _point_xy(self, point: Sequence[float]) -> Tuple[float, float]:
        return float(point[0]), float(point[1])


validator = ExerciseValidator()