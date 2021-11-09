class VideoRecorder {
    constructor() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            window.alert("There is no supporting device for recording!")
        }
        this.recordButton = document.getElementById("record")
        this.playButton = document.getElementById("play")
        this.coloredCircle = document.getElementsByClassName("circle")[0]
        this.saveButton = document.getElementById("save")
        this.videoPlayer = document.getElementById('video-player')

        this.recorder = undefined
        this.recorded = false
        this.recordBlobs = []
        this.savedURL = ''

        this.recordButton.onclick = this.beginRecord.bind(this)
        this.playButton.onclick = this.playRecordedBlobs.bind(this)
        this.saveButton.onclick = this.downloadFile.bind(this)
        this.coloredCircle.onclick = this.toggleColor.bind(this)
        this.record = this.record.bind(this)
        this.detectMimeType = this.detectMimeType.bind(this)
        this.combineBlobs = this.combineBlobs.bind(this)
        this.createBlobURL = this.createBlobURL.bind(this)
        this.stopPlaying = this.stopPlaying.bind(this)
        this.playStream = this.playStream.bind(this)
        this.playRecordedBlobs = this.playRecordedBlobs.bind(this)
        this.setData = this.setData.bind(this)
        this.stopMediaStream = this.stopMediaStream.bind(this)

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
            if(!this.recorder){
                this.recorder = await this.record((stream) =>
                    this.playStream(stream), (recordedBlobs) => this.setData(recordedBlobs));
            }else {
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

        const options = { mimeType: this.detectMimeType() };
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
        return new Blob(recordedBlobs, { type: 'video/webm' });
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
            this.saveButton.download = 'video.webm';
        }else {
            window.alert("No video exists!");
        }
    }

    toggleColor(){
        this.coloredCircle.classList.toggle("on-record");
    }
}

window.videoRecorder = new VideoRecorder();
