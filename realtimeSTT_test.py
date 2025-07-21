try:
    from RealtimeSTT import AudioToTextRecorder

    print("=" * 70)
    print("正在查詢您環境中 AudioToTextRecorder 的完整說明文件...")
    print("=" * 70)

    # 使用內建的 help() 函式來印出 AudioToTextRecorder 類別的完整說明文件
    # 內容會包含 __init__ 方法的所有可用參數
    help(AudioToTextRecorder)

    print("=" * 70)
    print("診斷結束。")
    print("請檢查上面輸出內容中 'Methods defined here:'")
    print("區塊下的 '__init__(self, ...)' 部分，找出與 VAD 相關的參數名稱。")
    print("=" * 70)

except ImportError as e:
    print(f"匯入時發生錯誤，請確認 RealtimeSTT 已正確安裝: {e}")
except Exception as e:
    print(f"發生未預期的錯誤: {e}")