import Question from "./question.js";
import Speech from "./speech.js";

class App {
    constructor() {
        new Question(document.getElementById("question"));
        new Speech(document.getElementById("speech"));
    }
}

new App();