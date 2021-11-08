const recordButton = document.getElementById("record");
const playButton = document.getElementById("play");
const coloredCircle = document.getElementsByClassName("circle")[0];
const evalButton = document.getElementById("eval");

const initMediaStream = async function() {
    // returns promise( resolved: MediaStream, failed: NonallowedError / NotFoundError, DOMException )
    const constraints = {
        'video': {
            width: 640,
            height: 360,
        },
        'audio': {
            echoCancellation: { exact: true },
        }
    };
    return await navigator.mediaDevices.getUserMedia(constraints);
};

const beginRecord = async (onStreamReady, onFinished) => {
    const stream = await initMediaStream();

    onStreamReady(stream);

    const options = { mimeType: detectMimeType() };
    const recordBlobs = [];
    const mediaRecorder = new MediaRecorder(stream, options);
    mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
            recordBlobs.push(event.data);
        }
    };
    mediaRecorder.onstop = () => {
        onFinished(recordBlobs);
        stopMediaStream(stream);
    }
    mediaRecorder.start();
    return mediaRecorder;
}

const detectMimeType = () => {
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
};

const combineBlobs = (recordedBlobs) => {
    return new Blob(recordedBlobs, { type: 'video/webm' });
};

const createBlobURL = (blobs) => {
    const combinedBlob = combineBlobs(blobs);
    return window.URL.createObjectURL(combinedBlob);
};

const stopPlaying = (videoElement) => {
    videoElement.pause();
    videoElement.src = null;
    videoElement.srcObject = null;
};

const playStream = (videoElement, stream) => {
    stopPlaying(videoElement);
    videoElement.srcObject = stream;
    videoElement.play();
}

const playRecordedBlobs = (videoElement, url) => {
    stopPlaying(videoElement);

    videoElement.controls = true;
    videoElement.src = url;
    videoElement.play();
};

const setData = (data) => {
    const url = createBlobURL(data);
    localStorage.setItem('audio_sample', url);
    console.log('saved locally.');
};

const stopMediaStream = async (stream) => {
    stream.getTracks().forEach((track) => track.stop());
};

let recorder = undefined;
let recorded = false;
document.addEventListener("DOMContentLoaded", function() {
    const videoElement = document.getElementById('video-player');

    recordButton.addEventListener('click', async function(){
        try {
            if(!recorder){
                recorder = await beginRecord((stream) =>
                    playStream(videoElement, stream), (recordedBlobs) => setData(recordedBlobs));
            }else {
                recorder.stop();
                stopPlaying(videoElement);
                recorder = undefined;
                recorded = true;
            }
        } catch (err) {
            console.error(err);
        }
    });

    playButton.addEventListener('click', function(){
        const savedURL = localStorage.getItem("audio_sample");
        playRecordedBlobs(videoElement, savedURL);
    });

    coloredCircle.onclick = function() {
        coloredCircle.classList.toggle("on-record");
    }

    // To-do: Blob transfer
});
