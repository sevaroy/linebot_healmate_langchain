#!/usr/bin/env python3
"""使用 Ollama 生成塔羅牌嵌入向量並上傳至 Qdrant REST API.

使用方法:
    python scripts/prepare_tarot_embeddings_ollama_simple.py [模型名稱]

環境變數:
    OLLAMA_BASE_URL        - Ollama API URL (預設: http://localhost:11434)
    QDRANT_HOST            - Qdrant 主機 (預設: localhost)
    QDRANT_PORT            - Qdrant 埠 (預設: 6333)
    QDRANT_COLLECTION      - 集合名稱 (預設: tarot_cards_ollama)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tarot_cards.json"

# Ollama 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = "nomic-embed-text"  # 良好的開源嵌入模型
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL

# Qdrant 配置
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_BASE_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", f"tarot_cards_ollama_{MODEL_NAME.replace(':', '_')}")


def get_embedding(text: str, model: str = MODEL_NAME) -> list[float]:
    """使用 Ollama 獲取文本嵌入向量。
    
    Args:
        text: 要嵌入的文本
        model: 要使用的 Ollama 模型
        
    Returns:
        嵌入向量
    """
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": model, "prompt": text}
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        print(f"錯誤: {str(e)}")
        raise


def check_model_availability(model: str) -> bool:
    """檢查 Ollama 模型是否可用。
    
    Args:
        model: 要檢查的模型名稱
        
    Returns:
        模型是否可用
    """
    url = f"{OLLAMA_BASE_URL}/api/tags"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            available_models = [m["name"] for m in data.get("models", [])]
            return model in available_models
    except Exception as e:
        print(f"檢查模型可用性時發生錯誤: {str(e)}")
        return False


def get_embedding_dimensions(model: str) -> int:
    """獲取嵌入模型的維度。
    
    Args:
        model: 模型名稱
        
    Returns:
        嵌入向量的維度
    """
    # 對一個簡單的文本進行嵌入以獲取維度
    sample_embedding = get_embedding("This is a test", model)
    return len(sample_embedding)


def ensure_collection_exists(collection_name: str, vector_size: int) -> None:
    """確保 Qdrant 集合存在，如果不存在則創建。
    
    Args:
        collection_name: 集合名稱
        vector_size: 嵌入向量的維度
    """
    # 檢查集合是否存在
    url = f"{QDRANT_BASE_URL}/collections/{collection_name}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ Qdrant 集合已存在: {collection_name}")
                return
            elif response.status_code != 404:
                response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            print(f"檢查集合時發生錯誤: {e}")
            raise
    
    # 創建集合
    url = f"{QDRANT_BASE_URL}/collections/{collection_name}"
    payload = {
        "vectors": {
            "size": vector_size,
            "distance": "Cosine"
        }
    }
    
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.put(url, json=payload)
            response.raise_for_status()
            print(f"✅ 創建 Qdrant 集合: {collection_name}")
    except Exception as e:
        print(f"創建集合時發生錯誤: {str(e)}")
        raise


def upload_points_batch(collection_name: str, points: list[dict], batch_size: int = 100) -> None:
    """將點批量上傳至 Qdrant。
    
    Args:
        collection_name: 集合名稱
        points: 點列表
        batch_size: 批次大小
    """
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        url = f"{QDRANT_BASE_URL}/collections/{collection_name}/points"
        payload = {"points": batch}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.put(url, json=payload)
                response.raise_for_status()
                print(f"  已上傳 {i + len(batch)}/{len(points)} 個點")
        except Exception as e:
            print(f"上傳點時發生錯誤: {str(e)}")
            raise


def main() -> None:
    """讀取塔羅牌數據，生成嵌入向量並上傳至 Qdrant。"""
    print(f"📊 使用 Ollama 模型 '{MODEL_NAME}' 生成塔羅牌嵌入向量")
    
    # 檢查 Ollama 服務可用性
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{OLLAMA_BASE_URL}/api/version")
            print(f"✅ Ollama 服務可用，版本: {response.json().get('version')}")
    except Exception as e:
        print(f"❌ 無法連接到 Ollama 服務: {str(e)}")
        print(f"   請確保 Ollama 已運行且可訪問: {OLLAMA_BASE_URL}")
        sys.exit(1)
    
    # 檢查 Qdrant 服務可用性
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{QDRANT_BASE_URL}/collections")
            print(f"✅ Qdrant 服務可用")
    except Exception as e:
        print(f"❌ 無法連接到 Qdrant 服務: {str(e)}")
        print(f"   請確保 Qdrant 已運行且可訪問: {QDRANT_BASE_URL}")
        sys.exit(1)
    
    # 檢查模型可用性
    if not check_model_availability(MODEL_NAME):
        print(f"⚠️ 模型 '{MODEL_NAME}' 在 Ollama 中可能不可用")
        pull = input(f"是否下載 {MODEL_NAME} 模型? (y/n): ")
        if pull.lower() == 'y':
            print(f"下載 {MODEL_NAME} 模型中...")
            os.system(f"ollama pull {MODEL_NAME}")
        else:
            print("繼續使用已存在的模型...")
    
    # 載入塔羅牌數據
    try:
        with DATA_PATH.open("r", encoding="utf-8") as fp:
            cards = json.load(fp)
        print(f"✅ 載入了 {len(cards)} 張塔羅牌")
    except Exception as e:
        print(f"❌ 載入塔羅牌數據失敗: {str(e)}")
        sys.exit(1)
    
    # 獲取嵌入向量的維度
    try:
        vector_size = get_embedding_dimensions(MODEL_NAME)
        print(f"✅ {MODEL_NAME} 嵌入向量維度: {vector_size}")
    except Exception as e:
        print(f"❌ 無法獲取嵌入向量維度: {str(e)}")
        sys.exit(1)
    
    # 確保集合存在
    try:
        ensure_collection_exists(COLLECTION_NAME, vector_size)
    except Exception as e:
        print(f"❌ Qdrant 操作失敗: {str(e)}")
        print("   請確保 Qdrant 服務正在運行")
        sys.exit(1)
    
    # 準備嵌入向量和 payload
    print(f"⏳ 生成 {len(cards)} 張塔羅牌的嵌入向量 (這可能需要一些時間)...")
    
    points = []
    for i, card in enumerate(cards):
        try:
            # 為每張卡牌生成嵌入向量
            card_text = f"{card['name']} ({card['orientation']}): {card['meaning']}"
            embedding = get_embedding(card_text, MODEL_NAME)
            
            # 創建 Qdrant 點
            points.append({
                "id": card["id"],
                "vector": embedding,
                "payload": card,
            })
            
            # 顯示進度
            if (i + 1) % 10 == 0 or i == len(cards) - 1:
                print(f"  進度: {i + 1}/{len(cards)} ({((i + 1) / len(cards) * 100):.1f}%)")
        except Exception as e:
            print(f"❌ 卡牌 '{card['name']}' 的嵌入失敗: {str(e)}")
    
    # 將嵌入向量上傳至 Qdrant
    if points:
        try:
            print(f"⏳ 將 {len(points)} 張塔羅牌上傳至 Qdrant...")
            start_time = time.time()
            upload_points_batch(COLLECTION_NAME, points)
            print(f"✅ 成功上傳 {len(points)} 張塔羅牌至 Qdrant 集合 '{COLLECTION_NAME}'")
            print(f"   耗時: {time.time() - start_time:.2f} 秒")
        except Exception as e:
            print(f"❌ Qdrant 上傳失敗: {str(e)}")
            sys.exit(1)
    else:
        print("❌ 沒有可上傳的嵌入向量")
        sys.exit(1)
    
    print("\n🎉 塔羅牌嵌入向量生成和上傳完成！")
    print(f"💡 提示: 您可以通過更新 RAG 服務來使用此新的集合 '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()
