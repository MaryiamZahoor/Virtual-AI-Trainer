class FeedbackRenderer {
    constructor() {
        this.elements = {
            detectedPosition: document.getElementById("detected-position"),
            sessionState: document.getElementById("session-state"),
            repCount: document.getElementById("rep-count"),
            accuracyScore: document.getElementById("accuracy-score"),
            holdPercent: document.getElementById("hold-percent"),
            holdProgressBar: document.getElementById("hold-progress-bar"),
            correctJoints: document.getElementById("correct-joints"),
            warningJoints: document.getElementById("warning-joints"),
            wrongJoints: document.getElementById("wrong-joints"),
            suggestionList: document.getElementById("suggestion-list"),
            eventLog: document.getElementById("event-log"),
        };
    }

    render(data) {
        this.elements.detectedPosition.textContent = this.formatValue(data.detected_position);
        this.elements.sessionState.textContent = this.formatValue(data.session_state);
        this.elements.repCount.textContent = data.rep_count ?? 0;
        this.elements.accuracyScore.textContent = this.formatPercent(data.accuracy_score);

        this.renderHoldProgress(data.hold_progress);
        this.renderJoints(data);
        this.renderSuggestions(data.feedback || []);

        if (data.event) {
            this.addEvent(data.event, data.rep_count);
        }
    }

    renderHoldProgress(progress) {
        const safeProgress = Math.max(0, Math.min(progress || 0, 1));
        const percent = Math.round(safeProgress * 100);

        this.elements.holdPercent.textContent = `${percent}%`;
        this.elements.holdProgressBar.style.width = `${percent}%`;
    }

    renderJoints(data) {
        this.elements.correctJoints.textContent = this.formatList(data.correct_joints);
        this.elements.warningJoints.textContent = this.formatList(data.warning_joints);
        this.elements.wrongJoints.textContent = this.formatList(data.wrong_joints);
    }

    renderSuggestions(feedback) {
        this.elements.suggestionList.innerHTML = "";

        if (!feedback.length) {
            const item = document.createElement("li");
            item.textContent = "No corrections needed.";
            this.elements.suggestionList.appendChild(item);
            return;
        }

        feedback.forEach((message) => {
            const item = document.createElement("li");
            item.textContent = message;
            this.elements.suggestionList.appendChild(item);
        });
    }

    addEvent(eventName, repCount) {
        const item = document.createElement("li");
        item.textContent = this.formatEvent(eventName, repCount);

        this.elements.eventLog.prepend(item);

        while (this.elements.eventLog.children.length > 8) {
            this.elements.eventLog.removeChild(this.elements.eventLog.lastChild);
        }
    }

    formatValue(value) {
        if (!value) {
            return "--";
        }

        return value.replace(/_/g, " ");
    }

    formatPercent(value) {
        if (value === undefined || value === null) {
            return "--";
        }

        return `${Math.round(value)}%`;
    }

    formatList(items) {
        if (!items || !items.length) {
            return "--";
        }

        return items.map((item) => item.replace(/_/g, " ")).join(", ");
    }

    formatEvent(eventName, repCount) {
        if (eventName === "start_confirmed") {
            return "Start position confirmed.";
        }

        if (eventName === "end_confirmed") {
            return "End position confirmed.";
        }

        if (eventName === "rep_completed") {
            return `Rep completed. Total reps: ${repCount}.`;
        }

        return eventName.replace(/_/g, " ");
    }
}