"""純情緒價值處理代理人

這個模組實現了一個專注於情緒陪伴和心理支持的LangChain代理人。
不使用RAG或向量資料庫，純粹透過對話記憶和情緒理解來提供價值。
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain_deepseek.chat_models import ChatDeepSeek

# 情緒分類和強度定義
EMOTION_CATEGORIES = {
    "positive": ["開心", "快樂", "興奮", "滿足", "感恩", "希望", "愛", "平靜"],
    "negative": ["難過", "憤怒", "焦慮", "恐懼", "失望", "孤單", "沮喪", "絕望"],
    "neutral": ["平常", "一般", "還好", "沒什麼", "普通"],
    "complex": ["矛盾", "複雜", "混亂", "不確定", "五味雜陳"]
}

class PureEmotionAgent:
    """純情緒價值處理代理人"""
    
    def __init__(self):
        """初始化代理人"""
        self.llm = self._init_llm()
        self.user_memories: Dict[str, ConversationBufferWindowMemory] = {}
        self.user_summaries: Dict[str, ConversationSummaryMemory] = {}
        
        # 建立處理鏈
        self.emotion_chain = self._build_emotion_analysis_chain()
        self.response_chain = self._build_response_chain()
        
    def _init_llm(self) -> ChatDeepSeek:
        """初始化語言模型"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")
            
        return ChatDeepSeek(
            api_key=api_key,
            model="deepseek-chat",
            temperature=0.8,  # 稍高的溫度讓回應更有人情味
            streaming=False
        )
    
    def _build_emotion_analysis_chain(self) -> RunnableSequence:
        """建立情緒分析鏈"""
        emotion_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位專業的心理情緒分析師。請分析用戶訊息中的情緒狀態。

請以以下JSON格式回覆：
{
    "primary_emotion": "主要情緒",
    "intensity": 情緒強度(1-10),
    "secondary_emotions": ["次要情緒1", "次要情緒2"],
    "emotion_category": "positive/negative/neutral/complex",
    "keywords": ["關鍵情緒詞彙"],
    "context": "情緒背景簡述"
}

情緒分類參考：
正面：開心、快樂、興奮、滿足、感恩、希望、愛、平靜
負面：難過、憤怒、焦慮、恐懼、失望、孤單、沮喪、絕望
中性：平常、一般、還好、沒什麼、普通
複雜：矛盾、複雜、混亂、不確定、五味雜陳"""),
            ("human", "{message}")
        ])
        
        return emotion_prompt | self.llm | StrOutputParser()
    
    def _build_response_chain(self) -> RunnableSequence:
        """建立回應生成鏈"""
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是「情緒陪伴師」，一位溫暖、有同理心的AI陪伴者。

你的使命：
1. 🤗 提供情緒支持和理解
2. 💝 給予溫暖的陪伴和關懷  
3. 🌟 溫和地引導正向思考
4. 🎯 幫助用戶釐清情緒和想法
5. 🌈 在適當時機提供希望和力量

回應原則：
- 先同理再引導：先理解並驗證用戶的情緒
- 溫暖而真誠：使用溫暖的語調，避免說教
- 個人化：根據歷史對話調整回應風格
- 希望導向：在適當時候注入正向能量
- 尊重邊界：不強迫積極思考，尊重用戶當下狀態

請根據情緒分析結果和對話歷史，提供一個溫暖、有同理心的回應。"""),
            
            MessagesPlaceholder(variable_name="chat_history"),
            
            ("human", """用戶訊息：{message}

情緒分析：{emotion_analysis}

對話摘要：{conversation_summary}

請提供一個溫暖、有同理心的回應：""")
        ])
        
        return response_prompt | self.llm | StrOutputParser()
    
    def _get_or_create_memory(self, user_id: str) -> tuple:
        """獲取或創建用戶記憶"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferWindowMemory(
                k=8,  # 保留最近8輪對話
                memory_key="chat_history",
                return_messages=True
            )
            
        if user_id not in self.user_summaries:
            self.user_summaries[user_id] = ConversationSummaryMemory(
                llm=self.llm,
                memory_key="conversation_summary",
                return_messages=False
            )
            
        return self.user_memories[user_id], self.user_summaries[user_id]
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """處理用戶訊息並返回回應"""
        try:
            # 獲取記憶
            window_memory, summary_memory = self._get_or_create_memory(user_id)
            
            # 1. 情緒分析
            emotion_analysis = await self.emotion_chain.ainvoke({"message": message})
            logging.info(f"Emotion analysis for user {user_id}: {emotion_analysis}")
            
            # 2. 獲取對話歷史和摘要
            chat_history = window_memory.chat_memory.messages
            conversation_summary = summary_memory.buffer if hasattr(summary_memory, 'buffer') else "這是我們的第一次對話"
            
            # 3. 生成回應
            response = await self.response_chain.ainvoke({
                "message": message,
                "emotion_analysis": emotion_analysis,
                "chat_history": chat_history,
                "conversation_summary": conversation_summary
            })
            
            # 4. 更新記憶
            window_memory.save_context(
                {"input": message}, 
                {"output": response}
            )
            summary_memory.save_context(
                {"input": message}, 
                {"output": response}
            )
            
            return {
                "reply": response,
                "emotion_analysis": emotion_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error processing message for user {user_id}: {e}")
            return {
                "reply": "抱歉，我現在有點情緒化，需要一點時間整理思緒。能再跟我說一次嗎？ 💙",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_user_emotion_summary(self, user_id: str) -> Optional[str]:
        """獲取用戶情緒摘要"""
        if user_id in self.user_summaries:
            return getattr(self.user_summaries[user_id], 'buffer', None)
        return None
    
    def clear_user_memory(self, user_id: str) -> bool:
        """清除用戶記憶"""
        try:
            if user_id in self.user_memories:
                self.user_memories[user_id].clear()
            if user_id in self.user_summaries:
                self.user_summaries[user_id].clear()
            return True
        except Exception as e:
            logging.error(f"Error clearing memory for user {user_id}: {e}")
            return False

# 全域實例
emotion_agent = PureEmotionAgent()

async def invoke_emotion_agent(user_id: str, text_message: str) -> Dict[str, Any]:
    """調用情緒代理人的主要函數"""
    return await emotion_agent.process_message(user_id, text_message)