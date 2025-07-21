# -*- coding: utf-8 -*-
""" my_flask_apis.py
Flask API for handling file uploads, text extraction, emotion highlighting, and sentiment analysis.
"""
import os
import json
import docx
import PyPDF2
import whisper
import tempfile
from openai import OpenAI
from datetime import datetime
from emotion_highlighter import EmotionHighlighter

import logging
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from RealtimeSTT import AudioToTextRecorder

# from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError
# from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 替換成你自己的 LINE Channel Access Token 和 Secret
LINE_CHANNEL_ACCESS_TOKEN = "kFtlIYzj4y2GdZ6f097lKqR8+xKLMCE63CozPyVbu1kemEdUTsSoqixAuIse4V7aiUKHQMpjygskjlO6GKiWP/rSXyWECrCEpegkPS0fmbDkn0YY2pHk/TeHFExWo3gLop8eQeoe+W0rjRHf7N4vDwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "c9d708cbd39678585490fc488b00c87a"

# line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
# handler = WebhookHandler(LINE_CHANNEL_SECRET)


highlighter = EmotionHighlighter()

# 初始化 OpenAI 客戶端，設定 API 金鑰和 OpenRouter 的 base_url
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
)

app = Flask(__name__)

model = whisper.load_model("large-v3", device="cuda")

def extract_text_from_file(file):
    """從不同類型的文件中提取文本內容"""
    filename = file.filename.lower()

    # 創建臨時文件
    temp = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp.name)
    temp.close()

    text = ""
    try:
        if filename.endswith(".txt"):
            with open(temp.name, "r", encoding="utf-8") as f:
                text = f.read()

        elif filename.endswith(".docx"):
            doc = docx.Document(temp.name)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

        elif filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(temp.name)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() + "\n"

        else:
            text = "不支援的檔案格式。請上傳 .txt, .docx 或 .pdf 檔案。"

    except Exception as e:
        text = f"讀取檔案時發生錯誤: {str(e)}"

    finally:
        # 刪除臨時文件
        if os.path.exists(temp.name):
            os.unlink(temp.name)

    return text

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/webhook-test", methods=["POST"])
# def webhook_test():
#     # 取得 X-Line-Signature header 簽名
#     signature = request.headers["X-Line-Signature"]

#     # 取得 request body 內容
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         app.logger.warning("Invalid signature. Check your channel access token/secret.")
#         return "Invalid signature", 400

#     return "OK", 200

# @handler.add(MessageEvent, message=TextMessage)
# def handle_text_message(event):
#     user_message = event.message.text
#     reply_text = f"你說的是：{user_message}"
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=reply_text)
#     )


@app.route("/uploadfile", methods=["GET", "POST"])
def upload_file():
    original_content = ""
    marked_content = ""
    marked_content2 = ""
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file.filename != "":
            original_content = extract_text_from_file(file)
            try:
                response = client.chat.completions.create(
                    model="meta-llama/llama-3.3-70b-instruct:free",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "你現在是一個功能強大的情緒標記工具，你的任務是幫我標記文字中帶有情緒或是動作的詞語，"
                                "並將原文字置換為=>原文字[情緒(喜悅、厭惡、悲傷、恐懼、驚訝、憤怒...etc)]。"
                                "你只需要回覆標記後的文字，不需要其他的說明或是任何的額外內容。"
                                '例如: 我很開心 => "我很開心"[喜悅]。'
                                '例如: "不好了不好了"[恐懼]！司馬懿帶著十五萬大軍，正殺過來了！！'
                            ),
                        },
                        {
                            "role": "user",
                            "content": original_content,  # 請確保 original_content 已定義並包含您要分析的文字
                        },
                    ],
                    stream=False,
                )
                marked_content = response.choices[0].message.content
                marked_content2 = highlighter.highlight(marked_content)

                # 將 response 儲存為 JSON 檔案
                try:
                    # 建立 logs 資料夾（若不存在）
                    os.makedirs("logs", exist_ok=True)

                    # 產生時間戳檔名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_filename = f"logs/llm_response_{timestamp}.json"

                    # 把整個 response 儲存下來（會自動轉成 dict）
                    with open(log_filename, "w", encoding="utf-8") as f:
                        f.write(response.model_dump_json(indent=2))
                except Exception as log_error:
                    print(
                        f"[Log Save Error] 儲存 response JSON 失敗: {str(log_error)}"
                    )
            except Exception as e:
                marked_content = f"呼叫情緒標記API時發生錯誤: {str(e)}"

    return render_template(
        "upload.html", original_content=original_content, marked_content=marked_content, marked_content2=marked_content2
    )

@app.route("/record")
def record_page():
    return render_template("record.html")

@app.route("/stt", methods=["POST"])
def stt():
    print(request.files["file"])
    audio = request.files["file"]
    file_path = f"./temp_{audio.filename}.m4a"
    print(file_path)
    audio.save(file_path)

    result = model.transcribe(file_path, initial_prompt="以下是中文語音:")
    # os.remove(file_path)

    return jsonify({"text": result["text"]})
    # return jsonify({"test": "success"})



if __name__ == "__main__":
    app.run(app, port=5000)
