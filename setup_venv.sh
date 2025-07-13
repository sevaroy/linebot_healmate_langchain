#!/bin/bash

# HealMate 專案自動虛擬環境安裝腳本
# 支援自動尋找 python3.10 > python3.11 > python3
# 並自動安裝 requirements.txt 及 deepseek-openai（若支援）

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

set -e

# 1. 尋找可用 python 版本
PYTHON_BIN=""
for ver in python3.10 python3.11 python3; do
    if command -v $ver >/dev/null 2>&1; then
        PYTHON_BIN=$(command -v $ver)
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}找不到可用的 Python 3.10/3.11/3！請先安裝合適版本。${NC}"
    exit 1
fi

echo -e "${GREEN}使用 Python: $($PYTHON_BIN --version)${NC}"

# 2. 移除舊虛擬環境
if [ -d ".venv" ]; then
    echo -e "${YELLOW}移除舊的 .venv ...${NC}"
    rm -rf .venv
fi

# 3. 建立新虛擬環境
$PYTHON_BIN -m venv .venv
source .venv/bin/activate

# 4. 升級 pip 並安裝依賴
pip install --upgrade pip
pip install -r requirements.txt

# 5. deepseek-openai 安裝判斷
if grep -q deepseek-openai requirements.txt; then
    PY_VER=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$PY_VER" == "3.10" || "$PY_VER" == "3.11" ]]; then
        echo -e "${GREEN}安裝 deepseek-openai...${NC}"
        pip install deepseek-openai
    else
        echo -e "${YELLOW}警告：deepseek-openai 只支援 Python 3.10/3.11，當前版本 $PY_VER，請考慮切換！${NC}"
    fi
else
    # 若 requirements.txt 沒有列出，也可手動加裝
    PY_VER=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$PY_VER" == "3.10" || "$PY_VER" == "3.11" ]]; then
        echo -e "${YELLOW}如需 DeepSeek，將自動安裝 deepseek-openai...${NC}"
        pip install deepseek-openai || true
    fi
fi

echo -e "${GREEN}虛擬環境安裝完成！${NC}"
