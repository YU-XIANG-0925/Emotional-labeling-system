from openai import OpenAI
import os

# ✅ 請填入你的 OpenRouter API Key
API_KEY = "your-openrouter-api-key"

# ✅ 建立 OpenAI 客戶端，使用 OpenRouter 的 endpoint
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)


def test_llm_response(input_text: str):
    try:
        print("🔍 測試傳送內容...\n")
        # response = client.responses.create(
        #     model="meta-llama/llama-3.3-70b-instruct:free",
        #     instructions=(
        #         "你現在是一個功能強大的情緒標記工具，你的任務是幫我標記文字中帶有情緒或是動作的詞語，"
        #         "並將原文字置換為=>原文字[情緒(喜悅、厭惡、悲傷、恐懼、驚訝、憤怒...etc)]。"
        #         "你只需要回覆標記後的文字，不需要其他的說明或是任何的額外內容。"
        #         '例如: 我很開心 => "我很開心"[喜悅]。'
        #         '例如: "不好了不好了"[恐懼]！司馬懿帶著十五萬大軍，正殺過來了！！'
        #     ),
        #     input=[{"role": "user", "content": input_text}],
        # )
        response = client.responses.create(
            model="gpt-4o",
            input= "請告訴我今天的天氣。"
        )
        
        print(response)
        print(response.output_text)
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")


if __name__ == "__main__":
    test_input = "他衝過來大喊：「快逃啊！」整座山開始搖晃。"
    test_llm_response(test_input)
