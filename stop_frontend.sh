#!/bin/bash

# LINE 占卜 & 心情陪伴 AI 師 前端停止腳本
# 此腳本用於停止前端 LIFF 應用

# 顏色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示歡迎訊息
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  LINE 占卜 & 心情陪伴 AI 師 - 前端停止  ${NC}"
echo -e "${BLUE}======================================${NC}"

# 停止前端服務
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "正在停止前端服務 (PID: $FRONTEND_PID)..."
        kill -15 $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null; then
            echo -e "${YELLOW}服務未完全停止，強制結束進程...${NC}"
            kill -9 $FRONTEND_PID 2>/dev/null
            sleep 1
        fi
        echo -e "${GREEN}✓ 前端服務已停止${NC}"
    else
        echo -e "${YELLOW}前端服務已不在運行狀態 (PID: $FRONTEND_PID)${NC}"
    fi
    rm -f logs/frontend.pid
else
    echo -e "${YELLOW}找不到前端服務的 PID 記錄${NC}"
    
    # 檢查是否有 vite 進程在運行，如果有則停止它們
    VITE_PIDS=$(ps -ef | grep "[v]ite" | awk '{print $2}')
    if [ ! -z "$VITE_PIDS" ]; then
        echo -e "${YELLOW}檢測到其他 vite 進程，正在清理...${NC}"
        for PID in $VITE_PIDS; do
            kill -15 $PID 2>/dev/null
            sleep 1
            kill -9 $PID 2>/dev/null
        done
        echo -e "${GREEN}✓ 已清理所有 vite 進程${NC}"
    fi
fi

echo -e "\n${BLUE}======================================${NC}"
echo -e "${BLUE}          前端服務已停止            ${NC}"
echo -e "${BLUE}======================================${NC}"
