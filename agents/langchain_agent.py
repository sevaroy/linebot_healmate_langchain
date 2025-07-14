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

from functools import partial
from langchain.tools import Tool

from .tools import strategy_tool, tarot_reading_tool, emotion_analysis_tool, random_tarot_reading_tool, horoscope_tool, knowledge_base_tool, _run_mood_history_tool

# --- Agent Initialization ---

# 1. Define the base tools the agent can use (without user-specific context)
base_tools = [strategy_tool, tarot_reading_tool, emotion_analysis_tool, random_tarot_reading_tool, horoscope_tool, knowledge_base_tool]

# The mood_history_tool will be created dynamically per user request.

# 2. 獲取環境變數
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 3. 根據提供商選擇語言模型
def get_llm() -> BaseChatModel:
    """根據環境變數配置選擇 LLM 提供商"""
    if not DEEPSEEK_API_KEY:
        logging.error("DeepSeek API Key not provided. Cannot initialize DeepSeek LLM.")
        raise ValueError("DEEPSEEK_API_KEY is required for DeepSeek LLM.")
        
    logging.info("Using DeepSeek LLM API v3")
    return ChatDeepSeek(
        api_key=DEEPSEEK_API_KEY,
        model="deepseek-chat",  # 使用 DeepSeek Chat 模型
        temperature=0.7,
        streaming=True
    )

# 初始化 LLM
llm = get_llm()

# 3. Define the System Prompt
# This prompt is crucial for the agent's behavior. It tells the LLM how to act.
AGENT_SYSTEM_PROMPT = """你是一個名為「HealMate」的AI助理，是一個充滿同理心、智慧和溫暖的陪伴者。
你的主要目標是幫助用戶探索他們的感受、找到方向，並提供支持。

**個人化能力**: 你可以記住與使用者的對話。在提供建議前，你可以使用 `MoodHistoryChecker` 工具來查詢使用者的近期心情，以便提供更貼心、更有脈絡的回應。

你可以使用以下工具來幫助你：
- **StrategyAdvisor**: 當用戶需要具體建議或行動步驟時使用。
- **TarotReader**: 當用戶想針對「特定問題」進行占卜，尋找與問題最相關的牌卡時使用。它會從牌庫中檢索最匹配的牌。
- **RandomTarotReader**: 當用戶想要「隨機抽牌」、算「每日運勢」或尋求一個隨機指引時使用。它會模擬真實的抽牌過程。
- **HoroscopeProvider**: 當用戶想要查詢特定星座的今日運勢時使用。如果用戶提到「白羊座」、「金牛座」等星座名稱並想了解運勢，就用這個工具。
- **EmotionAnalyzer**: 當你想更深入了解用戶的情緒狀態時，可以在內部使用此工具來輔助你做決策。
- **MoodHistoryChecker**: 在與使用者互動一段時間後，或當使用者提到「最近心情不好」等模糊的描述時，使用此工具來查詢他們最近的心情紀錄。這有助於你了解他們的長期情緒狀態。

你的行為準則：
1.  **優先使用工具**：根據用戶的意圖，優先選擇最合適的工具來回應。不要自己編造答案，除非沒有工具可用。
2.  **善用歷史紀錄**：在回應前，先考慮使用 `MoodHistoryChecker` 來檢查使用者的心情歷史，讓你的回應更具個人化和同理心。
3.  **自然地對話**：不要生硬地說「我將使用XX工具」。而是將工具的輸出自然地融入你的對話中。
4.  **富有同理心**：永遠保持溫暖和理解的語氣。在給予建議或占卜結果之前，先表示你理解用戶的感受。
5.  **處理閒聊**：如果用戶只是閒聊或問候，不需要使用工具，直接以你「HealMate」的身份自然回應即可。
6.  **結合多個工具**：如果情況複雜，你可以依序使用多個工具。例如，先用 `MoodHistoryChecker` 了解歷史情緒，再用 `EmotionAnalyzer` 分析當前訊息，最後用 `StrategyAdvisor` 提供建議。
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
# Global dictionary to store memory for each user
user_memories: Dict[str, ConversationBufferWindowMemory] = {}

# 5. Create the Agent
# This binds the LLM, prompt, and tools together.
# agent = create_openai_tools_agent(llm, tools, prompt) # This will be created dynamically per user

# 6. Create the Agent Executor
# This is the runtime for the agent. It adds the memory and handles the execution loop.
# agent_executor = AgentExecutor( # This will be created dynamically per user
#     agent=agent,
#     tools=tools,
#     memory=memory,
#     verbose=True,  # Set to True for debugging to see the agent's thoughts
#     handle_parsing_errors=True, # Gracefully handle cases where the LLM output is not perfect
# )

# --- Main Invocation Function ---

async def invoke_agent(
    user_id: str,
    text_message: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Invoke the main agent with a user message (text and/or image) and return the response.
    This function now correctly handles memory and multimodal inputs as expected by LangChain.

    Args:
        user_id: The user's unique identifier.
        text_message: The text part of the user's message.
        image_base64: The base64-encoded image from the user.

    Returns:
        A dictionary containing the agent's reply.
    """
    
    # 1. Retrieve or create memory for the user
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferWindowMemory(
            k=5, memory_key="chat_history", return_messages=True
        )
    memory = user_memories[user_id]

    # 2. Construct the input for the agent
    # The input should be a dictionary, where the 'input' key holds the user's message.
    # For multimodal input, the value is a list of content blocks (text, image).
    input_content: List[Dict[str, Any]] = []
    
    # Add text content if it exists.
    if text_message:
        input_content.append({"type": "text", "text": text_message})
    # If only an image is provided, add a default prompt.
    elif image_base64 and not text_message:
        input_content.append({"type": "text", "text": "請根據這張圖片提供你的分析或見解。"})

    # Add image content if it exists.
    if image_base64:
        input_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
        })

    if not input_content:
        return {"reply": "請提供一些訊息讓我處理。"}

    # 3. Create a user-specific version of the mood history tool
    mood_history_tool_for_user = Tool(
        name="MoodHistoryChecker",
        description="""查詢特定使用者的最近心情紀錄。在你提供個人化建議或分析前，可以使用此工具來了解使用者的情緒脈絡。這個工具不需要任何輸入。""",
        func=None,
        coroutine=partial(_run_mood_history_tool, user_id=user_id)
    )

    # Combine base tools with the user-specific tool
    tools = base_tools + [mood_history_tool_for_user]

    # 4. Create the agent and executor for this specific invocation
    # This ensures that each user gets their own memory-equipped agent instance.
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )
    
    # 5. Invoke the agent with the correctly structured multimodal input
    # The AgentExecutor will handle memory automatically:
    # - It reads the history from `memory`.
    # - It adds the current `input` to the conversation.
    # - It executes the agent.
    # - It saves the new input and the AI's response back to `memory`.
    response = await agent_executor.ainvoke({"input": input_content})
    
    return {"reply": response.get("output", "抱歉，我現在遇到一點問題，暫時無法回應。")}

