"""Defines a collection of tools for the LangChain agent.

This module refactors the original, separate agent classes (StrategyAgent, TarotAgent, etc.)
into a set of composable `Tool` objects that a central LangChain agent can use to handle user requests.
Each tool is self-contained and has a clear description, enabling the LLM to decide which tool to use for a given query.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from langchain.tools import Tool
import httpx
from langchain_community.embeddings import OllamaEmbeddings
from openai import AsyncOpenAI
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Load environment variables and initialize clients
load_dotenv()
aclient = AsyncOpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

# --- RAG Setup for Tarot ---

# Initialize Qdrant client and OpenAI embeddings
# Make API key optional for local Docker deployments
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=qdrant_api_key if qdrant_api_key else None,
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
        print("[Tarot Tool] 步驟 1: 開始向量化查詢...")
        query_vector = embeddings.embed_query(query)
        print("[Tarot Tool] 步驟 2: 查詢已向量化，正在搜尋 Qdrant...")

        search_results = qdrant_client.search(
            collection_name="tarot_cards_ollama_nomic-embed-text",
            query_vector=query_vector,
            limit=3,  # Retrieve the top 3 most relevant cards
            with_payload=True, # Include the card data in the result
        )
        print(f"[Tarot Tool] 步驟 3: Qdrant 搜尋完成，找到 {len(search_results)} 個結果。")

        if not search_results:
            return "抱歉，我沒有找到與您問題相關的塔羅牌。可以請您換個方式問嗎？"

        print("[Tarot Tool] 步驟 4: 正在為 LLM 準備上下文...")
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
        print("[Tarot Tool] 步驟 5: 上下文已準備好，正在呼叫 LLM...")

        response = await aclient.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": TAROT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_to_llm},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        print("[Tarot Tool] 步驟 6: LLM 呼叫成功。")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Tarot Tool] 執行時發生錯誤: {e}")
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

class EmotionAnalysisResult(BaseModel):
    emotion: str = Field(..., description="用戶最主要的情緒（例如：焦慮、開心、沮喪、憤怒、困惑等）")
    intensity: int = Field(..., ge=1, le=10, description="情緒強度，範圍從 1 到 10")
    reason: str = Field(..., description="簡要說明判斷該情緒的理由")

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
        response = await aclient.chat.completions.create(
            model="deepseek-chat", # 使用 DeepSeek 模型
            messages=[
                {"role": "system", "content": EMOTION_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            temperature=0,
            max_tokens=150,
            response_format={"type": "json_object"},
        )
        json_output = response.choices[0].message.content.strip()
        try:
            parsed_result = EmotionAnalysisResult.parse_raw(json_output)
            return parsed_result.json() # 返回標準化的 JSON
        except Exception as e:
            logging.error(f"Failed to parse emotion analysis JSON: {e}. Raw output: {json_output}")
            return json.dumps({"error": "無法解析情緒分析結果", "raw_output": json_output})
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
- **重要提示：你提供的所有建議僅供參考，不能取代專業的醫療、法律、金融或心理諮詢。請避免提供任何可能對用戶造成傷害的建議。**"""

