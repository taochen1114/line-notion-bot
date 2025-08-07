"""
Line 服務測試
"""
import pytest
from unittest.mock import Mock, patch
from app.services.line_service import LineService
from app.models.line_models import LineEvent, SearchResponse, SearchResult, ErrorResponse


@pytest.fixture
def line_service():
    """建立 LineService 實例"""
    with patch('app.services.line_service.get_settings') as mock_settings:
        mock_settings.return_value.line_channel_access_token = "test_token"
        mock_settings.return_value.line_channel_secret = "test_secret"
        
        service = LineService()
        return service


@pytest.fixture
def sample_line_event():
    """範例 Line 事件"""
    return LineEvent(
        type="message",
        mode="active",
        timestamp=1234567890,
        source={"userId": "test_user_id", "type": "user"},
        reply_token="test_reply_token",
        message={
            "type": "text",
            "text": "測試訊息"
        }
    )


@pytest.fixture
def sample_search_response():
    """範例搜尋回應"""
    results = [
        SearchResult(
            title="測試頁面 1",
            content="這是測試內容 1",
            url="https://notion.so/test1",
            tags=["測試", "Python"]
        ),
        SearchResult(
            title="測試頁面 2",
            content="這是測試內容 2",
            url="https://notion.so/test2",
            tags=["測試", "API"]
        )
    ]
    
    return SearchResponse(
        query="測試查詢",
        results=results,
        total_count=2
    )


