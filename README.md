# 🤖 HealMate AI 陪伴師

## ✨ 專案簡介

HealMate 是一個基於 LINE 平台的 AI 陪伴師，旨在透過塔羅占卜、情緒分析和個人化建議，提供使用者溫暖、智慧與支持。本專案採用現代化的技術棧，並經過近期的大幅優化，以提供更穩定、高效且具備記憶能力的互動體驗。

## 🚀 核心功能

*   **智慧對話代理**：整合 LangChain 與大型語言模型 (LLM)，實現多輪對話與意圖理解。
*   **塔羅牌占卜**：提供基於 RAG (Retrieval-Augmented Generation) 的精準塔羅牌解讀，以及隨機抽牌功能。
*   **情緒分析**：分析用戶訊息中的情緒，提供更具同理心的回應。
*   **個人化心情日記**：記錄用戶心情，AI 可根據歷史心情提供更貼心的建議。
*   **星座運勢查詢**：提供每日星座運勢。
*   **多模態支援**：支援圖片輸入，AI 可結合圖片內容進行分析。

## 🛠 技術棧 (更新)

*   **後端框架**: FastAPI
*   **AI 框架**: LangChain
*   **語言模型**: DeepSeek, GPT-4o (支援多模態)
*   **向量資料庫**: Qdrant
*   **關聯式資料庫**: PostgreSQL (用於心情日記等結構化數據)
*   **快取/訊息佇列**: Redis (基礎設施，未來可擴展)
*   **前端**: LINE LIFF (React + Vite)
*   **依賴管理**: `pip-tools` (Python), `npm` (Node.js)
*   **容器化**: Docker, Docker Compose

## ⚙️ 環境要求

*   Docker 及 Docker Compose
*   Node.js (用於前端開發，如果只用 Docker 可選)
*   Python 3.11+

## 🚀 快速開始 (全新簡化流程)

我們已將所有服務的啟動與管理統一至 Docker Compose。現在，你只需要幾個簡單的步驟即可啟動整個專案。

1.  **複製專案**：
    ```bash
    git clone https://github.com/your-repo/Linebot_healmate_langchain.git
    cd Linebot_healmate_langchain
    ```

2.  **設定環境變數**：
    複製 `.env.example` 為 `.env`，並填入必要的環境變數，例如 LINE Channel Access Token, LINE Channel Secret, OpenAI API Key 等。
    ```bash
    cp .env.example .env
    # 編輯 .env 檔案，填入你的 API Keys 和其他配置
    ```

3.  **啟動所有服務 (推薦)**：
    使用 Docker Compose 啟動後端 API、前端 LIFF 應用、Qdrant、Redis 和 PostgreSQL。
    ```bash
    docker-compose -f infra/docker-compose.yaml up --build -d
    ```
    *   `--build`: 首次運行或 Dockerfile 有變更時使用，會重新構建映像。
    *   `-d`: 在後台運行服務。

    服務啟動後，你可以訪問：
    *   **後端 API**: `http://localhost:8000`
    *   **前端 LIFF**: `http://localhost:5173`

4.  **停止所有服務**：
    ```bash
    docker-compose -f infra/docker-compose.yaml down
    ```

5.  **初始化塔羅牌數據 (重要)**：
    首次運行或數據更新時，你需要生成塔羅牌的嵌入向量並上傳到 Qdrant。請確保 Qdrant 服務已運行。
    ```bash
    # 使用 Ollama (需本地運行 Ollama 服務並下載模型，例如 nomic-embed-text)
    docker-compose -f infra/docker-compose.yaml exec backend python scripts/data_pipeline.py --embedder ollama --model nomic-embed-text

    # 或使用 OpenAI (需設定 OPENAI_API_KEY)
    # docker-compose -f infra/docker-compose.yaml exec backend python scripts/data_pipeline.py --embedder openai --model text-embedding-3-small
    ```
    *   `docker-compose exec backend`: 在 `backend` 服務容器內執行命令。
    *   你可以根據需求選擇不同的嵌入模型。

## 📂 專案結構 (更新)

