"""
Line Bot 服務模組
"""
import hashlib
import hmac
import base64
from typing import List, Optional, Dict, Any
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
from ..config import get_settings
from ..models.line_models import LineEvent, SearchResponse, ErrorResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LineService:
    """Line Bot 服務類別"""
    
    def __init__(self):
        self.settings = get_settings()
        self.line_bot_api = LineBotApi(self.settings.line_channel_access_token)
        self.handler = WebhookHandler(self.settings.line_channel_secret)
    
    def verify_signature(self, body: bytes, signature: str) -> bool:
        """驗證 Line Webhook 簽名"""
        try:
            hash_value = hmac.new(
                self.settings.line_channel_secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
            
            expected_signature = base64.b64encode(hash_value).decode('utf-8')
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"驗證簽名時發生錯誤", error=e)
            return False
    
    def parse_webhook_body(self, body: Dict[str, Any]) -> List[LineEvent]:
        """解析 Webhook 請求體"""
        try:
            events = []
            
            for event_data in body.get("events", []):
                event = LineEvent(**event_data)
                events.append(event)
            
            logger.info(f"解析到 {len(events)} 個事件")
            return events
            
        except Exception as e:
            logger.error(f"解析 Webhook 請求體時發生錯誤", error=e)
            return []
    
    async def reply_message(self, reply_token: str, messages: List[str]) -> bool:
        """回覆訊息"""
        try:
            if not reply_token:
                logger.warning("回覆 token 為空，無法回覆訊息")
                return False
            
            # 轉換為 Line 訊息格式
            line_messages = []
            for message in messages:
                if len(message.strip()) > 0:
                    # Line 訊息長度限制為 5000 字元
                    if len(message) > 5000:
                        message = message[:4997] + "..."
                    
                    line_messages.append(TextSendMessage(text=message))
            
            if not line_messages:
                logger.warning("沒有有效的訊息內容可回覆")
                return False
            
            # Line API 一次最多可發送 5 則訊息
            if len(line_messages) > 5:
                line_messages = line_messages[:5]
            
            # 發送回覆
            self.line_bot_api.reply_message(reply_token, line_messages)
            
            logger.info(f"成功回覆 {len(line_messages)} 則訊息")
            return True
            
        except LineBotApiError as e:
            logger.error(f"Line API 錯誤", error=e)
            return False
        except Exception as e:
            logger.error(f"回覆訊息時發生錯誤", error=e)
            return False
    
    async def reply_search_results(self, reply_token: str, search_response: SearchResponse) -> bool:
        """回覆搜尋結果"""
        try:
            messages = search_response.to_line_messages()
            
            # 如果沒有結果，提供搜尋建議
            if not search_response.results:
                messages.append(self._get_search_suggestions())
            
            return await self.reply_message(reply_token, messages)
            
        except Exception as e:
            logger.error(f"回覆搜尋結果時發生錯誤", error=e)
            return False
    
    async def reply_error(self, reply_token: str, error_response: ErrorResponse) -> bool:
        """回覆錯誤訊息"""
        try:
            message = error_response.to_line_message()
            return await self.reply_message(reply_token, [message.text])
            
        except Exception as e:
            logger.error(f"回覆錯誤訊息時發生錯誤", error=e)
            return False
    
    async def reply_help_message(self, reply_token: str) -> bool:
        """回覆幫助訊息"""
        try:
            help_text = self._get_help_message()
            return await self.reply_message(reply_token, [help_text])
            
        except Exception as e:
            logger.error(f"回覆幫助訊息時發生錯誤", error=e)
            return False
    
    def _get_help_message(self) -> str:
        """取得幫助訊息"""
        return """🤖 Notion 知識庫搜尋機器人

📖 使用方法：
• 直接輸入關鍵字進行搜尋
• 例如：「Python」、「API 設計」、「資料庫」

🔍 搜尋功能：
• 搜尋頁面標題
• 搜尋頁面內容
• 搜尋標籤

💡 小提示：
• 使用具體的關鍵字可以得到更精確的結果
• 支援中文和英文搜尋
• 每次最多顯示 5 個結果

如有問題，請聯繫管理員。"""
    
    def _get_search_suggestions(self) -> str:
        """取得搜尋建議"""
        return """💡 搜尋建議：
• 嘗試使用不同的關鍵字
• 使用更具體或更廣泛的搜尋詞
• 檢查拼寫是否正確
• 嘗試使用同義詞

輸入「幫助」查看使用說明。"""
    
    def create_quick_reply_buttons(self, suggestions: List[str]) -> Optional[QuickReply]:
        """建立快速回覆按鈕"""
        try:
            if not suggestions:
                return None
            
            buttons = []
            for suggestion in suggestions[:13]:  # Line 快速回覆最多 13 個按鈕
                button = QuickReplyButton(
                    action=MessageAction(
                        label=suggestion,
                        text=suggestion
                    )
                )
                buttons.append(button)
            
            return QuickReply(items=buttons)
            
        except Exception as e:
            logger.error(f"建立快速回覆按鈕時發生錯誤", error=e)
            return None
    
    async def push_message(self, user_id: str, messages: List[str]) -> bool:
        """主動推送訊息"""
        try:
            line_messages = []
            for message in messages:
                if len(message.strip()) > 0:
                    if len(message) > 5000:
                        message = message[:4997] + "..."
                    line_messages.append(TextSendMessage(text=message))
            
            if not line_messages:
                return False
            
            if len(line_messages) > 5:
                line_messages = line_messages[:5]
            
            self.line_bot_api.push_message(user_id, line_messages)
            
            logger.info(f"成功推送 {len(line_messages)} 則訊息給用戶 {user_id}")
            return True
            
        except LineBotApiError as e:
            logger.error(f"推送訊息時發生 Line API 錯誤", error=e)
            return False
        except Exception as e:
            logger.error(f"推送訊息時發生錯誤", error=e)
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """取得用戶資料"""
        try:
            profile = self.line_bot_api.get_profile(user_id)
            
            return {
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "picture_url": profile.picture_url,
                "status_message": profile.status_message
            }
            
        except LineBotApiError as e:
            logger.error(f"取得用戶資料時發生 Line API 錯誤", error=e)
            return None
        except Exception as e:
            logger.error(f"取得用戶資料時發生錯誤", error=e)
            return None
    
    def is_valid_reply_token(self, reply_token: str) -> bool:
        """檢查回覆 token 是否有效"""
        return reply_token and reply_token != "00000000000000000000000000000000"
    
    def extract_search_query(self, text: str) -> Optional[str]:
        """提取搜尋查詢"""
        if not text:
            return None
        
        text = text.strip()
        
        # 處理特殊指令
        if text.lower() in ["help", "幫助", "說明", "?"]:
            return None
        
        # 移除常見的搜尋前綴
        prefixes = ["搜尋", "search", "找", "查", "查詢"]
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                break
        
        # 檢查查詢長度
        if len(text) < 1:
            return None
        
        if len(text) > 100:
            text = text[:100]
        
        return text