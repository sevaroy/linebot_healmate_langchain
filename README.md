# 🤖 Advanced AI Agent LINE Bot (LangChain + GPT-4o)

這個專案讓你快速搭建一個基於 **LangChain** 的進階 AI 代理 (Agent) LINE Bot，不僅支援文字、圖片、語音等多模態輸入，更具備高度可擴展性，能輕鬆整合各種工具與外部 API。

## ✨ 功能亮點

- 🧠 **Agentic Architecture**：採用 LangChain Agent 架構，將複雜的邏輯、工具使用和記憶管理模組化，讓你的 Bot 更聰明、更強大。
- 🛠️ **工具使用 (Tool Using)**：內建塔羅牌抽牌工具，並提供清晰的擴充介面，讓你能輕鬆為 Agent 賦予新能力 (如天氣查詢、網路搜尋、資料庫存取等)。
- 🖼️ **GPT-4o 多模態**：整合 OpenAI 最新的 GPT-4o 模型，原生支援文字、圖片和語音的理解與生成。
- 🗣️ **異步處理**：核心服務採用 `async` 設計，提升在高併發場景下的處理效能。
- 📝 **對話記憶**：整合 LangChain Memory 模組，讓你的 Bot 能夠記住上下文，進行更流暢、更具個人化的對話。
- 🚀 **快速部署**：提供完整的部署指南，讓你從零開始，一步步將強大的 AI Agent 上線。

## 🎯 成功指標

1. **階段 1 (15分鐘)**：成功部署並收到 Agent 的基本文字回覆。
2. **階段 2 (30分鐘)**：透過 LINE Bot 成功呼叫 `/draw` 指令，並收到塔羅牌的圖文回覆。
3. **階段 3 (1小時)**：成功在 `agents/tools.py` 中加入一個你自己的新工具 (例如，一個回傳今天日期的工具)，並能透過對話觸發它。
4. **階段 4 (2小時)**：修改 `agents/langchain_agent.py` 中的 System Prompt，成功改變你的 Agent 的個性和行為模式。
5. **階段 5 (半天)**：為你的 Agent 整合一個外部 API (例如天氣資訊)，讓它具備與真實世界互動的能力。

## 🚀 快速啟動（手把手教學）

### 1. 準備環境

**A. 安裝 ffmpeg (若需處理語音訊息)**
```bash
# macOS: brew install ffmpeg
# Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg
# Windows: 前往 ffmpeg.org 下載並將 bin 目錄加入 PATH
```

**B. 下載專案、建立虛擬環境並安裝依賴**
```bash
git clone https://github.com/yourusername/langchain-agent-linebot.git
cd langchain-agent-linebot

# 建立並啟用虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 設定金鑰

```bash
cp .env.example .env
```
編輯 `.env` 文件，填入你的 `LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN` 和 `OPENAI_API_KEY`。

### 3. 啟動本地伺服器

```bash
uvicorn app:app --reload --port 8000
```

### 4. 暴露本地伺服器給外網

使用 ngrok 或 Cloudflare Tunnel 取得公開網址。
```bash
ngrok http 8000
```

### 5. 設定 LINE Webhook URL

前往 [LINE Developers Console](https://developers.line.biz/console/)，將 Webhook URL 設定為 `https://你的網址/callback`。

### 6. 發送訊息測試

掃描 QR Code 加入好友後，嘗試發送以下訊息：
- `你好` (測試基本對話)
- `我想抽一張塔羅牌` 或 `/draw` (測試工具使用)
- 傳送一張圖片 (測試圖片分析)
- 傳送一段語音 (測試語音辨識)

## 📁 檔案結構與說明

```
langchain-agent-linebot/
├─ agents/                  # 核心 Agent 邏輯
│  ├─ langchain_agent.py   # 主要 Agent 設定、Prompt 和執行流程
│  ├─ tools.py             # 定義 Agent 可使用的工具 (如塔羅牌)
│  ├─ strategy.py          # (可選) 定義複雜的策略或路由邏輯
│  └─ router.py            # (可選) 實現多代理路由
├─ app.py                   # FastAPI 主程式，負責接收 LINE Webhook 並呼叫 Agent
├─ services/                # 放置外部服務的客戶端 (如 Tarot API)
├─ requirements.txt         # 依賴套件清單
├─ .env.example             # 環境變數範例
└─ README.md                # 本文件
```

## 🔧 進階擴充指南

這個架構的核心在於擴充 Agent 的能力。主要有兩種方式：

### 1. 新增工具 (Tool)

這是最常見的擴充方式。打開 `agents/tools.py`：
1.  **定義新函數**：編寫一個 Python 函數，完成你想讓 Agent 做的事 (例如，`get_current_weather(city: str)`）。
2.  **加上 `@tool` 裝飾器**：在函數上方加上 `@tool`，並寫好 docstring 描述工具的功能、參數和回傳值。這個描述至關重要，因為 Agent 會根據它來決定何時使用此工具。
3.  **註冊工具**：將新工具函數加入到 `agents/langchain_agent.py` 的 `tools` 列表中。

### 2. 修改系統提示 (System Prompt)

打開 `agents/langchain_agent.py`，找到 `SYSTEM_PROMPT` 變數。你可以修改這裡的內容來：
-   改變 Agent 的**角色**和**個性** (例如，從專業顧問變為幽默的朋友)。
-   給予 Agent 更明確的**指令**或**限制** (例如，「絕對不能提供醫療建議」、「回覆必須使用繁體中文」)。
-   教導 Agent 如何**更好地使用工具**。

## 📚 學習資源

- [LangChain Agents 官方文檔](https://python.langchain.com/docs/modules/agents/)
- [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)
- [OpenAI API 參考](https://platform.openai.com/docs/api-reference)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)

---

🤝 有任何問題或建議，歡迎開 issue！
