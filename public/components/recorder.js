import Component from "./component.js";

export default class VideoRecorder extends Component{
    constructor(target) {
        super(target);
        this.$recordBlobs = [];
        this.$recorded = false;
        this.$recorder = undefined;
        this.$savedURL = ''
        this.$videoPlayer = document.getElementById('video-player');
    }

    setup() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            window.alert("There is no supporting device for recording!");
        }
    }

    template() {
        return `
            <div class="video">
                <video id="video-player" controls></video>
            </div>
            <div class="control-bar">
                <a id="save">
                    <i class="fas fa-file-download fa-3x"></i>
                </a>
                <div class="space"></div>
                <i class="fas fa-check-square fa-3x" id="eval"></i>
                <div class="space"></div>
                <div id="record">
                    <div class="circle"></div>
                </div>
                <div class="space"></div>
                <i class="fas fa-play fa-3x" id="play"></i>
            </div>
            <div id="display"></div>
        `
    }

    setEvent() {
        document.getElementById("record").addEventListener('click', async () => {
            try {
                if (!this.$recorder) {
                    this.$recorder = await this.record((stream) =>
                        this.playStream(stream), (recordedBlobs) => this.setData(recordedBlobs));
                } else {
                    this.$recorder.stop();
                    this.stopPlaying(this.$videoPlayer);
                    this.$recorder = undefined;
                    this.$recorded = true;
                }
            } catch (err) {
                console.error(err);
            }
        })
        document.getElementById("play").addEventListener('click', () => {
            this.stopPlaying(this.$videoPlayer);
            this.$videoPlayer.controls = true;
            this.$videoPlayer.src = this.$savedURL;
            this.$videoPlayer.play();
        });
        document.getElementsByClassName('circle')[0].addEventListener('click', ({target})=> {
            target.classList.toggle("on-record");
        });
        document.getElementById("save").addEventListener('click', ({currentTarget}) => {
            if (this.$savedURL) {
                currentTarget.href = this.$savedURL;
                currentTarget.download = 'video.webm';
            } else {
                window.alert("No video exists!");
            }
        });
        document.getElementById('eval').addEventListener('click', async () => {
            if (this.$recordBlobs) {
                let record = new FormData();
                let blob = this.combineBlobs(this.$recordBlobs);
                record.append("q_id", this.question_id);
                record.append("file", blob, "interview.webm");
                const response = await fetch(`http://127.0.0.1:8081/api/file`, {
                    method: 'POST',
                    body: record
                });

                if (response) {
                    const json = await response.json();
                    const displayElem = document.getElementById('display');
                    displayElem.innerHTML = `
                        <p>${json.stt}</p>
                        <ul>
                            ${json.result.map(item => `<li>${item.score}, when compare to the answer "${item.text}"</li>`).join('')}
                        </ul>
                    `;
                    console.log(json.stt);
                    console.log(json.result.forEach(elem => console.log(elem.score)));
                }
            }
        });
    }

    async record(onStreamReady, onFinished) {
        const stream = await navigator.mediaDevices.getUserMedia({
            'video': {
                width: 640,
                height: 360,
            },
            'audio': {
                echoCancellation: {exact: true},
            }
        });

        onStreamReady(stream);

        const options = {mimeType: this.detectMimeType()};
        const mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                this.$recordBlobs.push(event.data);
            }
        };
        mediaRecorder.onstop = () => {
            onFinished(this.$recordBlobs);
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

    playStream(stream) {
        this.stopPlaying(this.$videoPlayer);
        this.$videoPlayer.srcObject = stream;
        this.$videoPlayer.play();
    }

    stopMediaStream(stream) {
        stream.getTracks().forEach((track) => track.stop());
    }

    setData(data) {
        this.$savedURL = this.createBlobURL(data);
    }

    combineBlobs(recordedBlobs) {
        return new Blob(recordedBlobs, {type: 'video/webm'});
    }

    createBlobURL(blobs) {
        const combinedBlob = this.combineBlobs(blobs);
        return window.URL.createObjectURL(combinedBlob);
    }

    stopPlaying(player) {
        player.pause();
        player.src = null;
        player.srcObject = null;
    }
}