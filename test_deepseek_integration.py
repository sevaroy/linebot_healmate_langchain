"""
DeepSeek LLM API 集成測試腳本

此腳本用於測試 DeepSeek LLM API 的整合情況，確保系統可以成功切換並使用 DeepSeek LLM API。
"""

import os
import logging
import asyncio
from dotenv import load_dotenv

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加載環境變數
load_dotenv()

# 確保環境變數已正確設定
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

logger.info(f"當前 LLM 提供商設置為: {LLM_PROVIDER}")
if LLM_PROVIDER == "deepseek" and not DEEPSEEK_API_KEY:
    logger.warning("LLM 提供商設置為 DeepSeek，但未提供 API Key！")

# 導入 Agent 函數
from agents.langchain_agent import get_llm, invoke_agent

async def test_llm_provider():
    """測試當前配置的 LLM 提供商"""
    logger.info("獲取 LLM 提供商...")
    llm = get_llm()
    logger.info(f"使用的 LLM 提供商: {llm.__class__.__name__}")
    
    return llm.__class__.__name__

async def test_llm_response():
    """測試 LLM 回應"""
    logger.info("測試 LLM 回應...")
    
    # 使用占卜相關問題測試
    test_prompt = "我今天運勢如何？"
    user_id = "test_user_001"
    
    try:
        logger.info(f"發送測試提示: '{test_prompt}'")
        response_data = await invoke_agent(user_id=user_id, text_message=test_prompt)
        
        ai_reply = response_data.get("reply", "")
        
        if ai_reply:
            logger.info("成功收到回應!")
            logger.info(f"回應前 50 個字符: {ai_reply[:50]}...")
            return True
        else:
            logger.error("未收到有效回應")
            return False
            
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {str(e)}")
        return False

async def run_tests():
    """執行所有測試"""
    logger.info("===== 開始 DeepSeek LLM API 整合測試 =====")
    
    # 測試 LLM 提供商
    llm_provider = await test_llm_provider()
    logger.info(f"LLM 提供商測試結果: {llm_provider}")
    
    # 測試 LLM 回應
    response_test = await test_llm_response()
    logger.info(f"LLM 回應測試結果: {'成功' if response_test else '失敗'}")
    
    logger.info("===== DeepSeek LLM API 整合測試完成 =====")

if __name__ == "__main__":
    asyncio.run(run_tests())
