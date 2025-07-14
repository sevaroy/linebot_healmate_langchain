# 🤖 HealMate AI 陪伴師：基於 LLM 的個人化情緒支持平台

## 🌟 專案概述

HealMate 是一個創新的 LINE 平台 AI 陪伴師，旨在透過先進的語言模型 (LLM) 和多模態互動，為用戶提供個人化的情緒支持、塔羅占卜解讀及生活策略建議。本專案不僅聚焦於功能實現，更著重於**穩健的架構設計、高效的開發流程與持續優化的實踐**，旨在打造一個可擴展、易維護且具備深度情緒價值的 AI 應用。

## ✨ 核心亮點與技術深度

本專案在設計與實踐中，融入了多項現代軟體工程與 AI 開發的最佳實踐：

1.  **模組化與分層架構**：
    *   採用清晰的 FastAPI (後端 API) + LangChain (AI 代理核心) + LINE LIFF (前端互動介面) 分層架構，確保各模組職責分離，提高可維護性與擴展性。
    *   數據處理、資料庫操作、Agent 工具等模組獨立設計，便於單元測試與功能迭代。

2.  **智能對話代理 (LangChain Agent)**：
    *   **意圖理解與工具調度**：基於 LangChain Agent 框架，實現智能意圖識別與工具自動調用，使 AI 能根據用戶需求靈活響應。
    *   **對話記憶管理**：為每個用戶實作獨立的 `ConversationBufferWindowMemory`，確保多輪對話的上下文連貫性，提升用戶體驗。
    *   **個人化與情緒智能**：
        *   **心情日記整合**：引入 PostgreSQL 資料庫持久化儲存用戶心情數據，並透過專屬 LIFF 介面進行數據收集。
        *   **情緒脈絡感知**：Agent 內建 `MoodHistoryChecker` 工具，允許其查詢用戶歷史心情，從而提供更具同理心和個人化的建議，將「識別情緒」昇華為「理解情緒」。

3.  **高效數據管線 (RAG)**：
    *   **塔羅牌 RAG 系統**：利用 Qdrant 向量資料庫實現塔羅牌知識的語義檢索。用戶提問時，Agent 能精準檢索最相關的牌義，並結合 LLM 進行深度解讀，而非簡單的關鍵字匹配。
    *   **統一數據處理**：將分散的數據抓取、清洗、驗證、嵌入腳本整合為單一、自動化的 `data_pipeline.py`，確保數據處理流程的健壯性與可重現性。

4.  **容器化與開發流程優化**：
    *   **Docker Compose 統一管理**：所有服務 (後端、前端、資料庫、向量庫、快取) 均透過 Docker Compose 進行容器化管理，實現「一鍵啟動/停止」，極大簡化開發環境配置與部署流程。
    *   **依賴管理規範化**：Python 依賴採用 `pip-tools` 進行精確管理，確保開發與部署環境的一致性，避免版本衝突。
    *   **自動化構建**：為前後端服務編寫 `Dockerfile`，實現自動化映像構建，提升部署效率。

## 🛠 技術棧

*   **後端框架**: FastAPI (Python)
*   **AI 框架**: LangChain
*   **語言模型**: DeepSeek (核心 LLM)
*   **向量資料庫**: Qdrant
*   **關聯式資料庫**: PostgreSQL
*   **快取/訊息佇列**: Redis
*   **前端**: LINE LIFF (React + Vite)
*   **依賴管理**: `pip-tools`, `npm`
*   **容器化**: Docker, Docker Compose

## 🚀 快速開始

本專案已全面 Docker 化，提供簡潔高效的啟動體驗。

1.  **環境準備**：
    *   安裝 Docker 及 Docker Compose。
    *   確保已安裝 Python 3.11+ (用於本地腳本執行，非容器內)。

2.  **專案克隆**：
    ```bash
    git clone https://github.com/your-repo/Linebot_healmate_langchain.git
    cd Linebot_healmate_langchain
    ```

3.  **環境變數配置**：
    複製 `.env.example` 為 `.env`，並填入必要的 API Keys 及其他配置。
    ```bash
    cp .env.example .env
    # 編輯 .env 檔案，填入 DEEPSEEK_API_KEY, LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, VITE_LIFF_ID 等
    ```

