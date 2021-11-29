function docReady(fn) {
    if (document.readyState === "complete" || document.readyState === "interactive") {
        console.log('document already ready');
        setTimeout(fn, 1);
    } else {
        console.log('adding event listener');
        document.addEventListener("DOMContentLoaded", fn);
    }
}

function showData(data) {
    const outputElement = document.getElementById('question');
    outputElement.innerText = data.question;
}

class VideoRecorder {
    constructor(question_id) {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            window.alert("There is no supporting device for recording!");
        }
        this.recordButton = document.getElementById("record");
        this.playButton = document.getElementById("play");
        this.coloredCircle = document.getElementsByClassName("circle")[0];
        this.saveButton = document.getElementById("save");
        this.videoPlayer = document.getElementById('video-player');
        this.evalButton = document.getElementById('eval');
        this.transButton = document.getElementById('stt');

        this.question_id = question_id;
        this.recorder = undefined;
        this.recorded = false;
        this.recordBlobs = [];
        this.savedURL = '';
        this.transcription = '';

        this.transButton.onclick = this.handleUtter.bind(this);
        this.evalButton.onclick = this.handleEval.bind(this);
        this.recordButton.onclick = this.beginRecord.bind(this);
        this.playButton.onclick = this.playRecordedBlobs.bind(this);
        this.saveButton.onclick = this.downloadFile.bind(this);
        this.coloredCircle.onclick = this.toggleColor.bind(this);
        this.record = this.record.bind(this);
        this.detectMimeType = this.detectMimeType.bind(this);
        this.combineBlobs = this.combineBlobs.bind(this);
        this.createBlobURL = this.createBlobURL.bind(this);
        this.stopPlaying = this.stopPlaying.bind(this);
        this.playStream = this.playStream.bind(this);
        this.playRecordedBlobs = this.playRecordedBlobs.bind(this);
        this.setData = this.setData.bind(this);
        this.stopMediaStream = this.stopMediaStream.bind(this);

        this.constraints = {
            'video': {
                width: 640,
                height: 360,
            },
            'audio': {
                echoCancellation: {exact: true},
            }
        }
    }

    async beginRecord() {
        try {
            if (!this.recorder) {
                this.recorder = await this.record((stream) =>
                    this.playStream(stream), (recordedBlobs) => this.setData(recordedBlobs));
            } else {
                this.recorder.stop();
                this.stopPlaying(this.videoPlayer);
                this.recorder = undefined;
                this.recorded = true;
            }
        } catch (err) {
            console.error(err);
        }
    }

    async record(onStreamReady, onFinished) {
        const stream = await navigator.mediaDevices.getUserMedia(this.constraints);

        onStreamReady(stream);

        const options = {mimeType: this.detectMimeType()};
        const mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                this.recordBlobs.push(event.data);
            }
        };
        mediaRecorder.onstop = () => {
            onFinished(this.recordBlobs);
            this.stopMediaStream(stream);
        }
        mediaRecorder.start();
        return mediaRecorder;
    }

    detectMimeType() {
        const mimeTypes = [
            'video/webm;codecs=vp9,opus',
            'video/webm;codecs=vp8,opus',
            'video/webm',
        ];
        for (let mimeType of mimeTypes) {
            if (MediaRecorder.isTypeSupported(mimeType)) {
                return mimeType;
            }
        }
        return '';
    }

    combineBlobs(recordedBlobs) {
        return new Blob(recordedBlobs, {type: 'video/webm'});
    }

    createBlobURL(blobs) {
        const combinedBlob = this.combineBlobs(blobs);
        return window.URL.createObjectURL(combinedBlob);
    }

    stopPlaying() {
        this.videoPlayer.pause();
        this.videoPlayer.src = null;
        this.videoPlayer.srcObject = null;
    }

    playStream(stream) {
        this.stopPlaying();
        this.videoPlayer.srcObject = stream;
        this.videoPlayer.play();
    }

    playRecordedBlobs() {
        this.stopPlaying(this.videoPlayer);
        this.videoPlayer.controls = true;
        this.videoPlayer.src = this.savedURL;
        this.videoPlayer.play();
    }

    setData(data) {
        this.savedURL = this.createBlobURL(data);
    }

    async stopMediaStream(stream) {
        stream.getTracks().forEach((track) => track.stop());
    }

    async downloadFile() {
        if (this.savedURL) {
            this.saveButton.href = this.savedURL;
            this.saveButton.download = `question_${this.question_id}_answer`;
        } else {
            window.alert("No video exists!");
        }
    }

    toggleColor() {
        this.coloredCircle.classList.toggle("on-record");
    }

    async handleEval() {
        if (this.transcription) {
            const response = await fetch(`http://127.0.0.1:8080/api/score?q_id=${this.question_id}&text=${this.transcription}`, {
                method: 'GET',
            });

            if (response) {
                const json = await response.json();
                const displayElem = document.getElementById('score');
                displayElem.innerHTML = `
                    <ul>
                        ${json.result.map( item => `<li>${item.score}, when compare to the answer, ${item.text}</li>`).join()}
                    </ul>
                `;
            }
        } else {
            window.alert("Please record the answer before evaluation.")
        }
    }

    async handleUtter() {
         if (this.recordBlobs) {
            let record = new FormData();
            let blob = this.combineBlobs(this.recordBlobs);
            let currentDate = new Date();
            let datetime = `${currentDate.getMonth()+1}${currentDate.getDate()}_${currentDate.getHours()}:${(currentDate.getMinutes() < 10)?"0":"" + String(currentDate.getMinutes())}:${(currentDate.getSeconds() < 10)?"0":"" + String(currentDate.getSeconds())}`
            record.append("q_id", this.question_id);
            record.append("file", blob, `question_${this.question_id}_answer_${datetime}.webm`);
            const response = await fetch(`http://127.0.0.1:8080/api/file`, {
                method: 'POST',
                body: record
            });

            if (response) {
                const json = await response.json();
                this.transcription = json.stt;
                const displayElem = document.getElementById('display');
                displayElem.innerHTML = `
                    <p>${this.transcription}</p>
                `;
            }
        }
    }
}

!async function () {
    const response = await fetch('http://127.0.0.1:8080/api/question');
    const data = await response.json();
    console.log(data);
    docReady(showData(data));
    window.videoRecorder = new VideoRecorder(data.id);
}();