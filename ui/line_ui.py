#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LINE Bot UI 模組

此模組負責建立 LINE Bot 的互動式 UI 元件，例如：
- 快速回覆按鈕
- Flex 訊息
- 按鈕模板
- 輪播模板

這些 UI 元件使用 LINE Bot SDK v3 建立。
"""
import os
import json
from typing import Dict, List, Any, Optional
from linebot.v3.messaging import (
    QuickReply,
    QuickReplyItem,
    TextMessage,
    FlexMessage,
    MessageAction,
    ButtonsTemplate,
    TemplateMessage,
    CarouselTemplate,
    CarouselColumn,
)

# === 星座運勢相關 UI ===

# 星座中英文對照表
HOROSCOPE_SIGNS = {
    "白羊座": "Aries", "金牛座": "Taurus", "雙子座": "Gemini",
    "巨蟹座": "Cancer", "獅子座": "Leo", "處女座": "Virgo",
    "天秤座": "Libra", "天蠍座": "Scorpio", "射手座": "Sagittarius",
    "摩羯座": "Capricorn", "水瓶座": "Aquarius", "雙魚座": "Pisces"
}

# 星座對應表情符號
ZODIAC_EMOJI = {
    "白羊座": "♈", "金牛座": "♉", "雙子座": "♊",
    "巨蟹座": "♋", "獅子座": "♌", "處女座": "♍",
    "天秤座": "♎", "天蠍座": "♏", "射手座": "♐",
    "摩羯座": "♑", "水瓶座": "♒", "雙魚座": "♓"
}

def create_zodiac_quick_reply() -> QuickReply:
    """
    創建星座快速回覆按鈕
    
    Returns:
        QuickReply: 包含12個星座按鈕的快速回覆物件
    """
    items = []
    
    # 前6個星座
    for sign_ch, emoji in list(ZODIAC_EMOJI.items())[:6]:
        items.append(
            QuickReplyItem(
                action=MessageAction(
                    label=f"{emoji} {sign_ch}",
                    text=f"{sign_ch}今日運勢"
                )
            )
        )
    
    return QuickReply(items=items)

def create_zodiac_carousel() -> TemplateMessage:
    """
    創建星座輪播選單
    
    Returns:
        TemplateMessage: 包含全部星座的輪播選單
    """
    columns = []
    
    # 將星座分成4組，每組3個
    sign_groups = [list(ZODIAC_EMOJI.items())[i:i+3] for i in range(0, 12, 3)]
    
    for group in sign_groups:
        actions = []
        title = "選擇星座查詢運勢"
        text = ""
        
        for sign_ch, emoji in group:
            text += f"{emoji} {sign_ch}\n"
            actions.append(
                MessageAction(
                    label=sign_ch,
                    text=f"{sign_ch}今日運勢"
                )
            )
        
        columns.append(
            CarouselColumn(
                title=title,
                text=text.strip(),
                actions=actions
            )
        )
    
    carousel_template = CarouselTemplate(columns=columns)
    return TemplateMessage(alt_text="星座運勢選單", template=carousel_template)

# === 塔羅牌相關 UI ===

def create_tarot_buttons() -> TemplateMessage:
    """
    創建塔羅牌功能按鈕
    
    Returns:
        TemplateMessage: 包含塔羅牌功能按鈕的訊息
    """
    buttons_template = ButtonsTemplate(
        title="塔羅牌占卜",
        text="請選擇您想要的占卜方式",
        actions=[
            MessageAction(
                label="🎴 隨機抽一張牌",
                text="幫我隨機抽一張塔羅牌"
            ),
            MessageAction(
                label="🔮 針對問題占卜",
                text="我想針對一個問題進行塔羅占卜"
            )
        ]
    )
    
    return TemplateMessage(alt_text="塔羅牌占卜選單", template=buttons_template)

def create_main_menu_flex() -> FlexMessage:
    """
    創建主選單 Flex 訊息
    
    Returns:
        FlexMessage: 包含主要功能的 Flex 訊息
    """
    # 引入 get_liff_url 函數
    from .line_liff import get_liff_url
    
    # 主選單的 Flex 訊息 JSON 結構
    flex_json = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.imgur.com/TIlPJDX.png",
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
                    "text": "LINE 占卜 & 心情陪伴 AI 師",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#7D2EBD"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "請點選下方按鈕選擇功能",
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "md",
                                    "flex": 5
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
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "✨ 今日運勢",
                        "text": "今日運勢"
                    },
                    "color": "#7D2EBD"
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🔮 塔羅牌占卜",
                        "text": "我想抽塔羅牌"
                    },
                    "color": "#9B59B6"
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "💫 星座運勢",
                        "text": "查看星座運勢"
                    },
                    "color": "#2E86C1"
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "📝 心情日記",
                        "text": "我要寫心情日記"
                    },
                    "color": "#27AE60"
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "💭 心情諮詢",
                        "text": "我想談談我的心情"
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "📊 個人化空間",
                        "text": "打開個人化空間"
                    },
                    "color": "#FF8C00"
                }
            ],
            "flex": 0
        }
    }

    return FlexMessage(alt_text="主選單", contents=flex_json)


# === 每日運勢相關 UI ===
def create_daily_fortune_flex() -> FlexMessage:
    """
    創建今日運勢 Flex 訊息
    
    Returns:
        FlexMessage: 今日運勢選單的 Flex 訊息
    """
    today = "2025年7月12日" # 這裡使用固定日期，實際應用中可使用 datetime 獲取當前日期
    
    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "✨ 今日運勢 ✨",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "color": "#7D2EBD"
                },
                {
                    "type": "text",
                    "text": today,
                    "size": "sm",
                    "align": "center",
                    "margin": "md",
                    "color": "#888888"
                },
                {
                    "type": "separator",
                    "margin": "lg"
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
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "塔羅指引",
                                            "weight": "bold",
                                            "size": "md"
                                        },
                                        {
                                            "type": "text",
                                            "text": "今日幸運塔羅牌",
                                            "size": "xs",
                                            "color": "#888888",
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "抽取",
                                        "text": "幫我抽一張今日幸運塔羅牌"
                                    },
                                    "style": "primary",
                                    "color": "#9B59B6",
                                    "height": "sm"
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "星座運勢",
                                            "weight": "bold",
                                            "size": "md"
                                        },
                                        {
                                            "type": "text",
                                            "text": "查看您的星座今日運勢",
                                            "size": "xs",
                                            "color": "#888888",
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "選擇星座",
                                        "text": "查看星座運勢"
                                    },
                                    "style": "primary",
                                    "color": "#2E86C1",
                                    "height": "sm"
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "全面運勢解析",
                                            "weight": "bold",
                                            "size": "md"
                                        },
                                        {
                                            "type": "text",
                                            "text": "個人化的綜合運勢分析",
                                            "size": "xs",
                                            "color": "#888888",
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "分析",
                                        "text": "請幫我做今日全面運勢分析"
                                    },
                                    "style": "primary",
                                    "color": "#7D2EBD",
                                    "height": "sm"
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
    
    return FlexMessage(alt_text="今日運勢", contents=flex_json)


# === 心情日記相關 UI ===
def create_mood_diary_flex() -> FlexMessage:
    """
    創建心情日記 Flex 訊息
    
    Returns:
        FlexMessage: 心情日記選單的 Flex 訊息
    """
    today = "2025年7月12日" # 這裡使用固定日期，實際應用中可使用 datetime 獲取當前日期
    
    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📝 心情日記",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "color": "#27AE60"
                },
                {
                    "type": "text",
                    "text": today,
                    "size": "sm",
                    "align": "center",
                    "margin": "md",
                    "color": "#888888"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": "您今天感覺如何？",
                    "margin": "lg",
                    "size": "md",
                    "align": "center"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "😄 開心",
                                "text": "今天我感到很開心，因為..."
                            },
                            "style": "secondary",
                            "height": "sm",
                            "color": "#FFD700"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "😊 平靜",
                                "text": "今天我感到平靜，因為..."
                            },
                            "style": "secondary",
                            "height": "sm",
                            "color": "#87CEFA"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "😔 憂傷",
                                "text": "今天我感到有點憂傷，因為..."
                            },
                            "style": "secondary",
                            "height": "sm",
                            "color": "#B0C4DE"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "😠 生氣",
                                "text": "今天我感到生氣，因為..."
                            },
                            "style": "secondary",
                            "height": "sm",
                            "color": "#FA8072"
                        }
                    ]
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "lg",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "情緒分析",
                                    "weight": "bold",
                                    "size": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "分析您的情緒變化趨勢",
                                    "size": "xs",
                                    "color": "#888888",
                                    "margin": "sm"
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "分析",
                                "text": "請幫我分析最近的情緒變化"
                            },
                            "style": "primary",
                            "color": "#27AE60",
                            "height": "sm"
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
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "自由記錄心情",
                        "text": "我想記錄今天的心情："
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
    
    return FlexMessage(alt_text="心情日記", contents=flex_json)

# 建立星座運勢 Flex 訊息
def create_horoscope_menu_flex() -> FlexMessage:
    """
    創建星座運勢選擇 Flex 訊息
    
    Returns:
        FlexMessage: 包含所有星座選項的 Flex 訊息
    """
    contents = []
    
    # 將星座分成兩行，每行6個
    zodiac_items = list(ZODIAC_EMOJI.items())
    first_row = zodiac_items[:6]
    second_row = zodiac_items[6:]
    
    # 第一行星座
    first_row_box = {
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "contents": []
    }
    
    for sign_ch, emoji in first_row:
        first_row_box["contents"].append({
            "type": "button",
            "style": "link",
            "height": "sm",
            "action": {
                "type": "message",
                "label": f"{emoji} {sign_ch}",
                "text": f"{sign_ch}今日運勢"
            }
        })
    
    # 第二行星座
    second_row_box = {
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "contents": []
    }
    
    for sign_ch, emoji in second_row:
        second_row_box["contents"].append({
            "type": "button",
            "style": "link",
            "height": "sm",
            "action": {
                "type": "message",
                "label": f"{emoji} {sign_ch}",
                "text": f"{sign_ch}今日運勢"
            }
        })
    
    # 主要 Flex 訊息結構
    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "星座運勢",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#2E86C1"
                },
                {
                    "type": "text",
                    "text": "請選擇您的星座",
                    "margin": "md",
                    "size": "md",
                    "color": "#666666"
                },
                first_row_box,
                second_row_box
            ]
        }
    }
    
    return FlexMessage(alt_text="星座運勢選單", contents=flex_json)

# 建立處理使用者輸入的輔助函數
def check_for_menu_keywords(text: str) -> Optional[str]:
    """
    檢查使用者輸入是否包含選單關鍵字
    
    Args:
        text (str): 使用者輸入的文字
        
    Returns:
        Optional[str]: 如果包含關鍵字，返回對應的選單類型，否則返回 None
    """
    text = text.lower()
    
    # 檢查主選單關鍵字
    if any(keyword in text for keyword in ["選單", "功能", "menu", "幫助", "說明", "help"]):
        return "main_menu"
    
    # 檢查塔羅牌選單關鍵字（但排除具體的抽牌請求）
    elif any(keyword in text for keyword in ["塔羅", "tarot", "占卜"]) and not any(request in text for request in ["抽牌", "抽一張", "隨機抽", "給我抽"]):
        return "tarot_menu"
    
    # 檢查星座關鍵字
    elif any(keyword in text for keyword in ["星座", "horoscope", "zodiac"]):
        return "horoscope_menu"
        
    # 檢查每日運勢關鍵字
    elif any(keyword in text for keyword in ["今日運勢", "每日運勢", "今天運勢", "daily fortune"]):
        return "daily_fortune"
        
    # 檢查心情日記關鍵字
    elif any(keyword in text for keyword in ["心情日記", "記錄心情", "情緒日記", "mood diary", "心情記錄"]):
        return "mood_diary"
    
    return None


def check_for_zodiac_sign(text: str) -> Optional[str]:
    """
    檢查使用者輸入是否包含星座名稱
    
    Args:
        text (str): 使用者輸入的文字
        
    Returns:
        Optional[str]: 如果包含星座名稱，返回星座名稱，否則返回 None
    """
    text = text.lower()
    
    for zodiac_sign in HOROSCOPE_SIGNS.keys():
        if zodiac_sign.lower() in text:
            return zodiac_sign
            
    # 檢查英文星座名稱
    for zodiac_ch, zodiac_en in HOROSCOPE_SIGNS.items():
        if zodiac_en.lower() in text:
            return zodiac_ch
            
    return None
