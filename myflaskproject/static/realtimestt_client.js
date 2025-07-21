document.addEventListener('DOMContentLoaded', () => {
    const socket = io("http://127.0.0.1:5000"); // 連接到您的 Flask 伺服器

    const recordButton = document.getElementById('recordButton');
    const statusDiv = document.getElementById('status');
    const transcriptTextarea = document.getElementById('transcript');

    let isRecording = false;
    let mediaRecorder;
    let stream;

    socket.on('connect', () => {
        statusDiv.textContent = '已連接到伺服器，請點擊按鈕開始。';
        console.log('Connected to server.');
    });

    socket.on('disconnect', () => {
        statusDiv.textContent = '與伺服器斷開連線。';
        console.log('Disconnected from server.');
        if (isRecording) {
            stopRecording();
        }
    });

    socket.on('transcription_update', (data) => {
        transcriptTextarea.value = data.text;
    });

    recordButton.addEventListener('click', () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    // 將音訊數據塊發送到後端
                    socket.emit('audio_chunk', event.data);
                }
            };

            mediaRecorder.onstart = () => {
                isRecording = true;
                recordButton.textContent = '停止錄音';
                statusDiv.textContent = '正在錄音...';
                console.log('Recording started.');
            };

            mediaRecorder.onstop = () => {
                isRecording = false;
                recordButton.textContent = '開始錄音';
                statusDiv.textContent = '錄音已停止。';
                console.log('Recording stopped.');
            };
            
            // 每 250 毫秒發送一次數據
            mediaRecorder.start(250);

        } catch (error) {
            console.error('無法獲取麥克風:', error);
            statusDiv.textContent = `錯誤: ${error.message}`;
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
        }
    }
});