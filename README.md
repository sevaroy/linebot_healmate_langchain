# 🤖 LINE 占卜 & 心情陪伴 AI 師

## 🏆 專案亮點

*   **多模態 AI 代理**：整合 LangChain + GPT-4o + DeepSeek 實現智能對話系統。
*   **架構設計**：採用 FastAPI 後端 + LINE LIFF 前端的分層架構。
*   **技術創新**：實現塔羅牌 RAG 系統與情緒分析管道。

## 🛠 技術棧

*   **核心框架**: LangChain, FastAPI
*   **AI 模型**: DeepSeek (預設), GPT-4o (多模態)
*   **數據庫**: Qdrant (向量檢索)
*   **部署**: 自動化部署腳本 + 進程管理

## 🚧 未來規劃

### 近期 (Q3 2025)

*   **多語言支援**：日/英雙語界面。．．．
*   **自定義角色**：用戶創建專屬 AI 人格。
*   **API 開放平台**：第三方工具接入。

### 中期 (Q4 2025)

*   **情感語音合成**：個性化語音回應。
*   **跨平台擴展**：WhatsApp/Telegram 支援。
*   **訂閱分級系統**：進階功能商業化。

### 長期 (2026)

*   **AI 協作網絡**：多 Agent 協同解決複雜問題。
*   **個性化模型微調**：用戶專屬模型版本。
*   **AR 整合**：塔羅牌占卜視覺化體驗。

## 👨‍💻 個人貢獻

*   **系統架構設計**：主導 FastAPI + LangChain 分層架構。
*   **核心模組開發**：實現塔羅牌 RAG 系統與情緒分析管道。
*   **性能調優**：識別並解決主要性能瓶頸。
*   **部署自動化**：設計本地部署腳本與進程管理。

## 🚀 快速開始

1.  參閱 [安裝指南](docs/INSTALLATION.md) 完成環境設置。
2.  啟動服務:

    ```bash
    ./deploy_local.sh
    ```

3.  訪問 LINE Bot 進行測試。

## 📂 專案結構

```
├── docs/            # 文件 (包含安裝指南)
├── agents/          # LangChain Agent 實作
├── services/        # 外部服務整合
├── app.py           # FastAPI 主程式
└── README.md        # 本文件
```

## 🤝 學習資源

*   [LangChain Agents 官方文檔](https://python.langchain.com/docs/modules/agents/)
*   [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)
*   [OpenAI API 參考](https://platform.openai.com/docs/api-reference)
*   [FastAPI 文檔](https://fastapi.tiangolo.com/)

## 📚 進階指南

### 新增工具

1.  **定義新函數**：編寫一個 Python 函數，完成你想讓 Agent 做的事。
2.  **加上 `@tool` 裝飾器**：在函數上方加上 `@tool`，並寫好 docstring 描述工具的功能、參數和回傳值。
3.  **註冊工具**：將新工具函數加入到 `agents/langchain_agent.py` 的 `tools` 列表中。

### 修改系統提示

打開 `agents/langchain_agent.py`，找到 `SYSTEM_PROMPT` 變數。你可以修改這裡的內容來：

*   改變 Agent 的**角色**和**個性**。
*   給予 Agent 更明確的**指令**或**限制**。
*   教導 Agent 如何**更好地使用工具**。

## 📐 系統架構

```mermaid
flowchart LR
    A[LINE用戶] --> B[LINE平台]
    B --> C{FastAPI後端}
    C --> D[LangChain Agent]
    D --> E[工具調度器]
    E --> F[塔羅牌RAG]
    E --> G[情緒分析]
    E --> H[策略生成]
    F --> I[Qdrant向量庫]
    G --> J[情緒模型]
    H --> K[GPT-4o]
```

### 關鍵組件

1.  **路由層**：處理多平台請求 (LINE/Web)
2.  **Agent核心**：LangChain 驅動的決策引擎
3.  **記憶管理**：分層緩存 + 向量化長期記憶
4.  **工具層**：可插拔式工具模組
5.  **輸出適配器**：平台專用響應格式化

## 📝 專案貢獻

歡迎提交 issue 或 pull request，共同打造更好的 AI Agent LINE Bot。