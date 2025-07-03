#!/usr/bin/env python3
"""修復 tarot_cards.json 中的結構問題，包括重複條目和 ID 順序。"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tarot_cards.json"
FIXED_PATH = Path(__file__).resolve().parent.parent / "data" / "tarot_cards_fixed.json"


def main() -> None:
    """讀取、修復並保存修復後的 tarot_cards.json。"""
    print("📖 讀取塔羅牌 JSON 數據...")
    try:
        cards = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        print(f"✅ 讀取了 {len(cards)} 張牌")
    except json.JSONDecodeError:
        sys.exit("❌ JSON 解析錯誤！檢查 JSON 格式是否正確。")
    except FileNotFoundError:
        sys.exit(f"❌ 找不到文件: {DATA_PATH}")

    print("\n🔧 修復重複條目和 ID 順序...")
    
    # 第一步：按照名稱和方向分組，保留唯一條目
    unique_cards = {}
    for card in cards:
        key = (card["name"], card["orientation"])
        if key not in unique_cards:
            unique_cards[key] = card
        else:
            print(f"⚠️ 發現重複項: {card['name']} ({card['orientation']})")
    
    print(f"✅ 保留 {len(unique_cards)} 張唯一牌")
    
    # 第二步：重新組織牌組
    # 主牌（Major Arcana）：0-21 正位+逆位：0-43
    # 聖杯牌（Cups）：Ace-King 正位+逆位：44-71
    # 星幣牌（Pentacles）：Ace-King 正位+逆位：72-99 
    # 寶劍牌（Swords）：Ace-King 正位+逆位：100-127
    # 權杖牌（Wands）：Ace-King 正位+逆位：128-155
    
    # 按類型和名稱排序
    major_cards = [card for card in unique_cards.values() if card["arcana"] == "Major"]
    cups_cards = [card for card in unique_cards.values() if card["arcana"] == "Minor" and "of Cups" in card["name"]]
    pentacles_cards = [card for card in unique_cards.values() if card["arcana"] == "Minor" and "of Pentacles" in card["name"]]
    swords_cards = [card for card in unique_cards.values() if card["arcana"] == "Minor" and "of Swords" in card["name"]]
    wands_cards = [card for card in unique_cards.values() if card["arcana"] == "Minor" and "of Wands" in card["name"]]
    
    # Major Arcana 排序順序
    major_order = [
        "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
        "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
        "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
        "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
        "Judgement", "The World"
    ]
    
    # Minor Arcana 排序順序
    minor_order = [
        "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "Page", "Knight", "Queen", "King"
    ]
    
    # 排序函數
    def sort_major_cards(card):
        try:
            return major_order.index(card["name"]), 0 if card["orientation"] == "upright" else 1
        except ValueError:
            print(f"⚠️ 無法排序主牌: {card['name']}")
            return 99, 0 if card["orientation"] == "upright" else 1
    
    def sort_minor_cards(card):
        for i, prefix in enumerate(minor_order):
            if card["name"].startswith(prefix):
                return i, 0 if card["orientation"] == "upright" else 1
        print(f"⚠️ 無法排序小牌: {card['name']}")
        return 99, 0 if card["orientation"] == "upright" else 1
    
    # 排序
    major_cards.sort(key=sort_major_cards)
    cups_cards.sort(key=sort_minor_cards)
    pentacles_cards.sort(key=sort_minor_cards)
    swords_cards.sort(key=sort_minor_cards)
    wands_cards.sort(key=sort_minor_cards)
    
    # 重新分配ID
    fixed_cards = []
    id_counter = 0
    
    for card in major_cards:
        card["id"] = id_counter
        fixed_cards.append(card)
        id_counter += 1
    
    for card in cups_cards:
        card["id"] = id_counter
        fixed_cards.append(card)
        id_counter += 1
    
    for card in pentacles_cards:
        card["id"] = id_counter
        fixed_cards.append(card)
        id_counter += 1
    
    for card in swords_cards:
        card["id"] = id_counter
        fixed_cards.append(card)
        id_counter += 1
    
    for card in wands_cards:
        card["id"] = id_counter
        fixed_cards.append(card)
        id_counter += 1
    
    print(f"✅ 重新排序和分配 ID 給 {len(fixed_cards)} 張牌")
    
    # 檢查是否有 78 × 2 = 156 張牌
    if len(fixed_cards) != 156:
        print(f"⚠️ 警告: 預期 156 張牌，但找到 {len(fixed_cards)} 張")
        
        # 檢查哪些牌缺失
        all_major = set(major_order)
        all_minor = []
        for suit in ["Cups", "Pentacles", "Swords", "Wands"]:
            for rank in minor_order:
                all_minor.append(f"{rank} of {suit}")
        
        all_cards = set(all_major) | set(all_minor)
        found_names = {card["name"] for card in fixed_cards}
        
        missing = all_cards - found_names
        if missing:
            print(f"⚠️ 缺失的牌: {missing}")
    
    # 保存修復後的數據
    try:
        with FIXED_PATH.open("w", encoding="utf-8") as f:
            json.dump(fixed_cards, f, ensure_ascii=False, indent=2)
        print(f"✅ 修復後的數據已保存至: {FIXED_PATH}")
    except Exception as e:
        sys.exit(f"❌ 保存失敗: {e}")
    
    print("\n🎮 運行驗證腳本以檢查修復後的數據...")


if __name__ == "__main__":
    main()
