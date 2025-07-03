"""Defines a collection of tools for the LangChain agent.

This module refactors the original, separate agent classes (StrategyAgent, TarotAgent, etc.)
into a set of composable `Tool` objects that a central LangChain agent can use to handle user requests.
Each tool is self-contained and has a clear description, enabling the LLM to decide which tool to use for a given query.
"""

import os
from typing import Dict, Any, Optional, List

from langchain.tools import Tool
from langchain_community.embeddings import OllamaEmbeddings
from openai import AsyncOpenAI
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Load environment variables and initialize clients
load_dotenv()
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- RAG Setup for Tarot ---

# Initialize Qdrant client and OpenAI embeddings
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY"),
)
# Use the same embedding model as the one used to create the collection
embeddings = OllamaEmbeddings(model="nomic-embed-text")


# --- Tarot Reading Tool (RAG Version) ---

TAROT_SYSTEM_PROMPT = """你是一位專業的塔羅牌占卜師，你的任務是為用戶解讀抽到的塔羅牌。
請根據用戶的問題、抽到的牌（包括正逆位），提供一段溫暖、有啟發性且具體的解讀。
你的回應應該包含：
1. 對每張牌的牌義（正位或逆位）進行簡要解釋。
2. 綜合所有牌的意義，針對用戶的問題給出一個整體的分析和建議。
3. 使用溫和、鼓勵的語氣，給予用戶正向的引導。
"""

async def _run_tarot_tool(query: str) -> str:
    """The core logic for the tarot reading tool, using RAG with Qdrant."""
    try:
        # 1. Embed the user's query
        query_vector = embeddings.embed_query(query)

        # 2. Search for relevant cards in Qdrant
        search_results = qdrant_client.search(
            collection_name="tarot_cards_ollama_nomic-embed-text",
            query_vector=query_vector,
            limit=3,  # Retrieve the top 3 most relevant cards
            with_payload=True, # Include the card data in the result
        )

        if not search_results:
            return "抱歉，我沒有找到與您問題相關的塔羅牌。可以請您換個方式問嗎？"

        # 3. Prepare the context for the LLM
        retrieved_cards_info = []
        for result in search_results:
            payload = result.payload
            card_name = payload.get('name', '未知卡牌')
            orientation = '正位' if payload.get('orientation') == 'upright' else '逆位'
            meaning = payload.get('meaning', '無')
            retrieved_cards_info.append(f"- {card_name} ({orientation}): {meaning}")
        
        context_for_llm = "\n".join(retrieved_cards_info)

        prompt_to_llm = f"""用戶問題：{query}

根據您的問題，我為您抽到了以下幾張相關的牌：
{context_for_llm}

請基於以上牌義，為用戶提供一次完整、有深度的塔羅牌解讀。"""

        # 4. Call the LLM to generate the final interpretation
        response = await aclient.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": TAROT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_to_llm},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in Tarot Tool: {e}"

tarot_reading_tool = Tool(
    name="TarotReader",
    description="""當用戶想要算命、抽牌、占卜，或詢問關於運勢、未來、愛情、事業等需要神秘學指引的問題時使用。
    適用於包含「占卜」、「抽牌」、「算一下」、「運勢如何」等關鍵詞的請求。
    這個工具會為用戶抽三張塔羅牌並提供解讀。
    輸入應該是描述用戶想問的問題的句子。""",
    func=_run_tarot_tool,
    coroutine=_run_tarot_tool,
)


# --- Emotion Analysis Tool ---

EMOTION_SYSTEM_PROMPT = """你是一位專業的心理學家，專長是從文字中分析情緒。
你的任務是分析用戶的訊息，並以 JSON 格式回傳你的分析結果。
JSON 應包含以下三個欄位：
1. `emotion`: 字串，用戶最主要的情緒（例如：焦慮、開心、沮喪、憤怒、困惑等）。
2. `intensity`: 整數，情緒強度，範圍從 1 到 10。
3. `reason`: 字串，簡要說明你判斷該情緒的理由。

請直接回傳 JSON 物件，不要包含任何額外的解釋或 markdown 格式。"""

async def _run_emotion_tool(query: str) -> str:
    """The core logic for the emotion analysis tool."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": EMOTION_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            temperature=0,
            max_tokens=150,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in Emotion Tool: {e}"

emotion_analysis_tool = Tool(
    name="EmotionAnalyzer",
    description="""當需要深入了解用戶文字背後的情緒狀態時使用。
    這個工具可以分析一段文字，並回傳其中包含的主要情緒、強度和原因。
    它不直接回答用戶問題，而是為主代理提供決策參考。
    例如，在提供建議前，可以先用此工具分析用戶的情緒，以便給出更貼切的回應。
    輸入應該是需要被分析情緒的原始用戶訊息。""",
    func=_run_emotion_tool,
    coroutine=_run_emotion_tool,
)


# --- Strategy Tool ---

STRATEGY_SYSTEM_PROMPT = """你是一位專業的策略顧問，擅長為用戶提供實用且具體的行動建議。
你的任務是基於用戶的提問，提供具有針對性、可執行且易於理解的策略。
你的回應應該符合以下要求：
1. 簡短友善的開場語，顯示你理解了用戶的問題。
2. 一段中等長度的分析和策略建議，包含2-4條具體行動步驟。
3. 溫和有力的結束語，鼓勵用戶嘗試這些建議。
注意：
- 保持專業但溫暖的語調。
- 避免使用過於學術或技術性的詞彙。
- 建議需要具體且可行，而非空洞的勵志語。
"""

async def _run_strategy_tool(query: str) -> str:
    """The core logic for the strategy tool."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": STRATEGY_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in Strategy Tool: {e}"

strategy_tool = Tool(
    name="StrategyAdvisor",
    description="""當用戶需要針對特定問題或困境尋求建議、方法或具體行動步驟時使用。
    這個工具可以提供個人化、可行的策略。
    適用於詢問「我該怎麼辦？」、「有什麼建議嗎？」、「如何解決這個問題？」等需要指導和策略的情況。
    輸入應該是完整描述用戶問題的句子。""",
    func=_run_strategy_tool,  # For sync compatibility if needed
    coroutine=_run_strategy_tool, # For async execution
)