async def _run_strategy_tool(query: str) -> str:
    """The core logic for the strategy tool."""
    try:
        response = await aclient.chat.completions.create(
            model="deepseek-chat",
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


# --- New Random Tarot Reading Tool ---

import random
from data.tarot_data import TAROT_CARDS

RANDOM_TAROT_SYSTEM_PROMPT = """你是一位專業的塔羅牌占卜師，你的任務是為用戶解讀隨機抽到的塔羅牌。
請根據用戶的問題以及抽到的牌（包含其正逆位），提供一段溫暖、有啟發性且具體的解讀。
你的回應應該包含：
1. 清晰地告訴用戶他們抽到了哪張牌，以及是正位還是逆位。
2. 解釋這張牌在這個位置的牌義。
3. 結合用戶的問題，給出一個整體的分析和建議。
4. 使用溫和、鼓勵的語氣，給予用戶正向的引導。
"""

async def _run_random_tarot_tool(query: str) -> str:
    """
    Performs a random tarot card draw for the user and provides an interpretation.
    This tool simulates a real tarot reading by randomly selecting a card and its orientation.
    """
    try:
        print("[Random Tarot Tool] 步驟 1: 開始隨機抽牌...")
        
        # Randomly select one card from the list
        card = random.choice(TAROT_CARDS)
        
        # Randomly determine the orientation (upright or reversed)
        orientation = random.choice(['upright', 'reversed'])
        
        card_name = card['name']
        
        if orientation == 'upright':
            orientation_text = "正位"
            meaning = card['meaning_up']
        else:
            orientation_text = "逆位"
            meaning = card['meaning_rev']

        print(f"[Random Tarot Tool] 步驟 2: 抽牌完成。抽到的是 {card_name} ({orientation_text})。")

        prompt_to_llm = f"""用戶問題：{query}

我為你抽到的牌是：**{card_name} ({orientation_text})**

牌義：{meaning}

請基於以上資訊，為用戶提供一次完整、有深度的塔羅牌解讀。"""
        
        print("[Random Tarot Tool] 步驟 3: 正在呼叫 LLM 進行解讀...")
        response = await aclient.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": RANDOM_TAROT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_to_llm},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        print("[Random Tarot Tool] 步驟 4: LLM 解讀完成。")
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[Random Tarot Tool] 執行時發生錯誤: {e}")
        return f"Error in Random Tarot Tool: {e}"

random_tarot_reading_tool = Tool(
    name="RandomTarotReader",
    description="""當用戶想要進行一次傳統的隨機抽牌占卜時使用。適用於「幫我抽一張牌」、「算一下今天的運勢」、「隨機給我一些指引」等沒有指定要尋找特定答案的請求。
    這個工具會模擬真實的抽牌過程，隨機選擇一張塔羅牌及其正逆位，並提供解讀。
    輸入應該是描述用戶想問的問題的句子。""",
    func=_run_random_tarot_tool,
    coroutine=_run_random_tarot_tool,
)


# --- Horoscope Tool ---

from core.database import SessionLocal
from core.crud import get_mood_entries_by_user


# --- Mood History Tool ---

async def _run_mood_history_tool(user_id: str, query: str = "") -> str:
    """Fetches the user's recent mood history from the database and provides a summary."""
    if not user_id:
        return "無法查詢心情歷史，因為缺少 user_id。"
    
    db = SessionLocal()
    try:
        logging.info(f"[Mood History Tool] Fetching mood history summary for user {user_id}...")
        
        # Get a summary of recent moods
        mood_summary = get_mood_summary_by_user(db, user_id=user_id, days=7)
        
        # Get detailed recent entries (optional, for more context if needed by LLM)
        mood_entries = get_mood_entries_by_user(db, user_id=user_id, limit=3) # Get top 3 for detail
        detailed_entries = ""
        if mood_entries:
            detailed_entries = "\n最近的詳細紀錄：\n" + "\n".join(
                [f"- {entry.timestamp.strftime('%Y-%m-%d %H:%M')}: {entry.mood} (強度: {entry.intensity if entry.intensity else 'N/A'}, 筆記: {entry.note if entry.note else '無'}, 標籤: {entry.tags if entry.tags else '無'})" for entry in mood_entries]
            )

        response = f"{mood_summary}{detailed_entries}"
        logging.info(f"[Mood History Tool] Found history for user {user_id}:\n{response}")
        return response
        
    except Exception as e:
        logging.error(f"[Mood History Tool] Error fetching mood history for user {user_id}: {e}")
        return "查詢使用者心情歷史時發生錯誤。"
    finally:
        db.close()

mood_history_tool = Tool(
    name="MoodHistoryChecker",
    description="""查詢特定使用者的最近心情紀錄。在你提供個人化建議或分析前，可以使用此工具來了解使用者的情緒脈絡。這個工具不需要任何輸入。""",
    func=None, # This tool is async only
    coroutine=_run_mood_history_tool,
)


# --- Knowledge Base Tool (Wikipedia) ---

async def _run_knowledge_base_tool(query: str) -> str:
    """查詢維基百科摘要，回傳簡短解釋。"""
    try:
        url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{query.strip()}"
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("extract", "查無相關知識。")
            else:
                return "查無相關知識。"
    except Exception as e:
        return f"查詢知識時發生錯誤: {e}"

knowledge_base_tool = Tool(
    name="KnowledgeBaseTool",
    description="""當用戶詢問百科、知識、定義、歷史、地理等一般知識問題時使用。會查詢維基百科摘要，回傳簡短解釋。輸入應為條目名稱（如：塔羅牌、認知行為療法）。""",
    func=_run_knowledge_base_tool,
    coroutine=_run_knowledge_base_tool,
)


import httpx
import re

HOROSCOPE_SIGNS = {
    "白羊座": "Aries", "金牛座": "Taurus", "雙子座": "Gemini",
    "巨蟹座": "Cancer", "獅子座": "Leo", "處女座": "Virgo",
    "天秤座": "Libra", "天蠍座": "Scorpio", "射手座": "Sagittarius",
    "摩羯座": "Capricorn", "水瓶座": "Aquarius", "雙魚座": "Pisces",
    "aries": "Aries", "taurus": "Taurus", "gemini": "Gemini",
    "cancer": "Cancer", "leo": "Leo", "virgo": "Virgo",
    "libra": "Libra", "scorpio": "Scorpio", "sagittarius": "Sagittarius",
    "capricorn": "Capricorn", "aquarius": "Aquarius", "pisces": "Pisces"
}

async def _run_horoscope_tool(query: str) -> str:
    """Fetches the daily horoscope for a given zodiac sign."""
    print(f"[Horoscope Tool] 接收到查詢: {query}")
    sign_name_ch = None
    sign_name_en = None

    # Find which zodiac sign is mentioned in the query
    for sign_ch, sign_en in HOROSCOPE_SIGNS.items():
        if re.search(sign_ch, query, re.IGNORECASE):
            sign_name_ch = list(HOROSCOPE_SIGNS.keys())[list(HOROSCOPE_SIGNS.values()).index(sign_en)]
            sign_name_en = sign_en
            break

    if not sign_name_en:
        return "抱歉，請告訴我您想查詢哪個星座的運勢？例如：『獅子座今天運勢如何？』"

    print(f"[Horoscope Tool] 辨識到星座: {sign_name_ch} ({sign_name_en})")
    api_url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign_name_en}&day=TODAY"

    try:
        async with httpx.AsyncClient() as client:
            print(f"[Horoscope Tool] 正在呼叫 API: {api_url}")
            response = await client.get(api_url, timeout=10.0)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            print("[Horoscope Tool] API 呼叫成功，正在整理資料...")

            horoscope_data = data.get('data', {})
            prediction = horoscope_data.get('prediction', '暫無預測')

            formatted_response = f"以下是 {sign_name_ch} 今天的運勢分析：\n\n{prediction}"
            return formatted_response

    except httpx.RequestError as e:
        print(f"[Horoscope Tool] API 請求錯誤: {e}")
        return f"抱歉，查詢星座運勢時網路發生問題，請稍後再試。"
    except Exception as e:
        print(f"[Horoscope Tool] 發生未知錯誤: {e}")
        return f"抱歉，處理您的星座運勢請求時發生了未知的錯誤。"

horoscope_tool = Tool(
    name="HoroscopeProvider",
    description="""當用戶想要查詢特定星座的今日運勢時使用。適用於包含「星座」、「運勢」、「白羊座」、「獅子座」等關鍵詞的請求。
    這個工具會根據用戶提到的星座，提供今天的運勢分析。
    輸入應該是包含星座名稱的句子。""",
    func=_run_horoscope_tool,
    coroutine=_run_horoscope_tool,
)


