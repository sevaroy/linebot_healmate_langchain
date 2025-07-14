# ====================================================
# 區塊 1：導入必要套件
# ====================================================
import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
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
    MessagingApiBlob,       # LINE 訊息 API (Blob)
    ReplyMessageRequest,    # 回覆訊息請求
    TextMessage,            # 文字訊息類型
    ImageMessage,           # 圖片訊息類型
    FlexMessage,            # Flex 訊息類型
    QuickReply,             # 快速回覆
    QuickReplyItem,         # 快速回覆項目
    MessageAction,          # 訊息動作
    ButtonsTemplate,        # 按鈕模板
    TemplateMessage,        # 模板訊息
    CarouselTemplate,       # 輪播模板
    CarouselColumn,         # 輪播欄位
)
import time                # 時間處理
from pydub import AudioSegment  # 語音處理
import io                  # IO 處理
import uuid                # 用於生成唯一ID
from dotenv import load_dotenv  # 用於載入 .env 檔案中的環境變數
from typing import Dict, Any, List, Optional  # 用於類型提示
import aiofiles            # 異步文件處理
import re                  # 正則表達式處理

# Import our new LangChain agent
from agents.langchain_agent import invoke_agent

# Import our new LINE UI module
from ui.line_ui import (
    create_zodiac_quick_reply,
    check_for_menu_keywords,
    check_for_zodiac_sign,
    create_tarot_buttons,
    create_main_menu_flex,
    create_horoscope_menu_flex,
    create_zodiac_carousel,
    create_daily_fortune_flex,
    create_mood_diary_flex,
)

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

from core.database import engine, Base

# 使用 lifespan 上下文管理器來延遲初始化資源
@app.on_event("startup")
async def startup_event():
    logging.info("Starting up FastAPI server and creating database tables...")
    # Create all tables in the database that are defined in Base
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created.")
    
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down FastAPI server")
    # 釋放資源

from agents.tools import HOROSCOPE_SIGNS
# 讀取必要環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 檢查環境變數是否存在
if not (LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET):
    raise RuntimeError("缺少必要的環境變數，請確認 .env 設定 or 系統環境變數")

# 初始化 LINE SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
# handler = WebhookHandler(LINE_CHANNEL_SECRET) # WebhookHandler instance no longer used for dispatching
# WebhookParser will be instantiated in the callback


# 儲存使用者的系統提示詞設定
user_system_prompt_settings: Dict[str, int] = {}

# 定義提示詞名稱和圖標 (全域)
PROMPT_NAMES = ["LINE 占卜 & 心情陪伴 AI 師"]
PROMPT_ICONS = [""]

