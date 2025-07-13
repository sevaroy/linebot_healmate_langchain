#!/bin/bash

# LINE 占卜 & 心情陪伴 AI 師 後端啟動腳本
# 此腳本用於啟動後端 FastAPI 服務

# 顏色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示歡迎訊息
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  LINE 占卜 & 心情陪伴 AI 師 - 後端啟動  ${NC}"
echo -e "${BLUE}======================================${NC}"

# 檢查 .env 檔案是否存在
if [ ! -f ".env" ]; then
    echo -e "${RED}錯誤: .env 檔案不存在${NC}"
    echo -e "${YELLOW}請複製 .env.example 到 .env 並填入必要的環境變數${NC}"
    exit 1
fi

# 啟動虛擬環境
echo -e "\n${GREEN}1. 啟動 Python 虛擬環境...${NC}"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}錯誤: 無法啟動虛擬環境${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 虛擬環境已啟動${NC}"
else
    echo -e "${RED}錯誤: 找不到 .venv 資料夾${NC}"
    echo -e "${YELLOW}請先執行以下命令創建虛擬環境:${NC}"
    echo -e "python3 -m venv .venv"
    echo -e "source .venv/bin/activate"
    echo -e "pip install -r requirements.txt"
    exit 1
fi

# 創建日誌資料夾
mkdir -p logs

# 啟動後端 FastAPI 服務器
echo -e "\n${GREEN}2. 啟動後端服務...${NC}"
echo -e "${BLUE}啟動 FastAPI 後端服務器...${NC}"
.venv/bin/uvicorn app:app --reload --port 8080 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > logs/backend.pid
echo -e "${GREEN}✓ 後端服務已啟動 (PID: $BACKEND_PID)${NC}"

# 等待服務啟動
echo -e "\n${YELLOW}等待服務啟動中...${NC}"
sleep 3

# 顯示服務網址
echo -e "\n${GREEN}3. 服務已啟動!${NC}"
echo -e "${BLUE}後端 API: ${NC}http://localhost:8080"
echo -e "\n${YELLOW}請使用瀏覽器訪問以上網址${NC}"

# 使用說明
echo -e "\n${BLUE}======================================${NC}"
echo -e "${BLUE}              使用說明                ${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "• 服務日誌保存在 logs/backend.log"
echo -e "• 如要停止服務，請執行 ./stop_backend.sh"
echo -e "• 要測試 LINE Bot，請使用 ngrok 等工具建立公開 URL"
echo -e "${BLUE}======================================${NC}"

# 保持腳本運行並顯示日誌
echo -e "\n${YELLOW}按 Ctrl+C 停止此腳本 (不會停止服務)${NC}"
tail -f logs/backend.log
