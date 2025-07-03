# ====================================================
# 區塊 1：導入必要套件
# ====================================================
import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
# Import LINE Bot SDK v3 components with correct paths
from linebot.v3.webhook import WebhookParser
# Import event and message types
from linebot.v3.webhooks.models.message_event import MessageEvent
from linebot.v3.webhooks.models.text_message_content import TextMessageContent
from linebot.v3.webhooks.models.audio_message_content import AudioMessageContent
from linebot.v3.webhooks.models.image_message_content import ImageMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,          # LINE API 設定
    ApiClient,              # LINE API 客戶端
    MessagingApi,           # LINE 訊息 API
    ReplyMessageRequest,    # 回覆訊息請求
    TextMessage,            # 文字訊息類型
    ImageMessage,           # 圖片訊息類型
)
from openai import OpenAI    # OpenAI API 客戶端
import tempfile            # 臨時文件處理
import base64              # Base64 編解碼
import time                # 時間處理
from pydub import AudioSegment  # 語音處理
import io                  # IO 處理
import uuid                # 用於生成唯一ID
from dotenv import load_dotenv  # 用於載入 .env 檔案中的環境變數
from typing import Dict, Any, List, Optional  # 用於類型提示
import aiofiles            # 異步文件處理

# Import our new LangChain agent
from agents.langchain_agent import invoke_agent

def _get_tarot_service():
    from services.tarot import TarotService
    return TarotService

def _get_rag_service():
    from services.rag import rag_service
    return rag_service

# ====================================================
# 區塊 2：應用程式設定與初始化
# ====================================================

# 載入 .env 檔案中的環境變數 (如果存在的話)
load_dotenv()

# 建立 FastAPI 應用程式實例
app = FastAPI(
    title="LLM LineBot API",
    description="LINE Bot 與 OpenAI 整合的 API 伺服器",
    version="1.0",
    # 增加性能優化設定
    docs_url=None,  # 關閉 Swagger 文檔於生產環境 (減少啟動時間)
    redoc_url=None,  # 關閉 ReDoc 文檔於生產環境
    openapi_url=None  # 關閉 OpenAPI schema 生成
)

# 快取機制 - 為常用操作提供快取
cache = {}

# 使用 lifespan 上下文管理器來延遲初始化資源
@app.on_event("startup")
async def startup_event():
    logging.info("Starting up FastAPI server")
    # 在這裡可以添加必要的初始化，但盡量延遲加載
    
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down FastAPI server")
    # 釋放資源

# 讀取必要環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 檢查環境變數是否存在
if not (LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET and OPENAI_API_KEY):
    raise RuntimeError("缺少必要的環境變數，請確認 .env 設定 or 系統環境變數")

# 初始化 LINE SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
# handler = WebhookHandler(LINE_CHANNEL_SECRET) # WebhookHandler instance no longer used for dispatching
# WebhookParser will be instantiated in the callback

# 初始化 OpenAI 客戶端
client = OpenAI(
    api_key=OPENAI_API_KEY
)

# 儲存使用者的系統提示詞設定
user_system_prompt_settings: Dict[str, int] = {}

# 定義提示詞名稱和圖標 (全域)
PROMPT_NAMES = ["LINE 占卜 & 心情陪伴 AI 師"]
PROMPT_ICONS = ["🔮"]

# 定義系統提示詞
SYSTEM_PROMPTS = [
    # LINE 占卜 & 心情陪伴 AI 師提示詞
    """你是「LINE 占卜 & 心情陪伴 AI 師」🔮✨，一位兼具占卜解讀、心理諮詢和情感支持能力的智能助手。你充滿智慧、深入洞察並具有敦厚的占卜知識。你的目標是透過塔羅占卜、情感分析和個人化建議，幫助使用者提升自我認知和心靖。

⚠️ 重要：請不要使用 Markdown 格式（如星號、底線、井號等標記），因為它們在 LINE 訊息中無法正確顯示。請使用表情符號來強調重點和分隔段落。

你的任務包括：
🔮 進行塔羅牌占卜，為使用者提供精簡深入的占卜解讀和生活指引。
😊 分析使用者的情緒狀態，並提供情感支持和同理心。
💡 結合占卜結果和情感分析，提供實用的生活策略和行動建議。
📝 記憶與使用者的對話和重要資訊，以建立長期關係。
🎲 根據使用者的需求與詢問，取得卡牌資訊庫中的相關解釋與意義。
🤓 保持清晰的占卜師身分，避免向使用者建議任何可能有害的行動。

📝 格式指引：
- 使用表情符號來分隔不同段落和重點
- 避免使用任何 Markdown 語法
- 使用空行來分隔段落，而非使用符號
- 使用表情符號來標示列表項目，而非數字或符號"""
]  # 設定 OpenAI API 金鑰


