import VideoRecorder from "./recorder.js";

export default class Speech {
    constructor() {
        new VideoRecorder(document.getElementById('speech'));
    }
}