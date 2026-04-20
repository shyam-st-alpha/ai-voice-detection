let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let streamRef = null;

// UI elements
const btn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const resultText = document.getElementById("result");
const loader = document.getElementById("loader");
const wave = document.getElementById("wave");
const confidenceText = document.getElementById("confidence");
const themeBtn = document.getElementById("themeBtn");

// 🎧 Canvas for waveform
const canvas = document.getElementById("visualizer");
const ctx = canvas.getContext("2d");

let animationId = null;

// 🎧 DRAW REAL WAVEFORM
function drawWave(stream) {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();

    source.connect(analyser);
    analyser.fftSize = 256;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        animationId = requestAnimationFrame(draw);

        analyser.getByteFrequencyData(dataArray);

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let barWidth = (canvas.width / bufferLength) * 2;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            let barHeight = dataArray[i];

            ctx.fillStyle = "#3498db";
            ctx.fillRect(x, canvas.height - barHeight / 2, barWidth, barHeight / 2);

            x += barWidth + 1;
        }
    }

    draw();
}

// 🛑 STOP WAVEFORM
function stopWave() {
    if (animationId) {
        cancelAnimationFrame(animationId);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

// 🎤 RECORD BUTTON
btn.onclick = async () => {
    try {
        if (!isRecording) {
            console.log("🎙 START RECORDING");

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef = stream;

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };

            mediaRecorder.start();
            isRecording = true;

            btn.innerText = "⏹ Stop Recording";
            btn.classList.add("recording");

            statusText.innerText = "Recording...";
            resultText.innerText = "";
            confidenceText.innerText = "";

            loader.style.display = "none";
            wave.style.visibility = "visible";

            // 🎧 start waveform
            drawWave(stream);

        } else {
            console.log("⏹ STOP RECORDING");

            mediaRecorder.stop();
            isRecording = false;

            btn.innerText = "🎤 Start Recording";
            btn.classList.remove("recording");

            statusText.innerText = "Processing...";
            loader.style.display = "block";
            wave.style.visibility = "hidden";

            // stop waveform
            stopWave();

            // stop mic stream
            if (streamRef) {
                streamRef.getTracks().forEach(track => track.stop());
            }

            mediaRecorder.onstop = async () => {
                try {
                    console.log("📤 Sending audio to backend");

                    const blob = new Blob(audioChunks, { type: "audio/webm" });

                    const formData = new FormData();
                    formData.append("audio", blob, "recording.webm");

                    const response = await fetch("/predict", {
                        method: "POST",
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error("Server error");
                    }

                    const data = await response.json();

                    console.log("✅ Response:", data);

                    // 🎯 REAL OUTPUT
                    resultText.innerText = data.label;
                    confidenceText.innerText = `Confidence: ${data.confidence}%`;

                    statusText.innerText = "Done ✅";
                    loader.style.display = "none";

                } catch (error) {
                    console.error("❌ Prediction Error:", error);

                    statusText.innerText = "Error ❌";
                    resultText.innerText = "Something went wrong";
                    loader.style.display = "none";
                }
            };
        }

    } catch (error) {
        console.error("❌ Mic Error:", error);
        statusText.innerText = "Mic permission denied ❌";
    }
};

// 🌙 DARK MODE
themeBtn.onclick = () => {
    document.body.classList.toggle("dark");
};