# 定義系統提示詞
SYSTEM_PROMPTS = [
    # LINE 占卜 & 心情陪伴 AI 師提示詞
    """你是「LINE 占卜 & 心情陪伴 AI 師」，一位兼具占卜解讀、心理諮詢和情感支持能力的智能助手。你充滿智慧、深入洞察並具有敦厚的占卜知識。你的目標是透過塔羅占卜、情感分析和個人化建議，幫助使用者提升自我認知和心靖。

⚠️ 重要：請不要使用 Markdown 格式（如星號、底線、井號等標記），因為它們在 LINE 訊息中無法正確顯示。請使用表情符號來強調重點和分隔段落。

你的任務包括：
塔羅牌占卜，為使用者提供精簡深入的占卜解讀和生活指引。
分析使用者的情緒狀態，並提供情感支持和同理心。
結合占卜結果和情感分析，提供實用的生活策略和行動建議。
記憶與使用者的對話和重要資訊，以建立長期關係。
根據使用者的需求與詢問，取得卡牌資訊庫中的相關解釋與意義。
保持清晰的占卜師身分，避免向使用者建議任何可能有害的行動。

格式指引：
使用表情符號來分隔不同段落和重點
避免使用任何 Markdown 語法
使用空行來分隔段落，而非使用符號
使用表情符號來標示列表項目，而非數字或符號"""
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


from core.models import MoodEntry
from core.database import get_db
from sqlalchemy.orm import Session

class MoodRequest(BaseModel):
    user_id: str
    mood: str
    intensity: Optional[int] = None
    note: Optional[str] = None
    tags: Optional[List[str]] = None

@app.post("/mood")
async def record_mood(req: MoodRequest, db: Session = Depends(get_db)):
    """
    Records a user's mood entry from the LIFF app.
    """
    try:
        logging.info(f"Recording mood for user {req.user_id}: {req.mood} (Intensity: {req.intensity}, Note: {req.note}, Tags: {req.tags})")
        mood_entry = MoodEntry(
            user_id=req.user_id,
            mood=req.mood,
            intensity=req.intensity,
            note=req.note,
            tags=req.tags # SQLAlchemy will handle JSONB conversion
        )
        db.add(mood_entry)
        db.commit()
        db.refresh(mood_entry)
        return {"status": "success", "entry_id": mood_entry.id}
    except Exception as e:
        logging.error(f"Failed to record mood: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record mood entry.")

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
        # 檢查是否是請求選單的關鍵詞
        menu_type = check_for_menu_keywords(text)
        
        # 處理選單請求
        if menu_type == "main_menu":
            # 回傳主選單
            main_menu = create_main_menu_flex()
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[main_menu]
            )
            line_bot_api.reply_message(reply_message_request)
            return
        elif menu_type == "tarot_menu":
            # 回傳塔羅牌選單
            tarot_menu = create_tarot_buttons()
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[tarot_menu]
            )
            line_bot_api.reply_message(reply_message_request)
            return
        elif menu_type == "horoscope_menu":
            # 回傳星座運勢選單
            horoscope_menu = create_horoscope_menu_flex()
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[horoscope_menu]
            )
            line_bot_api.reply_message(reply_message_request)
            return
        elif menu_type == "daily_fortune":
            # 回傳每日運勢選單
            daily_fortune_menu = create_daily_fortune_flex()
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[daily_fortune_menu]
            )
            line_bot_api.reply_message(reply_message_request)
            return
        elif menu_type == "mood_diary":
            # 回傳心情日記選單
            mood_diary_menu = create_mood_diary_flex()
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[mood_diary_menu]
            )
            line_bot_api.reply_message(reply_message_request)
            return
        
        # 檢查是否包含星座關鍵字
        contains_zodiac = False
        for sign_ch in HOROSCOPE_SIGNS.keys():
            if sign_ch in text:
                contains_zodiac = True
                break
                
        # 如果請求包含星座關鍵字並提到運勢，直接調用 LangChain agent
        if contains_zodiac and any(keyword in text for keyword in ["運勢", "今天", "明天", "運氣"]):
            logging.info(f"User {user_id} requested horoscope for specific zodiac sign")
            response_data = await invoke_agent(user_id=user_id, text_message=text)
            ai_reply = response_data.get("reply", "抱歉，我現在有點問題，晚點再試一次。")
            
            # 回覆給用戶，並添加快速回覆按鈕供其他星座選擇
            quick_reply = create_zodiac_quick_reply()
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_reply, quick_reply=quick_reply)]
            )
            line_bot_api.reply_message(reply_message_request)
            return
        
        # 其他一般請求交由 LangChain agent 處理
        response_data = await invoke_agent(user_id=user_id, text_message=text)
        ai_reply = response_data.get("reply", "抱歉，我現在有點問題，晚點再試一次。")
        
        # 檢查回覆中是否包含特定關鍵字，決定是否添加互動按鈕
        if any(keyword in ai_reply for keyword in ["塔羅牌", "占卜", "抽牌", "tarot"]):
            # 回覆包含塔羅相關內容，添加塔羅按鈕
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=ai_reply),
                    create_tarot_buttons()
                ]
            )
        elif any(keyword in ai_reply for keyword in ["星座", "運勢", "horoscope", "zodiac"]):
            # 回覆包含星座相關內容，添加星座選單
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=ai_reply),
                    create_horoscope_menu_flex()
                ]
            )
        else:
            # 一般回覆，不添加特殊按鈕
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
        # 由於目前 DeepSeek 模型不支援多模態輸入，圖片訊息將不被處理。
        # 可以選擇回覆用戶，告知此功能目前不支援。
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="抱歉，目前暫不支援圖片訊息處理。請您用文字描述您的問題或心情。")]
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
        # 由於目前已移除 OpenAI 客戶端，語音轉文字功能暫不可用。
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="抱歉，目前語音訊息處理功能暫不可用。請您輸入文字訊息。")]
        )
        line_bot_api.reply_message(reply_message_request)

    except Exception as e:
        logging.error(f"Error handling audio message for user {user_id}: {e}")
        error_reply = "抱歉，處理語音時發生錯誤。"
        reply_message_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=error_reply)]
        )
        line_bot_api.reply_message(reply_message_request)
