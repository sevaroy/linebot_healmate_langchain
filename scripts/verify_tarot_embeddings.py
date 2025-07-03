#!/usr/bin/env python3
"""驗證塔羅牌嵌入向量是否已成功上傳至 Qdrant，並進行簡單的檢索測試。

使用方法:
    python scripts/verify_tarot_embeddings.py [collection_name]

環境變數:
    OLLAMA_BASE_URL - Ollama API URL (預設: http://localhost:11434)
    QDRANT_HOST     - Qdrant 主機 (預設: localhost)
    QDRANT_PORT     - Qdrant 埠 (預設: 6333)
"""
from __future__ import annotations

import os
import sys
from pprint import pprint

import httpx

# Ollama 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = "nomic-embed-text"  # 使用與生成嵌入相同的模型

# Qdrant 配置
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_BASE_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

# 使用命令行參數指定集合名稱，或使用默認值
COLLECTION_NAME = sys.argv[1] if len(sys.argv) > 1 else f"tarot_cards_ollama_{DEFAULT_MODEL.replace(':', '_')}"


def get_collection_info() -> dict:
    """獲取集合信息。"""
    url = f"{QDRANT_BASE_URL}/collections/{COLLECTION_NAME}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            result = response.json()
            # 為調試添加完整的回應輸出
            print("DEBUG - API 回應:")
            pprint(result)
            return result
    except Exception as e:
        print(f"⚠️ API 調用錯誤: {str(e)}")
        raise


def count_points() -> int:
    """計算集合中的點數量。"""
    url = f"{QDRANT_BASE_URL}/collections/{COLLECTION_NAME}/points/count"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json().get("result", {}).get("count", 0)


def get_embedding(text: str, model: str = DEFAULT_MODEL) -> list[float]:
    """使用 Ollama 獲取文本嵌入向量。"""
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": model, "prompt": text}
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["embedding"]


def search_by_text(text: str, limit: int = 5) -> list[dict]:
    """根據文本在集合中搜索相似的點。"""
    # 獲取查詢的嵌入向量
    embedding = get_embedding(text)
    
    # 執行向量搜索
    url = f"{QDRANT_BASE_URL}/collections/{COLLECTION_NAME}/points/search"
    payload = {
        "vector": embedding,
        "limit": limit,
        "with_payload": True,
    }
    
    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("result", [])


def main() -> None:
    """執行驗證和測試。"""
    print(f"檢查 Qdrant 集合: {COLLECTION_NAME}\n")
    
    # 獲取集合信息
    try:
        collection_info = get_collection_info()
        print(f"集合資訊:\n")
        
        # 根據 Qdrant API 的回應結構安全地提取資訊
        if 'result' in collection_info:
            info = collection_info['result']
            print(f"  名稱: {info.get('name', '未知')}")
            
            if 'vectors' in info:
                vectors_info = info['vectors']
                if isinstance(vectors_info, dict):
                    print(f"  向量大小: {vectors_info.get('size', '未知')}")
                    print(f"  距離函數: {vectors_info.get('distance', '未知')}")
                else:
                    print(f"  向量資訊: {vectors_info}")
            else:
                print("  沒有向量資訊")
        else:
            print("  回應中沒有 'result' 欄位")
            pprint(collection_info)  # 輸出完整回應供調試
    except Exception as e:
        print(f"❌ 無法獲取集合信息: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n嘗試直接查詢所有集合列表...")
        try:
            url = f"{QDRANT_BASE_URL}/collections"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                collections = response.json()
                print("可用集合:")
                pprint(collections)
        except Exception as inner_e:
            print(f"❌ 無法獲取集合列表: {str(inner_e)}")
        sys.exit(1)
    
    # 計算點數量
    try:
        count = count_points()
        print(f"\n總共有 {count} 個向量在集合中")
        if count != 156:
            print(f"⚠️ 警告: 期望有 156 個向量 (78 張卡牌 × 2 種方向)，但實際有 {count} 個")
    except Exception as e:
        print(f"❌ 無法計算點數量: {str(e)}")
    
    # 執行搜索測試
    print("\n執行搜索測試:")
    
    # 測試查詢列表
    test_queries = [
        "愛情中的背叛",
        "職業上的新機會",
        "財務狀況不佳",
        "家庭關係緊張",
        "精神上的成長"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查詢: '{query}'")
        try:
            results = search_by_text(query)
            print(f"  找到 {len(results)} 個結果:")
            
            for i, result in enumerate(results):
                card = result.get("payload", {})
                print(f"\n  {i+1}. {card.get('name', 'Unknown')} ({card.get('orientation', 'Unknown')})")
                print(f"     相似度: {result.get('score', 0):.4f}")
                
                # 限制意義顯示長度，避免過長
                meaning = card.get("meaning", "")
                if len(meaning) > 100:
                    meaning = meaning[:100] + "..."
                print(f"     意義: {meaning}")
        except Exception as e:
            print(f"  ❌ 搜索失敗: {str(e)}")
    
    print("\n✅ 驗證完成")


if __name__ == "__main__":
    main()