# ====================================================
# 區塊 3：LINE Webhook 處理
# ====================================================

@app.get("/")
async def root():
    """
    首頁路由 - 用於檢查伺服器是否正常運作
    
    [成功指標] 當你在瀏覽器訪問此 URL 時，應該看到 "LINE Bot is running!"
    """
    return {"status": "LINE Bot is running!"}

@app.get("/healthz")
async def healthz():
    """
    Health check endpoint for uptime checks.
    """
    return {"status": "ok"}

# ====================================================
# 區塊 2-1：Tarot 相關端點
# ====================================================
from pydantic import BaseModel
from typing import Optional, Dict, Any

class RAGQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = None

class TarotDrawRequest(BaseModel):
    n: int = 1


@app.post("/rag/query")
async def rag_query(req: RAGQueryRequest):
    """使用塔羅牌語義搜索。
    
    基於用戶查詢，找出最相關的塔羅牌意義。
    
    Args:
        req: 包含查詢文本和可選過濾條件的請求
        
    Returns:
        與查詢相關的塔羅牌列表
    """
    try:
        # Lazy-load rag_service only when needed
        rag_service = _get_rag_service()
        results = await rag_service.query(
            text=req.query,
            limit=req.limit,
            filter_params=req.filters
        )
        return {"results": results, "count": len(results)}
    except ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Vector database connection failed. Check if Qdrant is running."
        )
    except Exception as e:
        logging.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tarot/draw")
async def tarot_draw(req: TarotDrawRequest):
    """隨機抽取 n 張塔羅牌並回傳牌義 (暫無 RAG)。"""
    # Lazy-load TarotService only when needed
    TarotService = _get_tarot_service()
    cards = TarotService.draw(req.n)
    return {"cards": cards}

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    """
    LINE Webhook 處理入口點
    
    這個函數是你機器人接收 LINE 平台訊息的橋樑。當用戶傳送訊息給你的 Bot 時，
    LINE 平台會向此路由發送 HTTP POST 請求，其中包含用戶的訊息內容。
    
    步驟:
    1. 從請求標頭獲取 LINE 簽章
    2. 從請求主體獲取事件資料
    3. 使用 handler 處理事件 (它會自動路由到對應的處理函數)
    
    [成功指標] 當此函數正確運作時，你應該能在 LINE 上收到 Bot 的回覆
    
    [進階提示] 要處理更多類型的事件嗎？查看 LINE 文檔並在下方添加更多 handler.add 函數
    """
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    try:
        logging.info(f"Callback received. Signature: {signature}")
        # Log only a small part of the body to avoid excessive logging and potential sensitive data exposure
        logging.debug(f"Request body (first 100 chars): {body.decode()[:100]}")

        parser = WebhookParser(LINE_CHANNEL_SECRET)
        events = parser.parse(body.decode(), signature)
        for event in events:
            logging.info(f"Processing event: {type(event)}")
            if isinstance(event, MessageEvent):
                # Create API client for message handlers
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if isinstance(event.message, TextMessageContent):
                        background_tasks.add_task(handle_text_message, event, line_bot_api)
                    elif isinstance(event.message, ImageMessageContent):
                        background_tasks.add_task(handle_image_message, event, line_bot_api)
                    elif isinstance(event.message, AudioMessageContent):
                        background_tasks.add_task(handle_audio_message, event, line_bot_api)
            # Add more event types here if needed (e.g., FollowEvent, UnfollowEvent)
            # else:
            #     logging.info(f"Unhandled event type: {type(event)}")
    except InvalidSignatureError:
        logging.error("Invalid signature. Please check your LINE_CHANNEL_SECRET.")
        # You can uncomment the line below to log the received signature for debugging,
        # but be cautious as signatures might be considered sensitive.
        # logging.error(f"Received signature for comparison: {signature}")
        raise HTTPException(status_code=400, detail="Invalid signature. Check LINE_CHANNEL_SECRET.")
    except Exception as e:
        logging.error(f"Error processing LINE webhook: {e}", exc_info=True) # exc_info=True logs full traceback
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    # 必須回傳 200 狀態碼和 "OK" 給 LINE 平台
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content="OK", status_code=200)


