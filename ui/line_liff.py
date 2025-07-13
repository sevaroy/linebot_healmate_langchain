#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LINE LIFF 整合 UI 模組

此模組負責建立 LINE Bot 與 LIFF 應用程式整合的 UI 元件，例如：
- LIFF 啟動按鈕
- LIFF 應用入口 Flex 訊息
- LIFF URL 建構輔助函數
"""
import os
from typing import Dict, List, Any, Optional
from linebot.v3.messaging import (
    QuickReply,
    QuickReplyItem,
    TextMessage,
    FlexMessage,
    MessageAction,
    URIAction,
)

# 從環境變數獲取 LIFF URL (預設為本地開發伺服器)
LIFF_BASE_URL = os.environ.get("LIFF_BASE_URL", "https://liff.line.me")
LIFF_ID = os.environ.get("LIFF_ID", "")

def get_liff_url(path: str = "") -> str:
    """
    建構 LIFF 應用程式的 URL
    
    Args:
        path (str): LIFF 應用內的路徑，例如 '/tarot', '/mood' 等
        
    Returns:
        str: 完整的 LIFF 應用 URL
    """
    return f"{LIFF_BASE_URL}/{LIFF_ID}{path}"

def create_liff_quick_reply() -> QuickReply:
    """
    創建 LIFF 應用快速回覆按鈕
    
    Returns:
        QuickReply: 包含 LIFF 相關功能的快速回覆
    """
    items = [
        QuickReplyItem(
            action=URIAction(
                label="🔮 占卜紀錄",
                uri=get_liff_url("/history?type=tarot")
            )
        ),
        QuickReplyItem(
            action=URIAction(
                label="♈ 星座運勢",
                uri=get_liff_url("/history?type=zodiac")
            )
        ),
        QuickReplyItem(
            action=URIAction(
                label="📝 心情日記",
                uri=get_liff_url("/mood")
            )
        ),
        QuickReplyItem(
            action=URIAction(
                label="📊 歷史紀錄",
                uri=get_liff_url("/history")
            )
        ),
    ]
    return QuickReply(items=items)

def create_liff_launch_flex() -> FlexMessage:
    """
    創建 LIFF 應用啟動 Flex 訊息
    
    Returns:
        FlexMessage: 包含 LIFF 啟動選項的 Flex 訊息
    """
    flex_json = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.imgur.com/VRLihYo.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": get_liff_url()
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "個人化占卜與心靈空間",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#8A2BE2"
                },
                {
                    "type": "text",
                    "text": "打開您的個人化頁面，查看占卜歷史、星座運勢與心情追蹤",
                    "wrap": True,
                    "margin": "md",
                    "size": "sm",
                    "color": "#666666"
                },
                {
                    "type": "separator",
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "height": "sm",
                                    "color": "#9932CC",
                                    "action": {
                                        "type": "uri",
                                        "label": "占卜歷史",
                                        "uri": get_liff_url("/history?type=tarot")
                                    },
                                    "flex": 1
                                },
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "height": "sm",
                                    "color": "#1E88E5",
                                    "action": {
                                        "type": "uri",
                                        "label": "星座運勢",
                                        "uri": get_liff_url("/history?type=zodiac")
                                    },
                                    "flex": 1
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "height": "sm",
                                    "color": "#27AE60",
                                    "action": {
                                        "type": "uri",
                                        "label": "心情追蹤",
                                        "uri": get_liff_url("/mood")
                                    },
                                    "flex": 1
                                },
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "height": "sm",
                                    "color": "#FF8C00",
                                    "action": {
                                        "type": "uri",
                                        "label": "完整歷史",
                                        "uri": get_liff_url("/history")
                                    },
                                    "flex": 1
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "uri",
                        "label": "進入個人化空間",
                        "uri": get_liff_url()
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "返回主選單",
                        "text": "顯示主選單"
                    }
                }
            ],
            "flex": 0
        }
    }
    
    return FlexMessage(alt_text="個人占卜與心情空間", contents=flex_json)
