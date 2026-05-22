class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async getExercises() {
        const response = await fetch(`${this.baseUrl}/exercises`);

        if (!response.ok) {
            throw new Error("Failed to load exercises");
        }

        const data = await response.json();
        return data.exercises || [];
    }

    async getExercise(exerciseId) {
        const response = await fetch(`${this.baseUrl}/exercises/${exerciseId}`);

        if (!response.ok) {
            throw new Error(`Failed to load exercise: ${exerciseId}`);
        }

        return response.json();
    }
}