#!/bin/bash

# LINE 占卜 & 心情陪伴 AI 師 本地服務停止腳本
# 此腳本用於安全地關閉由 deploy_local.sh 啟動的所有服務

# 顏色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示歡迎訊息
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  LINE 占卜 & 心情陪伴 AI 師 - 停止服務  ${NC}"
echo -e "${BLUE}======================================${NC}"

# 檢查是否有 PID 文件
if [ ! -f "logs/backend.pid" ] && [ ! -f "logs/frontend.pid" ]; then
    echo -e "${YELLOW}警告: 找不到服務 PID 文件，服務可能尚未啟動${NC}"
    
    # 嘗試查找相關進程
    BACKEND_PROCESSES=$(ps aux | grep "[u]vicorn app:app" | awk '{print $2}')
    FRONTEND_PROCESSES=$(ps aux | grep "[v]ite" | awk '{print $2}')
    
    if [ -n "$BACKEND_PROCESSES" ] || [ -n "$FRONTEND_PROCESSES" ]; then
        echo -e "${YELLOW}檢測到以下可能相關的進程:${NC}"
        
        if [ -n "$BACKEND_PROCESSES" ]; then
            echo -e "${YELLOW}後端進程:${NC}"
            ps aux | grep "[u]vicorn app:app"
            echo -e "${YELLOW}是否停止這些進程? (y/n)${NC}"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo $BACKEND_PROCESSES | xargs kill -9
                echo -e "${GREEN}✓ 後端進程已停止${NC}"
            fi
        fi
        
        if [ -n "$FRONTEND_PROCESSES" ]; then
            echo -e "${YELLOW}前端進程:${NC}"
            ps aux | grep "[v]ite"
            echo -e "${YELLOW}是否停止這些進程? (y/n)${NC}"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo $FRONTEND_PROCESSES | xargs kill -9
                echo -e "${GREEN}✓ 前端進程已停止${NC}"
            fi
        fi
        
        exit 0
    else
        echo -e "${RED}未檢測到運行中的服務進程${NC}"
        exit 1
    fi
fi

# 停止後端服務
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo -e "${YELLOW}正在停止後端服務 (PID: $BACKEND_PID)...${NC}"
        kill -15 $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null; then
            echo -e "${YELLOW}後端服務未響應，強制終止...${NC}"
            kill -9 $BACKEND_PID
        fi
        echo -e "${GREEN}✓ 後端服務已停止${NC}"
    else
        echo -e "${YELLOW}後端服務 (PID: $BACKEND_PID) 已不存在${NC}"
    fi
    rm logs/backend.pid
fi

# 停止前端服務
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${YELLOW}正在停止前端服務 (PID: $FRONTEND_PID)...${NC}"
        kill -15 $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null; then
            echo -e "${YELLOW}前端服務未響應，強制終止...${NC}"
            kill -9 $FRONTEND_PID
        fi
        echo -e "${GREEN}✓ 前端服務已停止${NC}"
    else
        echo -e "${YELLOW}前端服務 (PID: $FRONTEND_PID) 已不存在${NC}"
    fi
    rm logs/frontend.pid
fi

# 檢查是否有其他相關進程
UVICORN_PROCESSES=$(ps aux | grep "[u]vicorn app:app" | awk '{print $2}')
if [ -n "$UVICORN_PROCESSES" ]; then
    echo -e "${YELLOW}檢測到其他 uvicorn 進程，正在清理...${NC}"
    echo $UVICORN_PROCESSES | xargs kill -9
    echo -e "${GREEN}✓ 已清理所有 uvicorn 進程${NC}"
fi

VITE_PROCESSES=$(ps aux | grep "[v]ite" | awk '{print $2}')
if [ -n "$VITE_PROCESSES" ]; then
    echo -e "${YELLOW}檢測到其他 vite 進程，正在清理...${NC}"
    echo $VITE_PROCESSES | xargs kill -9
    echo -e "${GREEN}✓ 已清理所有 vite 進程${NC}"
fi

echo -e "\n${GREEN}所有服務已停止${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}            服務已完全停止            ${NC}"
echo -e "${BLUE}======================================${NC}"