class TestLineService:
    """LineService 測試類別"""
    
    def test_verify_signature_success(self, line_service):
        """測試簽名驗證成功"""
        body = b'{"test": "data"}'
        
        # 模擬正確的簽名
        with patch('hmac.compare_digest', return_value=True):
            result = line_service.verify_signature(body, "valid_signature")
            assert result is True
    
    def test_verify_signature_failure(self, line_service):
        """測試簽名驗證失敗"""
        body = b'{"test": "data"}'
        
        # 模擬錯誤的簽名
        with patch('hmac.compare_digest', return_value=False):
            result = line_service.verify_signature(body, "invalid_signature")
            assert result is False
    
    def test_parse_webhook_body_success(self, line_service):
        """測試成功解析 Webhook 請求體"""
        body = {
            "events": [
                {
                    "type": "message",
                    "mode": "active",
                    "timestamp": 1234567890,
                    "source": {"userId": "test_user", "type": "user"},
                    "reply_token": "test_token",
                    "message": {"type": "text", "text": "Hello"}
                }
            ]
        }
        
        events = line_service.parse_webhook_body(body)
        
        assert len(events) == 1
        assert events[0].type == "message"
        assert events[0].user_id == "test_user"
        assert events[0].text_content == "Hello"
    
    def test_parse_webhook_body_empty(self, line_service):
        """測試解析空的 Webhook 請求體"""
        body = {"events": []}
        
        events = line_service.parse_webhook_body(body)
        
        assert len(events) == 0
    
    @pytest.mark.asyncio
    async def test_reply_message_success(self, line_service):
        """測試成功回覆訊息"""
        with patch.object(line_service.line_bot_api, 'reply_message') as mock_reply:
            result = await line_service.reply_message("test_token", ["測試訊息"])
            
            assert result is True
            mock_reply.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reply_message_empty_token(self, line_service):
        """測試空的回覆 token"""
        result = await line_service.reply_message("", ["測試訊息"])
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reply_message_empty_messages(self, line_service):
        """測試空的訊息列表"""
        result = await line_service.reply_message("test_token", [])
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reply_search_results_with_results(self, line_service, sample_search_response):
        """測試回覆有結果的搜尋"""
        with patch.object(line_service, 'reply_message', return_value=True) as mock_reply:
            result = await line_service.reply_search_results("test_token", sample_search_response)
            
            assert result is True
            mock_reply.assert_called_once()
            
            # 檢查傳遞的訊息
            args, kwargs = mock_reply.call_args
            messages = args[1]
            assert len(messages) > 0
            assert "測試查詢" in messages[0]
    
    @pytest.mark.asyncio
    async def test_reply_search_results_no_results(self, line_service):
        """測試回覆無結果的搜尋"""
        empty_response = SearchResponse(query="無結果查詢", results=[], total_count=0)
        
        with patch.object(line_service, 'reply_message', return_value=True) as mock_reply:
            result = await line_service.reply_search_results("test_token", empty_response)
            
            assert result is True
            mock_reply.assert_called_once()
            
            # 檢查傳遞的訊息包含搜尋建議
            args, kwargs = mock_reply.call_args
            messages = args[1]
            assert len(messages) >= 2  # 無結果訊息 + 搜尋建議
    
    @pytest.mark.asyncio
    async def test_reply_error(self, line_service):
        """測試回覆錯誤訊息"""
        error_response = ErrorResponse(
            error_code="TEST_ERROR",
            message="測試錯誤",
            user_message="發生錯誤，請稍後再試"
        )
        
        with patch.object(line_service, 'reply_message', return_value=True) as mock_reply:
            result = await line_service.reply_error("test_token", error_response)
            
            assert result is True
            mock_reply.assert_called_once()
            
            # 檢查傳遞的訊息
            args, kwargs = mock_reply.call_args
            messages = args[1]
            assert messages[0] == "發生錯誤，請稍後再試"
    
    @pytest.mark.asyncio
    async def test_reply_help_message(self, line_service):
        """測試回覆幫助訊息"""
        with patch.object(line_service, 'reply_message', return_value=True) as mock_reply:
            result = await line_service.reply_help_message("test_token")
            
            assert result is True
            mock_reply.assert_called_once()
            
            # 檢查幫助訊息內容
            args, kwargs = mock_reply.call_args
            messages = args[1]
            assert "使用方法" in messages[0]
    
    def test_extract_search_query_normal(self, line_service):
        """測試提取正常搜尋查詢"""
        query = line_service.extract_search_query("Python 教學")
        assert query == "Python 教學"
    
    def test_extract_search_query_with_prefix(self, line_service):
        """測試提取帶前綴的搜尋查詢"""
        query = line_service.extract_search_query("搜尋 Python 教學")
        assert query == "Python 教學"
        
        query = line_service.extract_search_query("search API 設計")
        assert query == "API 設計"
    
    def test_extract_search_query_help_command(self, line_service):
        """測試幫助指令"""
        query = line_service.extract_search_query("help")
        assert query is None
        
        query = line_service.extract_search_query("幫助")
        assert query is None
    
    def test_extract_search_query_empty(self, line_service):
        """測試空查詢"""
        query = line_service.extract_search_query("")
        assert query is None
        
        query = line_service.extract_search_query("   ")
        assert query is None
    
    def test_extract_search_query_too_long(self, line_service):
        """測試過長的查詢"""
        long_query = "a" * 150
        query = line_service.extract_search_query(long_query)
        assert len(query) == 100
    
    def test_is_valid_reply_token(self, line_service):
        """測試回覆 token 驗證"""
        assert line_service.is_valid_reply_token("valid_token") is True
        assert line_service.is_valid_reply_token("") is False
        assert line_service.is_valid_reply_token(None) is False
        assert line_service.is_valid_reply_token("00000000000000000000000000000000") is False
    
    def test_get_user_profile_success(self, line_service):
        """測試成功取得用戶資料"""
        mock_profile = Mock()
        mock_profile.user_id = "test_user"
        mock_profile.display_name = "測試用戶"
        mock_profile.picture_url = "https://example.com/pic.jpg"
        mock_profile.status_message = "測試狀態"
        
        with patch.object(line_service.line_bot_api, 'get_profile', return_value=mock_profile):
            profile = line_service.get_user_profile("test_user")
            
            assert profile is not None
            assert profile["user_id"] == "test_user"
            assert profile["display_name"] == "測試用戶"
    
    def test_get_user_profile_failure(self, line_service):
        """測試取得用戶資料失敗"""
        with patch.object(line_service.line_bot_api, 'get_profile', side_effect=Exception("API 錯誤")):
            profile = line_service.get_user_profile("test_user")
            assert profile is None