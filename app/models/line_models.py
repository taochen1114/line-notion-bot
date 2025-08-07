"""
Line Bot 訊息模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LineUser(BaseModel):
    """Line 用戶模型"""
    user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None


class LineMessage(BaseModel):
    """Line 訊息基礎模型"""
    id: str
    type: str
    timestamp: int
    mode: str


class TextMessage(LineMessage):
    """文字訊息模型"""
    text: str
    
    @property
    def is_search_query(self) -> bool:
        """檢查是否為搜尋查詢"""
        return len(self.text.strip()) > 0


class LineEvent(BaseModel):
    """Line 事件模型"""
    type: str
    mode: str
    timestamp: int
    source: Dict[str, Any]
    reply_token: Optional[str] = None
    message: Optional[Dict[str, Any]] = None
    
    @property
    def user_id(self) -> Optional[str]:
        """取得用戶 ID"""
        return self.source.get("userId")
    
    @property
    def is_message_event(self) -> bool:
        """檢查是否為訊息事件"""
        return self.type == "message"
    
    @property
    def is_text_message(self) -> bool:
        """檢查是否為文字訊息"""
        return (self.is_message_event and 
                self.message and 
                self.message.get("type") == "text")
    
    @property
    def text_content(self) -> Optional[str]:
        """取得文字內容"""
        if self.is_text_message:
            return self.message.get("text")
        return None


class SearchResult(BaseModel):
    """搜尋結果模型"""
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    def to_line_message(self) -> str:
        """轉換為 Line 訊息格式"""
        message_parts = [f"📄 {self.title}"]
        
        if self.content:
            # 限制內容長度
            content = self.content[:200] + "..." if len(self.content) > 200 else self.content
            message_parts.append(f"\n{content}")
        
        if self.tags:
            tags_str = " ".join([f"#{tag}" for tag in self.tags])
            message_parts.append(f"\n🏷️ {tags_str}")
        
        if self.url:
            message_parts.append(f"\n🔗 {self.url}")
        
        return "".join(message_parts)


class SearchResponse(BaseModel):
    """搜尋回應模型"""
    query: str
    results: List[SearchResult] = Field(default_factory=list)
    total_count: int = 0
    
    def to_line_messages(self) -> List[str]:
        """轉換為 Line 訊息列表"""
        if not self.results:
            return [f"🔍 搜尋「{self.query}」沒有找到相關內容"]
        
        messages = [f"🔍 搜尋「{self.query}」找到 {self.total_count} 個結果：\n"]
        
        for i, result in enumerate(self.results, 1):
            message = f"{i}. {result.to_line_message()}"
            messages.append(message)
        
        return messages


class LineReplyMessage(BaseModel):
    """Line 回覆訊息模型"""
    type: str = "text"
    text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "type": self.type,
            "text": self.text
        }


class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    error_code: str
    message: str
    user_message: str
    
    def to_line_message(self) -> LineReplyMessage:
        """轉換為 Line 回覆訊息"""
        return LineReplyMessage(text=self.user_message)