```
.env                 # 環境變數配置 (從 .env.example 複製並修改)
app.py               # FastAPI 主應用程式入口
requirements.in      # Python 核心依賴定義 (用於 pip-tools)
requirements.txt     # Python 鎖定依賴 (由 pip-compile 生成)
Dockerfile.backend   # 後端服務 Dockerfile

├── agents/          # LangChain Agent 相關模組
│   ├── langchain_agent.py # Agent 核心邏輯與工具調度
│   └── tools.py           # Agent 可用的工具定義 (如塔羅、情緒分析、心情歷史)
├── core/            # 核心服務與資料庫相關
│   ├── database.py        # 資料庫連線與 Session 管理
│   ├── models.py          # SQLAlchemy 資料模型定義 (如 MoodEntry)
│   └── crud.py            # 資料庫操作 (Create, Read, Update, Delete)
├── data/            # 數據文件
│   ├── tarot_cards_processed.json # 處理後的塔羅牌數據
│   └── ...
├── infra/           # 基礎設施配置
│   └── docker-compose.yaml # Docker Compose 配置 (包含所有服務)
├── liff/            # LINE LIFF 前端應用
│   ├── src/               # React 原始碼
│   │   ├── components/    # React 組件 (如 MoodTracker.tsx)
│   │   └── ...
│   └── Dockerfile.frontend # 前端服務 Dockerfile
├── scripts/         # 自動化腳本
│   └── data_pipeline.py   # 統一的數據處理管線 (抓取、清洗、嵌入)
└── ui/              # LINE UI 相關工具
```

## 📈 優化與更新記錄 (由 Gemini AI 代理完成)

本次更新旨在大幅提升專案的穩定性、可維護性與功能性，解決了多個核心痛點。

### 1. 依賴管理現代化
*   **問題**：`requirements.txt` 與 `requirements_working.txt` 混亂，導致環境不一致。
*   **解決方案**：引入 `pip-tools`。現在僅維護 `requirements.in`，並由 `pip-compile` 自動生成鎖定版本的 `requirements.txt`，確保環境可重現。

### 2. 服務啟動與管理簡化
*   **問題**：多個手動編寫的 `.sh` 腳本用於啟動/停止前後端服務，重複且易錯。
*   **解決方案**：全面擁抱 Docker Compose。將後端 FastAPI 與前端 LIFF 應用納入 `infra/docker-compose.yaml` 管理，並為其創建專屬 `Dockerfile`。現在，只需 `docker-compose up --build -d` 即可啟動所有服務，`docker-compose down` 即可停止。
*   **影響**：刪除了 `deploy_local.sh`, `start_backend.sh`, `start_frontend.sh`, `stop_backend.sh`, `stop_frontend.sh`, `stop_local.sh` 等冗餘腳本。

### 3. 專案結構清理
*   **問題**：`liff/liff-app` 存在多餘的嵌套前端專案，且部署配置 (`netlify.toml`, `vercel.json`) 混淆。
*   **解決方案**：刪除 `liff/liff-app`，並統一前端部署配置，移除 `netlify.toml`。

### 4. 數據管線自動化與統一
*   **問題**：塔羅牌數據處理流程分散在多個獨立且重複的 Python 腳本中 (`fetch_tarot_sources.py`, `fix_tarot_json.py`, `validate_tarot_json.py`, `prepare_tarot_embeddings*.py`)，手動執行繁瑣且易錯。
*   **解決方案**：將所有數據處理邏輯整合至單一、可配置的 `scripts/data_pipeline.py`。該腳本支援選擇不同的嵌入模型 (OpenAI/Ollama)，並自動完成數據抓取、清洗、驗證、嵌入及上傳至 Qdrant 的全流程。
*   **影響**：刪除了所有舊的數據處理腳本。

### 5. AI Agent 記憶與個人化能力增強
*   **問題**：AI Agent 的對話記憶機制未被正確利用，且缺乏記錄用戶心情的能力，導致無法提供個人化服務。
*   **解決方案**：
    *   **修正 Agent 記憶**：修復 `agents/langchain_agent.py` 中 `AgentExecutor` 的記憶體處理邏輯，確保多模態輸入和對話歷史被正確傳遞和管理。
    *   **引入心情日記功能**：
        *   新增 PostgreSQL 資料庫整合，用於持久化儲存用戶心情數據。
        *   在後端 `app.py` 中新增 `/mood` API 端點，接收並儲存用戶心情。
        *   在 `agents/tools.py` 中新增 `MoodHistoryChecker` 工具，允許 Agent 查詢用戶歷史心情。
        *   更新 Agent 的系統提示詞，引導其利用心情歷史提供更貼心的回應。
        *   修改前端 `liff/src/components/MoodTracker.tsx`，使其能將用戶選擇的心情發送至後端 API。

## 🤝 貢獻

歡迎提交 issue 或 pull request，共同打造更好的 HealMate AI 陪伴師。