"""測試純情緒處理代理人

這個腳本用於測試純情緒處理代理人的功能，
包括情緒識別、記憶功能和個性化回應等。
"""

import asyncio
import logging
from agents.pure_emotion_agent import invoke_emotion_agent

# 設置日誌
logging.basicConfig(level=logging.INFO)

async def test_emotion_scenarios():
    """測試不同情緒場景"""
    
    test_user_id = "test_user_001"
    
    # 測試場景
    test_scenarios = [
        "嗨，我是新用戶",
        "今天工作壓力好大，感覺快要撐不下去了",  
        "我覺得好孤單，朋友都不理我",
        "剛剛跟男朋友吵架了，心情很糟",
        "謝謝你的陪伴，感覺好一點了",
        "我想知道你還記得我之前說過的事情嗎？",
        "最近天氣不錯，心情也變好了",
        "但是想到明天要上班又開始焦慮"
    ]
    
    print("🤖 開始測試純情緒處理代理人...\n")
    print("=" * 60)
    
    for i, message in enumerate(test_scenarios, 1):
        print(f"\n📝 測試 {i}: {message}")
        print("-" * 40)
        
        try:
            response = await invoke_emotion_agent(test_user_id, message)
            
            print(f"🤗 機器人回應: {response.get('reply', 'No reply')}")
            
            # 如果有情緒分析結果，也顯示出來
            if 'emotion_analysis' in response:
                print(f"📊 情緒分析: {response['emotion_analysis']}")
                
        except Exception as e:
            print(f"❌ 錯誤: {e}")
        
        print("=" * 60)
        
        # 等待一下，避免請求太快
        await asyncio.sleep(1)
    
    print("\n✅ 測試完成！")

async def test_memory_function():
    """測試記憶功能"""
    
    print("\n🧠 測試記憶功能...")
    
    user_id = "memory_test_user"
    
    # 第一次對話
    print("\n第一次對話:")
    response1 = await invoke_emotion_agent(user_id, "我叫小明，今天很沮喪因為失業了")
    print(f"機器人: {response1.get('reply')}")
    
    await asyncio.sleep(1)
    
    # 第二次對話 - 測試是否記住名字和情況
    print("\n第二次對話:")
    response2 = await invoke_emotion_agent(user_id, "你還記得我是誰嗎？")
    print(f"機器人: {response2.get('reply')}")
    
    await asyncio.sleep(1)
    
    # 第三次對話 - 測試情緒延續性
    print("\n第三次對話:")
    response3 = await invoke_emotion_agent(user_id, "我今天心情好一點了")
    print(f"機器人: {response3.get('reply')}")

if __name__ == "__main__":
    # 運行基本測試
    asyncio.run(test_emotion_scenarios())
    
    # 運行記憶測試
    asyncio.run(test_memory_function())