4.  **啟動所有服務**：
    此命令將構建 Docker 映像並啟動所有後端、前端、資料庫服務。
    ```bash
    docker-compose --project-directory . -f infra/docker-compose.yaml up --build -d
    ```
    *   `--build`: 首次運行或 Dockerfile 有變更時使用，確保映像最新。
    *   `-d`: 在後台運行服務。

    服務啟動後，你可以訪問：
    *   **後端 API**: `http://localhost:8080`
    *   **前端 LIFF**: `http://localhost:5173`

5.  **初始化塔羅牌數據 (重要)**：
    首次運行或數據更新時，需生成塔羅牌嵌入向量並上傳至 Qdrant。請確保 Qdrant 服務已運行。
    ```bash
    docker-compose --project-directory . -f infra/docker-compose.yaml exec backend python scripts/data_pipeline.py --embedder ollama --model nomic-embed-text
    # 提示：若需使用其他嵌入模型，請參考 data_pipeline.py 的說明。
    ```

6.  **停止所有服務**：
    ```bash
    docker-compose --project-directory . -f infra/docker-compose.yaml down
    ```

## 📂 專案結構

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
├── data/            # 數據文件 (如處理後的塔羅牌數據)
├── infra/           # 基礎設施配置 (Docker Compose)
├── liff/            # LINE LIFF 前端應用
│   ├── src/               # React 原始碼
│   └── Dockerfile.frontend # 前端服務 Dockerfile
├── scripts/         # 自動化腳本 (如統一的數據處理管線)
└── ui/              # LINE UI 相關工具
```

## 📈 優化與重構歷程 (由 Gemini AI 代理協作完成)

本專案經歷了從原型到產品級的關鍵重構與優化，旨在解決初期存在的技術債務與提升整體品質。主要里程碑包括：

1.  **依賴管理規範化**：從混亂的 `requirements.txt` 轉向 `pip-tools`，實現精確且可重現的 Python 環境管理。
2.  **服務啟動與部署簡化**：淘汰冗餘的 Shell 腳本，全面採用 Docker Compose 進行服務的統一啟動、停止與構建，大幅提升開發者體驗與部署效率。
3.  **專案結構清晰化**：清理了前端專案中多餘的嵌套結構與混淆的部署配置，使專案目錄層次更合理。
4.  **數據管線自動化與整合**：將分散的數據處理腳本整合為單一、可配置的 `data_pipeline.py`，實現數據從抓取到嵌入 Qdrant 的全自動化流程。
5.  **AI Agent 核心能力增強**：
    *   **記憶機制修復**：修正 LangChain Agent 的記憶體處理邏輯，確保對話上下文的正確傳遞與管理。
    *   **個人化心情日記功能**：引入 PostgreSQL 數據庫，實現用戶心情數據的持久化儲存。Agent 透過新增的 `MoodHistoryChecker` 工具，能夠查詢並利用用戶歷史心情，提供更具同理心的個人化回應。
    *   **情緒分析與策略建議優化**：強化 `EmotionAnalyzer` 的輸出穩定性，並在 `StrategyAdvisor` 中加入安全免責聲明，同時為未來整合更多情緒上下文奠定基礎。
    *   **LLM 統一**：將核心 LLM 統一為 DeepSeek API，並相應調整了圖片/語音訊息的處理策略。

## 💡 未來展望

*   **情緒價值深度挖掘**：引入引導式日記、應對技巧庫、肯定語生成等功能，提供更豐富的情緒支持工具。
*   **數據分析與視覺化**：增強心情數據的分析能力，並在 LIFF 中提供更直觀的視覺化報告。
*   **多平台擴展**：探索與其他訊息平台（如 WhatsApp, Telegram）的整合。
*   **模型迭代與優化**：持續探索更適合情緒陪伴場景的 LLM 模型，並進行提示詞工程的精細化調優。

## 🤝 貢獻

歡迎提交 issue 或 pull request，共同打造更好的 HealMate AI 陪伴師。
