import os
import wave
from pydub import AudioSegment

def check_and_convert_wav(input_path: str, output_path: str):
    """
    檢查 WAV 檔案的音訊格式，如果不是 16kHz/16-bit/單聲道，
    就進行轉換並儲存為新檔案。

    :param input_path: 輸入的 WAV 檔案路徑
    :param output_path: 轉換後輸出的 WAV 檔案路徑
    """
    # --- 1. 檢查輸入檔案是否存在 ---
    if not os.path.exists(input_path):
        print(f"錯誤：找不到輸入檔案 '{input_path}'")
        return

    # --- 2. 使用內建的 wave 模組檢查原始格式 ---
    try:
        with wave.open(input_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            
            # 將位元寬度從 bytes 轉換為 bits
            bit_depth = sampwidth * 8
            
            channel_str = "單聲道 (mono)" if n_channels == 1 else "立體聲 (stereo)" if n_channels == 2 else f"{n_channels} 聲道"

            print("-" * 30)
            print(f"檔案 '{os.path.basename(input_path)}' 的原始音訊格式：")
            print(f"  取樣率 (Sample Rate): {framerate} Hz")
            print(f"  位元深度 (Bit Depth): {bit_depth}-bit")
            print(f"  聲道數 (Channels): {n_channels} ({channel_str})")
            print("-" * 30)

            # --- 3. 判斷是否需要轉換 ---
            is_target_format = (framerate == 16000 and bit_depth == 16 and n_channels == 1)

            if is_target_format:
                print("✅ 檔案格式符合目標規格 (16000 Hz, 16-bit, 單聲道)，無需轉換。")
                return
            else:
                print("⚠️ 檔案格式不符，準備進行轉換...")

    except wave.Error as e:
        print(f"無法讀取 WAV 檔案標頭，可能檔案已損壞或非標準 WAV 格式: {e}")
        # 即使標頭讀取失敗，仍嘗試讓 pydub 處理
        print("將嘗試使用 pydub 直接進行轉換...")
    
    # --- 4. 使用 pydub 進行格式轉換 ---
    try:
        print("正在載入音訊檔案...")
        audio = AudioSegment.from_file(input_path)

        print("正在轉換取樣率至 16000 Hz...")
        audio = audio.set_frame_rate(16000)

        print("正在轉換為單聲道...")
        audio = audio.set_channels(1)
        
        # pydub 在匯出為 WAV 時，預設使用 16-bit，所以通常不需特別設定
        # set_sample_width() 也可以用來強制設定
        # audio = audio.set_sample_width(2) # 2 bytes = 16 bits

        print(f"正在匯出轉換後的檔案至 '{output_path}'...")
        audio.export(output_path, format="wav")
        
        print("\n🎉 轉換成功！")
        print(f"已將標準格式的音訊儲存至: {output_path}")

    except Exception as e:
        print(f"\n❌ 轉換過程中發生錯誤: {e}")
        print("請確保您已正確安裝 FFmpeg 並將其加入系統環境變數 Path 中。")


if __name__ == '__main__':
    print("--- WAV 音訊格式轉換工具 ---")
    input_file = input("請輸入來源 .wav 檔案的路徑: ")
    
    # 自動產生輸出檔案名稱
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_16k_mono.wav"
    
    print(f"轉換後的檔案將儲存為: {output_file}")
    
    check_and_convert_wav(input_file, output_file)