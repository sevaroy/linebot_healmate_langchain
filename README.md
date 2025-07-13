# 🤖 Advanced AI Agent LINE Bot (LangChain + GPT-4o + DeepSeek)

## ✨ 核心功能

- 🧠 **Agent 架構** - 採用 LangChain Agent 實現模組化邏輯與工具管理
- 🛠️ **工具擴充** - 內建塔羅牌工具，提供清晰擴充介面
- 🖼️🎙️ **多模態處理** - 整合 GPT-4o 支援文字、圖片和語音
- 🔥 **高效模型** - 預設使用 DeepSeek 提供經濟高效的對話體驗
- 🗣️ **異步處理** - 全異步設計提升高併發效能
- 📝 **對話記憶** - LangChain Memory 實現上下文記憶
- 🚀 **一鍵部署** - 完整部署指南與腳本

## ⚙️ 技術配置

### 模型設定

```env
# 主要語言模型 (deepseek | gpt-3.5-turbo | gpt-4-turbo)
PRIMARY_MODEL=deepseek

# 多模態模型 (gpt-4o | gpt-4-vision-preview)
MULTIMODAL_MODEL=gpt-4o
```

## 🚀 快速開始

1. 參閱 [安裝指南](docs/INSTALLATION.md) 完成環境設置
2. 啟動服務:
   ```bash
   ./deploy_local.sh
   ```
3. 訪問 LINE Bot 進行測試

## 📂 專案結構

```
├── docs/            # 文件 (包含安裝指南)
├── agents/          # LangChain Agent 實作
├── services/        # 外部服務整合
├── app.py           # FastAPI 主程式
└── README.md        # 本文件
```

## 🤝 學習資源

- [LangChain Agents 官方文檔](https://python.langchain.com/docs/modules/agents/)
- [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)
- [OpenAI API 參考](https://platform.openai.com/docs/api-reference)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)

## 📚 進階指南

### 新增工具

1.  **定義新函數**：編寫一個 Python 函數，完成你想讓 Agent 做的事。
2.  **加上 `@tool` 裝飾器**：在函數上方加上 `@tool`，並寫好 docstring 描述工具的功能、參數和回傳值。
3.  **註冊工具**：將新工具函數加入到 `agents/langchain_agent.py` 的 `tools` 列表中。

### 修改系統提示

打開 `agents/langchain_agent.py`，找到 `SYSTEM_PROMPT` 變數。你可以修改這裡的內容來：
-   改變 Agent 的**角色**和**個性**。
-   給予 Agent 更明確的**指令**或**限制**。
-   教導 Agent 如何**更好地使用工具**。

## 📝 專案貢獻

歡迎提交 issue 或 pull request，共同打造更好的 AI Agent LINE Bot。
