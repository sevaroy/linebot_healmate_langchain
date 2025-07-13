#!/bin/bash

# LINE 占卜 & 心情陪伴 AI 師 前端啟動腳本
# 此腳本用於啟動前端 LIFF 應用

# 顏色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示歡迎訊息
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  LINE 占卜 & 心情陪伴 AI 師 - 前端啟動  ${NC}"
echo -e "${BLUE}======================================${NC}"

# 確認 LIFF 前端應用是否有 node_modules
echo -e "\n${GREEN}1. 檢查 LIFF 前端應用依賴...${NC}"
if [ ! -d "liff/node_modules" ]; then
    echo -e "${YELLOW}LIFF 前端應用尚未安裝依賴，正在安裝...${NC}"
    cd liff && npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}錯誤: 無法安裝 LIFF 前端依賴${NC}"
        cd ..
        exit 1
    fi
    cd ..
    echo -e "${GREEN}✓ LIFF 前端依賴已安裝${NC}"
else
    echo -e "${GREEN}✓ LIFF 前端依賴已存在${NC}"
fi

# 創建日誌資料夾
mkdir -p logs

# 啟動前端 LIFF 應用
echo -e "\n${GREEN}2. 啟動前端服務...${NC}"
echo -e "${BLUE}啟動 LIFF 前端應用...${NC}"
cd liff && npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > logs/frontend.pid
echo -e "${GREEN}✓ 前端應用已啟動 (PID: $FRONTEND_PID)${NC}"

# 等待服務啟動
echo -e "\n${YELLOW}等待服務啟動中...${NC}"
sleep 3

# 顯示服務網址
echo -e "\n${GREEN}3. 服務已啟動!${NC}"
echo -e "${BLUE}前端 LIFF: ${NC}http://localhost:5173"
echo -e "\n${YELLOW}請使用瀏覽器訪問以上網址${NC}"

# 使用說明
echo -e "\n${BLUE}======================================${NC}"
echo -e "${BLUE}              使用說明                ${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "• 服務日誌保存在 logs/frontend.log"
echo -e "• 如要停止服務，請執行 ./stop_frontend.sh"
echo -e "• 本地前端無法使用 LINE 登入功能，請使用瀏覽器測試 UI"
echo -e "${BLUE}======================================${NC}"

# 保持腳本運行並顯示日誌
echo -e "\n${YELLOW}按 Ctrl+C 停止此腳本 (不會停止服務)${NC}"
tail -f logs/frontend.log
