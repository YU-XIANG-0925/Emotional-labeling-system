from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import whisper
import tempfile
import os
import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Whisper GPU 模型載入
model = whisper.load_model("large-v3", device="cuda")

@app.route("/record")
def record_page():
    return render_template("record.html")

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("audio_chunk")
def handle_audio_chunk(data):
    try:
        audio_data = base64.b64decode(data.split(",")[1])  # 去掉 data URI 前綴
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".webm").name

        with open(temp_path, "wb") as f:
            f.write(audio_data)

        result = model.transcribe(temp_path, initial_prompt="以下是中文語音:")
        text = result.get("text", "")

    except Exception as e:
        text = f"辨識失敗: {str(e)}"

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    emit("transcript", text)

if __name__ == "__main__":
    socketio.run(app, port=5001, debug=True)