from flask import Flask, render_template
from flask_socketio import SocketIO
from RealtimeSTT import AudioToTextRecorder
import logging

# 保持 Flask 和 SocketIO 物件在全域範圍，以便註冊路由和事件
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 只需要註冊這個 Flask 路由
@app.route('/realtime-stt')
def index():
    """提供主網頁"""
    return render_template('realtime_stt.html')

def main():
    """主執行函式，包含所有初始化和事件處理邏輯"""
    logging.basicConfig(level=logging.INFO)
    logging.info("Initializing application...")

    # --- RealtimeSTT 核心設定 ---

    # 將回呼函數定義在 main 內部，它可以存取 socketio
    def text_detected(text):
        """當辨識出文字時，透過 WebSocket 發送給前端"""
        logging.info(f"偵測到文字: {text}")
        # 使用 socketio 物件發送事件
        socketio.emit('transcription_update', {'text': text})

    # 將 recorder 的初始化移到 main 函式內部
    # 這是最關鍵的修正
    recorder = AudioToTextRecorder(
        model="base",
        language="zh",
        use_microphone=False,
        on_realtime_transcription_update=text_detected,
        on_realtime_transcription_stabilized=text_detected,

        # --- 徹底的修正方案 ---

        # 1. 啟用即時辨識功能 (最關鍵的修正)
        enable_realtime_transcription=True,

        # 2. 將 VAD 靈敏度調到最高
        #    根據文件，0 是最敏感的設定 (least aggressive / most sensitive)
        webrtc_sensitivity=0,

        # 3. 關閉額外的 VAD 過濾器，簡化判斷流程，讓靈敏度設定更直接生效
        faster_whisper_vad_filter=False
    )

    # --- SocketIO 事件處理 ---
    # 將事件處理器也定義在 main 內部，這樣它們可以存取 recorder
    
    @socketio.on('connect')
    def handle_connect():
        """處理客戶端連接事件"""
        logging.info('客戶端已連接')
        recorder.start()

    @socketio.on('disconnect')
    def handle_disconnect():
        """處理客戶端斷開事件"""
        logging.info('客戶端已斷開')
        recorder.stop()

    @socketio.on('audio_chunk')
    def handle_audio_chunk(chunk):
        """接收來自前端的音訊數據塊"""
        # 【請加入這一行來除錯】
        logging.info(f"收到音訊數據塊，大小為: {len(chunk) if chunk else 0} bytes")
        
        if chunk:
            recorder.feed_audio(chunk)

    # --- 啟動伺服器 ---
    logging.info("啟動 Flask-SocketIO 伺服器...")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)


# 使用這個 Python 標準寫法來保護您的主程式入口
if __name__ == '__main__':
    main()