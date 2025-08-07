"""
Notion 服務測試
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.notion_service import NotionService
from app.models.line_models import SearchResponse, SearchResult


@pytest.fixture
def notion_service():
    """建立 NotionService 實例"""
    with patch('app.services.notion_service.get_settings') as mock_settings:
        mock_settings.return_value.notion_api_token = "test_token"
        mock_settings.return_value.notion_database_id = "test_db_id"
        mock_settings.return_value.max_search_results = 5
        
        service = NotionService()
        return service


@pytest.fixture
def mock_notion_response():
    """模擬 Notion API 回應"""
    return {
        "results": [
            {
                "id": "test_page_1",
                "url": "https://notion.so/test_page_1",
                "created_time": "2023-01-01T00:00:00.000Z",
                "last_edited_time": "2023-01-02T00:00:00.000Z",
                "properties": {
                    "Name": {
                        "type": "title",
                        "title": [
                            {
                                "plain_text": "測試頁面 1"
                            }
                        ]
                    },
                    "Tags": {
                        "type": "multi_select",
                        "multi_select": [
                            {"name": "測試"},
                            {"name": "Python"}
                        ]
                    }
                }
            }
        ]
    }


@pytest.fixture
def mock_blocks_response():
    """模擬 Notion 區塊回應"""
    return {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "plain_text": "這是測試內容"
                        }
                    ]
                }
            }
        ]
    }


class TestNotionService:
    """NotionService 測試類別"""
    
    @pytest.mark.asyncio
    async def test_search_database_success(self, notion_service, mock_notion_response, mock_blocks_response):
        """測試成功搜尋資料庫"""
        with patch.object(notion_service, '_perform_search', return_value=mock_notion_response), \
             patch.object(notion_service, '_extract_content', return_value="這是測試內容"):
            
            result = await notion_service.search_database("測試查詢")
            
            assert isinstance(result, SearchResponse)
            assert result.query == "測試查詢"
            assert len(result.results) == 1
            assert result.total_count == 1
            assert result.results[0].title == "測試頁面 1"
    
    @pytest.mark.asyncio
    async def test_search_database_empty_results(self, notion_service):
        """測試搜尋無結果"""
        with patch.object(notion_service, '_perform_search', return_value={"results": []}):
            
            result = await notion_service.search_database("不存在的查詢")
            
            assert isinstance(result, SearchResponse)
            assert result.query == "不存在的查詢"
            assert len(result.results) == 0
            assert result.total_count == 0
    
    @pytest.mark.asyncio
    async def test_search_database_exception(self, notion_service):
        """測試搜尋時發生例外"""
        with patch.object(notion_service, '_perform_search', side_effect=Exception("API 錯誤")):
            
            result = await notion_service.search_database("測試查詢")
            
            assert isinstance(result, SearchResponse)
            assert result.query == "測試查詢"
            assert len(result.results) == 0
            assert result.total_count == 0
    
    def test_extract_title_success(self, notion_service):
        """測試成功提取標題"""
        item = {
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [
                        {"plain_text": "測試標題"}
                    ]
                }
            }
        }
        
        title = notion_service._extract_title(item)
        assert title == "測試標題"
    
    def test_extract_title_no_title(self, notion_service):
        """測試沒有標題的情況"""
        item = {"properties": {}}
        
        title = notion_service._extract_title(item)
        assert title == "無標題"
    
    def test_extract_tags_success(self, notion_service):
        """測試成功提取標籤"""
        item = {
            "properties": {
                "Tags": {
                    "type": "multi_select",
                    "multi_select": [
                        {"name": "標籤1"},
                        {"name": "標籤2"}
                    ]
                }
            }
        }
        
        tags = notion_service._extract_tags(item)
        assert tags == ["標籤1", "標籤2"]
    
    def test_extract_tags_no_tags(self, notion_service):
        """測試沒有標籤的情況"""
        item = {"properties": {}}
        
        tags = notion_service._extract_tags(item)
        assert tags == []
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, notion_service):
        """測試連線成功"""
        with patch.object(notion_service.client.databases, 'retrieve', return_value={"id": "test"}):
            result = await notion_service.test_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, notion_service):
        """測試連線失敗"""
        with patch.object(notion_service.client.databases, 'retrieve', side_effect=Exception("連線錯誤")):
            result = await notion_service.test_connection()
            assert result is False