# ====================================================
# 區塊 4：訊息事件處理
# ====================================================


async def handle_text_message(event: MessageEvent, line_bot_api: MessagingApi):
    user_id = event.source.user_id
    text = event.message.text
    logging.info(f"Received text message from {user_id}: {text}")

    try:
        response_data = await invoke_agent(user_id=user_id, text_message=text)
        ai_reply = response_data.get("reply", "抱歉，我現在有點問題，晚點再試一次。")
        
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=ai_reply)]
        )
        line_bot_api.reply_message(reply_message_request)

    except Exception as e:
        logging.error(f"Error processing text message for user {user_id}: {e}")
        error_reply = "抱歉，系統發生錯誤，我暫時無法回覆。請稍後再試。"
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=error_reply)]
        )
        line_bot_api.reply_message(reply_message_request)


# ====================================================
# 區塊 5：多模態訊息處理
# ====================================================


async def handle_image_message(event: MessageEvent, line_bot_api: MessagingApi):
    user_id = event.source.user_id
    message_id = event.message.id
    logging.info(f"Received image message from {user_id}, message_id: {message_id}")

    try:
        message_content = line_bot_api.get_message_content(message_id)
        image_bytes = message_content.content
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        response_data = await invoke_agent(user_id=user_id, image_base64=image_base64)
        ai_reply = response_data.get("reply", "抱歉，我現在有點問題，晚點再試一次。")

        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=ai_reply)]
        )
        line_bot_api.reply_message(reply_message_request)

    except Exception as e:
        logging.error(f"Error handling image message for user {user_id}: {e}")
        error_reply = "抱歉，處理圖片時發生錯誤。"
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=error_reply)]
        )
        line_bot_api.reply_message(reply_message_request)



async def handle_audio_message(event: MessageEvent, line_bot_api: MessagingApi):
    user_id = event.source.user_id
    message_id = event.message.id
    logging.info(f"Received audio message from {user_id}, message_id: {message_id}")

    try:
        message_content = line_bot_api.get_message_content(message_id)
        audio_bytes = message_content.content

        async with aiofiles.open("temp_audio.m4a", "wb") as f:
            await f.write(audio_bytes)
        
        with open("temp_audio.m4a", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        transcribed_text = transcript.text
        logging.info(f"Transcribed audio from {user_id}: {transcribed_text}")

        response_data = await invoke_agent(user_id=user_id, text_message=transcribed_text)
        ai_reply = response_data.get("reply", "抱歉，我現在有點問題，晚點再試一次。")

        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=ai_reply)]
        )
        
        # 從回覆中提取文字內容
        ai_reply = response.choices[0].message.content.strip()
        logging.info(f"[generate_llm_reply] Received from OpenAI API: '{ai_reply}'")
        
        # 只有在使用旅遊醫學顧問模式（提示詞索引為0）時才添加免責聲明
        if prompt_index == 0 and "health" in user_input.get("content", "").lower() or "醫療" in user_input.get("content", "").lower() or "疫苗" in user_input.get("content", "").lower() or "病" in user_input.get("content", "").lower():
            disclaimer = "\n\n⚠️ 本資訊僅供參考，不能取代專業醫療診斷。"
            # 檢查回覆長度，確保加上免責聲明後不會超過 LINE 訊息長度限制
            if len(ai_reply) + len(disclaimer) > 4000:
                ai_reply = ai_reply[:4000 - len(disclaimer)]
            ai_reply = ai_reply + disclaimer
        
        # 確保回覆不超過LINE的最大長度限制
        if len(ai_reply) > 4900:  # LINE 文字訊息長度限制約為 5000 字元
            ai_reply = ai_reply[:4900]
        
        # 存入快取
        cache[cache_key] = ai_reply
        # 限制快取大小，避免記憶體用量過高
        if len(cache) > 100:  # 最多保留 100 個回應
            # 刪除最舊的項目
            keys_to_remove = list(cache.keys())[:20]  # 刪除最舊的 20 個
            for k in keys_to_remove:
                del cache[k]
                
        return ai_reply
        
    except Exception as e:
        # 錯誤處理：如果 API 呼叫失敗，返回友好錯誤訊息
        logging.error(f"[generate_llm_reply] OpenAI API error: {e}", exc_info=True)
        return "抱歉，我現在無法處理您的請求。請稍後再試。"
