import os
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

def trim_audio_to_30s(input_path: str, output_path: str):
    """
    載入一個音訊檔案，擷取其前 30 秒，並儲存為新的 WAV 檔案。

    :param input_path: 輸入的音訊檔案路徑
    :param output_path: 裁切後輸出的 WAV 檔案路徑
    """
    # --- 1. 檢查輸入檔案是否存在 ---
    if not os.path.exists(input_path):
        print(f"❌ 錯誤：找不到輸入檔案 '{input_path}'")
        return

    try:
        # --- 2. 使用 pydub 載入音訊檔案 ---
        print(f"正在載入檔案: '{os.path.basename(input_path)}'...")
        audio = AudioSegment.from_file(input_path)
        print("檔案載入成功。")

        # --- 3. 進行裁切 ---
        # pydub 的時間單位是毫秒 (milliseconds)，所以 30 秒 = 30 * 1000 = 30000 毫秒
        duration_to_trim_ms = 30 * 1000

        print(f"正在擷取前 {duration_to_trim_ms / 1000} 秒的音訊...")
        
        # 使用類似 Python list 的切片語法來裁切音訊
        first_30_seconds_clip = audio[:duration_to_trim_ms]

        # --- 4. 匯出裁切後的音訊 ---
        print(f"正在儲存裁切後的檔案至 '{output_path}'...")
        # 匯出為 wav 格式
        first_30_seconds_clip.export(output_path, format="wav")
        
        print("\n🎉 裁切並儲存成功！")
        print(f"已將前 30 秒的音訊儲存至: {output_path}")

    except CouldntDecodeError:
        print(f"❌ 錯誤：無法解碼檔案 '{input_path}'。")
        print("請確認檔案格式是否受支援，以及 FFmpeg 是否已正確安裝並設定於環境變數中。")
    except Exception as e:
        print(f"\n❌ 處理過程中發生未預期的錯誤: {e}")


if __name__ == '__main__':
    print("--- 音訊檔案裁切工具 (擷取前 30 秒) ---")
    
    # --- 讓使用者輸入檔案 ---
    input_file = input("請輸入來源音訊檔案的路徑 (wav, mp3, etc.): ")
    
    # --- 自動產生輸出檔案名稱 ---
    # 根據使用者的要求，固定輸出檔名為 sample_30s.wav
    output_file = "sample_30s.wav"
    
    # 執行裁切函式
    trim_audio_to_30s(input_file, output_file)