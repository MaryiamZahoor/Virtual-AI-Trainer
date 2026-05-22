const DemoLandmarks = {
    squatStart: [
        [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
        [100, 100], [200, 100],
        [160, 100], [260, 100],
        [220, 100], [320, 100],
        [100, 250], [200, 250],
        [100, 400], [200, 400],
        [100, 550], [200, 550],
    ],

    squatEnd: [
        [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
        [100, 100], [200, 100],
        [160, 100], [260, 100],
        [220, 100], [320, 100],
        [100, 250], [200, 250],
        [250, 224], [350, 224],
        [276, 374], [376, 374],
    ],

    getSquatRepSequence() {
        return [
            ...this.repeat(this.squatStart, 36),
            ...this.repeat(this.squatEnd, 36),
            ...this.repeat(this.squatStart, 36),
        ];
    },

    repeat(landmarks, count) {
        return Array.from({ length: count }, () => landmarks);
    },
};