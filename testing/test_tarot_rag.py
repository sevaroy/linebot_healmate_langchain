import asyncio
import os
from dotenv import load_dotenv

# It's important to load .env before importing modules that need it
load_dotenv()

# Add project root to the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.tools import _run_tarot_tool
from openai import AsyncOpenAI

async def check_openai_connection():
    """Performs a simple API call to check OpenAI connection."""
    print("\n--- 正在檢查 OpenAI 連線 ---")
    try:
        aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        await aclient.chat.completions.create(
            model="gpt-3.5-turbo",  # Use a faster model for the check
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
            timeout=20.0,  # Set a 20-second timeout
        )
        print("--- OpenAI 連線成功 ---")
        return True
    except Exception as e:
        print(f"--- OpenAI 連線失敗: {e} ---")
        return False

async def main():
    """Runs a test query through the tarot reading tool."""
    print("--- 測試塔羅牌 RAG 工具 ---")
    
    # Check for necessary environment variables
    required_vars = ["OPENAI_API_KEY", "QDRANT_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n錯誤：缺少必要的環境變數：{', '.join(missing_vars)}")
        print("請確保您的 .env 檔案已正確設定。")
        return

    # First, check the connection to OpenAI
    if not await check_openai_connection():
        print("\n由於 OpenAI 連線失敗，測試中止。")
        return

    query = "我最近的工作運勢如何？會不會有新的發展機會？"
    print(f"\n測試問題：{query}")
    print("\n正在執行塔羅牌工具，請稍候...")
    
    try:
        result = await _run_tarot_tool(query)
        print("\n--- 塔羅牌解讀結果 ---")
        print(result)
        print("\n-----------------------")
        print("\n將結果寫入 testing/test_output.log 以供驗證...")
        with open("testing/test_output.log", "w", encoding="utf-8") as f:
            f.write(result)
        print("寫入完成。")
    except Exception as e:
        print(f"\n執行時發生錯誤：{e}")

if __name__ == "__main__":
    asyncio.run(main())
