"""Main LangChain Agent for the HealMate bot.

This module initializes a conversational agent that uses a set of tools to interact with the user.
The agent is responsible for understanding user intent, routing requests to the appropriate tool,
and generating a coherent, empathetic, and helpful response.

It leverages LangChain's agent framework, including tools, a language model, and memory,
to create a flexible and powerful conversational experience.
"""

import os
import logging
from typing import Dict, Any, Optional, List

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models.llms import BaseLLM
from langchain.memory import ConversationBufferWindowMemory

# 添加 DeepSeek LLM 支援
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_deepseek.chat_models import ChatDeepSeek

from .tools import strategy_tool, tarot_reading_tool, emotion_analysis_tool, random_tarot_reading_tool, horoscope_tool, knowledge_base_tool

# --- Agent Initialization ---

# 1. Define the tools the agent can use
tools = [strategy_tool, tarot_reading_tool, emotion_analysis_tool, random_tarot_reading_tool, horoscope_tool, knowledge_base_tool]

# 2. 獲取環境變數
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 3. 根據提供商選擇語言模型
def get_llm() -> BaseChatModel:
    """根據環境變數配置選擇 LLM 提供商"""
    if LLM_PROVIDER == "deepseek":
        if not DEEPSEEK_API_KEY:
            logging.warning("DeepSeek API Key not provided. Falling back to OpenAI.")
            return ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)
            
        logging.info("Using DeepSeek LLM API v3")
        return ChatDeepSeek(
            api_key=DEEPSEEK_API_KEY,
            model="deepseek-chat",  # 使用 DeepSeek Chat 模型
            temperature=0.7,
            streaming=True
        )
    else:  # default: openai
        logging.info("Using OpenAI API")
        return ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)

# 初始化 LLM
llm = get_llm()

# 3. Define the System Prompt
# This prompt is crucial for the agent's behavior. It tells the LLM how to act.
AGENT_SYSTEM_PROMPT = """你是一個名為「HealMate」的AI助理，是一個充滿同理心、智慧和溫暖的陪伴者。
你的主要目標是幫助用戶探索他們的感受、找到方向，並提供支持。

**多模態能力**: 你能理解用戶傳送的圖片。當用戶傳送圖片時，請結合圖片內容和文字進行分析和回應。

你可以使用以下工具來幫助你：
- **StrategyAdvisor**: 當用戶需要具體建議或行動步驟時使用。
- **TarotReader**: 當用戶想針對「特定問題」進行占卜，尋找與問題最相關的牌卡時使用。它會從牌庫中檢索最匹配的牌。
- **RandomTarotReader**: 當用戶想要「隨機抽牌」、算「每日運勢」或尋求一個隨機指引時使用。它會模擬真實的抽牌過程。
- **HoroscopeProvider**: 當用戶想要查詢特定星座的今日運勢時使用。如果用戶提到「白羊座」、「金牛座」等星座名稱並想了解運勢，就用這個工具。
- **EmotionAnalyzer**: 當你想更深入了解用戶的情緒狀態時，可以在內部使用此工具來輔助你做決策。

你的行為準則：
1.  **優先使用工具**：根據用戶的意圖，優先選擇最合適的工具來回應。不要自己編造答案，除非沒有工具可用。
2.  **自然地對話**：不要生硬地說「我將使用XX工具」。而是將工具的輸出自然地融入你的對話中。
3.  **富有同理心**：永遠保持溫暖和理解的語氣。在給予建議或占卜結果之前，先表示你理解用戶的感受。
4.  **處理閒聊**：如果用戶只是閒聊或問候，不需要使用工具，直接以你「HealMate」的身份自然回應即可。
5.  **結合多個工具**：如果情況複雜，你可以依序使用多個工具。例如，先用 EmotionAnalyzer 了解情緒，再用 StrategyAdvisor 提供建議。
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# 4. Define the Memory
# We use a windowed buffer to keep the last K interactions in memory.
memory = ConversationBufferWindowMemory(
    k=5, memory_key="chat_history", return_messages=True
)

# 5. Create the Agent
# This binds the LLM, prompt, and tools together.
agent = create_openai_tools_agent(llm, tools, prompt)

# 6. Create the Agent Executor
# This is the runtime for the agent. It adds the memory and handles the execution loop.
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,  # Set to True for debugging to see the agent's thoughts
    handle_parsing_errors=True, # Gracefully handle cases where the LLM output is not perfect
)

# --- Main Invocation Function ---

# 新增：根據 input_content 動態選擇 LLM
from langchain_openai import ChatOpenAI
from langchain_deepseek.chat_models import ChatDeepSeek

def get_llm_dynamic(input_content: list) -> BaseChatModel:
    has_image = any(item.get("type") == "image_url" for item in input_content)
    has_audio = any(item.get("type") == "audio_url" or item.get("type") == "audio_base64" for item in input_content)
    if has_image or has_audio:
        # 圖片或音訊用 gpt-4o
        return ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)
    else:
        # 純文字預設用 deepseek
        return ChatDeepSeek(api_key=DEEPSEEK_API_KEY, model="deepseek-chat", temperature=0.7, streaming=True)

async def invoke_agent(
    user_id: str,
    text_message: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Invoke the main agent with a user message (text and/or image) and return the response.

    Args:
        user_id: The user's unique identifier.
        text_message: The text part of the user's message.
        image_base64: The base64-encoded image from the user.

    Returns:
        A dictionary containing the agent's reply.
    """
    input_content: List[Dict[str, Any]] = []

    # Add text to input
    if image_base64 and not text_message:
        input_content.append({"type": "text", "text": "請根據這張圖片提供你的分析或見解。"})
    elif text_message:
        input_content.append({"type": "text", "text": text_message})
    # Add image to input
    if image_base64:
        input_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
        })
    if not input_content:
        return {"reply": "請提供一些訊息讓我處理。"}

    # 動態選擇 LLM 並建立 agent_executor
    llm_dynamic = get_llm_dynamic(input_content)
    agent = create_openai_tools_agent(llm_dynamic, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )
    response = await agent_executor.ainvoke({"input": input_content})
    return {"reply": response.get("output", "抱歉，我現在遇到一點問題，暫時無法回應。")}

