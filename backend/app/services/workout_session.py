import time
from typing import Dict, Optional


class WorkoutSession:
    """Track start/end holds and completed reps for one WebSocket session."""

    HOLD_SECONDS = 1.0
    SCORE_THRESHOLD = 75.0

    def __init__(self):
        self.exercise_id: Optional[str] = None
        self.state = "WAITING_START"
        self.rep_count = 0
        self.confirmed_position: Optional[str] = None
        self._hold_position: Optional[str] = None
        self._hold_started_at: Optional[float] = None

    def update(self, exercise_id: str, analysis: Dict) -> Dict:
        if self.exercise_id != exercise_id:
            self.reset(exercise_id)

        detected_position = analysis.get("detected_position")
        position_scores = analysis.get("position_scores", {})
        position_score = position_scores.get(detected_position, 0.0)

        event = None
        now = time.monotonic()

        if detected_position not in ("start", "end") or position_score < self.SCORE_THRESHOLD:
            self._clear_hold()
            return self._response(event)

        held = self._update_hold(detected_position, now)

        if self.state == "WAITING_START":
            if detected_position == "start" and held:
                self.state = "WAITING_END"
                self.confirmed_position = "start"
                event = "start_confirmed"
                self._clear_hold()

        elif self.state == "WAITING_END":
            if detected_position == "end" and held:
                self.state = "WAITING_RETURN_START"
                self.confirmed_position = "end"
                event = "end_confirmed"
                self._clear_hold()

        elif self.state == "WAITING_RETURN_START":
            if detected_position == "start" and held:
                self.rep_count += 1
                self.state = "WAITING_END"
                self.confirmed_position = "start"
                event = "rep_completed"
                self._clear_hold()

        return self._response(event)

    def reset(self, exercise_id: str) -> None:
        self.exercise_id = exercise_id
        self.state = "WAITING_START"
        self.rep_count = 0
        self.confirmed_position = None
        self._clear_hold()

    def _update_hold(self, position: str, now: float) -> bool:
        if self._hold_position != position:
            self._hold_position = position
            self._hold_started_at = now
            return False

        if self._hold_started_at is None:
            self._hold_started_at = now
            return False

        return (now - self._hold_started_at) >= self.HOLD_SECONDS

    def _clear_hold(self) -> None:
        self._hold_position = None
        self._hold_started_at = None

    def _hold_progress(self) -> float:
        if self._hold_started_at is None:
            return 0.0

        elapsed = time.monotonic() - self._hold_started_at
        return round(min(elapsed / self.HOLD_SECONDS, 1.0), 2)

    def _response(self, event: Optional[str]) -> Dict:
        return {
            "rep_count": self.rep_count,
            "session_state": self.state,
            "confirmed_position": self.confirmed_position,
            "hold_progress": self._hold_progress(),
            "event": event,
        }