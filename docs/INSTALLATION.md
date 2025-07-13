# 安裝指南

## 系統需求

- Python 3.10 或更高版本
- Node.js 16+ (前端 LIFF 應用)
- ffmpeg (語音處理需用)

## 1. 環境準備

### 安裝 ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# 前往 ffmpeg.org 下載並將 bin 目錄加入 PATH
```

## 2. 專案設置

```bash
git clone https://github.com/yourusername/langchain-agent-linebot.git
cd langchain-agent-linebot

# 建立並啟用虛擬環境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 複製環境變數範例
cp .env.example .env
```

## 3. 配置設定

編輯 `.env` 文件，填入以下金鑰：
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `OPENAI_API_KEY` (或 `DEEPSEEK_API_KEY`)

## 4. 啟動服務

使用部署腳本啟動完整服務：

```bash
./deploy_local.sh
```

或手動啟動：

```bash
# 後端
uvicorn app:app --reload --port 8000

# 前端 (LIFF)
npm --prefix liff run dev
```

## 5. 測試

1. 使用 ngrok 暴露本地服務
2. 在 LINE Developer Console 設定 Webhook URL
3. 掃描 QR Code 測試功能
