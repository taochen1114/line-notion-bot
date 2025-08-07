"""
Notion API 服務模組
"""
import asyncio
from typing import List, Optional, Dict, Any
from notion_client import Client
from notion_client.errors import APIResponseError, RequestTimeoutError
from ..config import get_settings
from ..models.line_models import SearchResult, SearchResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NotionService:
    """Notion API 服務類別"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Client(auth=self.settings.notion_api_token)
        self.database_id = self.settings.notion_database_id
    
    async def search_database(self, query: str) -> SearchResponse:
        """搜尋 Notion 資料庫"""
        try:
            logger.info(f"開始搜尋 Notion 資料庫，查詢：{query}")
            
            # 執行搜尋
            search_results = await self._perform_search(query)
            
            # 處理搜尋結果
            results = []
            for item in search_results.get("results", []):
                result = await self._process_search_result(item)
                if result:
                    results.append(result)
            
            total_count = len(results)
            
            # 限制結果數量
            max_results = self.settings.max_search_results
            if len(results) > max_results:
                results = results[:max_results]
            
            logger.info(f"搜尋完成，找到 {total_count} 個結果，返回前 {len(results)} 個")
            
            return SearchResponse(
                query=query,
                results=results,
                total_count=total_count
            )
            
        except Exception as e:
            logger.error(f"搜尋 Notion 資料庫時發生錯誤", error=e)
            return SearchResponse(query=query, results=[], total_count=0)
    
    async def _perform_search(self, query: str) -> Dict[str, Any]:
        """執行 Notion 搜尋"""
        try:
            # 使用 asyncio 執行同步的 Notion API 調用
            loop = asyncio.get_event_loop()
            
            # 先嘗試在資料庫中搜尋
            database_results = await loop.run_in_executor(
                None,
                lambda: self.client.databases.query(
                    database_id=self.database_id,
                    filter={
                        "or": [
                            {
                                "property": "Name",
                                "title": {
                                    "contains": query
                                }
                            },
                            {
                                "property": "Tags",
                                "multi_select": {
                                    "contains": query
                                }
                            }
                        ]
                    },
                    sorts=[
                        {
                            "property": "Last edited time",
                            "direction": "descending"
                        }
                    ]
                )
            )
            
            # 如果資料庫搜尋結果不足，再進行全域搜尋
            if len(database_results.get("results", [])) < self.settings.max_search_results:
                global_results = await loop.run_in_executor(
                    None,
                    lambda: self.client.search(
                        query=query,
                        filter={
                            "property": "object",
                            "value": "page"
                        },
                        sort={
                            "direction": "descending",
                            "timestamp": "last_edited_time"
                        }
                    )
                )
                
                # 合併結果並去重
                all_results = database_results.get("results", [])
                existing_ids = {result["id"] for result in all_results}
                
                for result in global_results.get("results", []):
                    if result["id"] not in existing_ids:
                        all_results.append(result)
                
                database_results["results"] = all_results
            
            return database_results
            
        except APIResponseError as e:
            logger.error(f"Notion API 回應錯誤", error=e)
            raise
        except RequestTimeoutError as e:
            logger.error(f"Notion API 請求超時", error=e)
            raise
        except Exception as e:
            logger.error(f"執行 Notion 搜尋時發生未知錯誤", error=e)
            raise
    
    async def _process_search_result(self, item: Dict[str, Any]) -> Optional[SearchResult]:
        """處理單個搜尋結果"""
        try:
            # 取得頁面標題
            title = self._extract_title(item)
            if not title:
                return None
            
            # 取得頁面內容
            content = await self._extract_content(item["id"])
            
            # 取得頁面 URL
            url = item.get("url")
            
            # 取得時間資訊
            created_time = item.get("created_time")
            last_edited_time = item.get("last_edited_time")
            
            # 取得標籤
            tags = self._extract_tags(item)
            
            return SearchResult(
                title=title,
                content=content,
                url=url,
                created_time=created_time,
                last_edited_time=last_edited_time,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"處理搜尋結果時發生錯誤", error=e)
            return None
    
    def _extract_title(self, item: Dict[str, Any]) -> Optional[str]:
        """提取頁面標題"""
        try:
            properties = item.get("properties", {})
            
            # 嘗試不同的標題屬性名稱
            title_properties = ["Name", "Title", "名稱", "標題"]
            
            for prop_name in title_properties:
                if prop_name in properties:
                    prop = properties[prop_name]
                    if prop.get("type") == "title":
                        title_array = prop.get("title", [])
                        if title_array:
                            return "".join([t.get("plain_text", "") for t in title_array])
            
            # 如果沒有找到標題屬性，使用第一個文字屬性
            for prop_name, prop in properties.items():
                if prop.get("type") == "rich_text":
                    text_array = prop.get("rich_text", [])
                    if text_array:
                        return "".join([t.get("plain_text", "") for t in text_array])
            
            return "無標題"
            
        except Exception as e:
            logger.error(f"提取標題時發生錯誤", error=e)
            return "無標題"
    
    async def _extract_content(self, page_id: str) -> Optional[str]:
        """提取頁面內容"""
        try:
            loop = asyncio.get_event_loop()
            
            # 取得頁面區塊
            blocks = await loop.run_in_executor(
                None,
                lambda: self.client.blocks.children.list(block_id=page_id)
            )
            
            content_parts = []
            for block in blocks.get("results", []):
                text = self._extract_block_text(block)
                if text:
                    content_parts.append(text)
            
            content = "\n".join(content_parts)
            
            # 限制內容長度
            if len(content) > 500:
                content = content[:500] + "..."
            
            return content if content else None
            
        except Exception as e:
            logger.error(f"提取頁面內容時發生錯誤", error=e)
            return None
    
    def _extract_block_text(self, block: Dict[str, Any]) -> Optional[str]:
        """提取區塊文字"""
        try:
            block_type = block.get("type")
            if not block_type:
                return None
            
            block_data = block.get(block_type, {})
            
            # 處理不同類型的區塊
            if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
                rich_text = block_data.get("rich_text", [])
                return "".join([t.get("plain_text", "") for t in rich_text])
            
            return None
            
        except Exception as e:
            logger.error(f"提取區塊文字時發生錯誤", error=e)
            return None
    
    def _extract_tags(self, item: Dict[str, Any]) -> List[str]:
        """提取標籤"""
        try:
            properties = item.get("properties", {})
            tags = []
            
            # 尋找多選屬性（標籤）
            for prop_name, prop in properties.items():
                if prop.get("type") == "multi_select":
                    options = prop.get("multi_select", [])
                    for option in options:
                        tag_name = option.get("name")
                        if tag_name:
                            tags.append(tag_name)
            
            return tags
            
        except Exception as e:
            logger.error(f"提取標籤時發生錯誤", error=e)
            return []
    
    async def test_connection(self) -> bool:
        """測試 Notion API 連線"""
        try:
            logger.info("測試 Notion API 連線")
            
            loop = asyncio.get_event_loop()
            
            # 嘗試取得資料庫資訊
            await loop.run_in_executor(
                None,
                lambda: self.client.databases.retrieve(database_id=self.database_id)
            )
            
            logger.info("Notion API 連線測試成功")
            return True
            
        except Exception as e:
            logger.error(f"Notion API 連線測試失敗", error=e)
            return False