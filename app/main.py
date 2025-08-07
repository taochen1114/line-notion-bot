"""
Line Bot 串接 Notion API 主應用程式
"""
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .config import get_settings, is_production
from .services.line_service import LineService
from .services.notion_service import NotionService
from .models.line_models import ErrorResponse
from .utils.logger import get_logger

logger = get_logger(__name__)


# 全域服務實例
line_service: LineService = None
notion_service: NotionService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    global line_service, notion_service
    
    logger.info("正在啟動 Line Bot 應用程式...")
    
    try:
        # 初始化服務
        line_service = LineService()
        notion_service = NotionService()
        
        # 測試 Notion 連線
        if await notion_service.test_connection():
            logger.info("Notion API 連線測試成功")
        else:
            logger.warning("Notion API 連線測試失敗，但應用程式將繼續運行")
        
        logger.info("Line Bot 應用程式啟動完成")
        
        yield
        
    except Exception as e:
        logger.error("應用程式啟動時發生錯誤", error=e)
        raise
    finally:
        logger.info("正在關閉 Line Bot 應用程式...")


# 建立 FastAPI 應用程式
app = FastAPI(
    title="Line Bot Notion API",
    description="Line Bot 串接 Notion API 知識庫搜尋服務",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """根路徑健康檢查"""
    return {
        "status": "ok",
        "message": "Line Bot Notion API 服務正在運行",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    try:
        # 檢查 Notion 連線
        notion_status = await notion_service.test_connection()
        
        return {
            "status": "healthy",
            "services": {
                "notion": "ok" if notion_status else "error",
                "line": "ok"
            }
        }
    except Exception as e:
        logger.error("健康檢查時發生錯誤", error=e)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """Line Bot Webhook 端點"""
    try:
        # 取得請求內容
        body = await request.body()
        signature = request.headers.get("X-Line-Signature", "")
        
        # 驗證簽名
        if not line_service.verify_signature(body, signature):
            logger.warning("Webhook 簽名驗證失敗")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析請求體
        try:
            body_json = await request.json()
        except Exception as e:
            logger.error("解析 JSON 請求體失敗", error=e)
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # 解析事件
        events = line_service.parse_webhook_body(body_json)
        
        # 處理事件（背景任務）
        for event in events:
            background_tasks.add_task(process_line_event, event)
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("處理 Webhook 請求時發生錯誤", error=e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_line_event(event):
    """處理 Line 事件"""
    try:
        logger.info(f"處理 Line 事件：{event.type}")
        
        # 只處理訊息事件
        if not event.is_message_event:
            logger.info(f"忽略非訊息事件：{event.type}")
            return
        
        # 只處理文字訊息
        if not event.is_text_message:
            await _reply_unsupported_message(event)
            return
        
        # 處理文字訊息
        await process_text_message(event)
        
    except Exception as e:
        logger.error(f"處理 Line 事件時發生錯誤", error=e)
        
        # 嘗試回覆錯誤訊息
        if event.reply_token and line_service.is_valid_reply_token(event.reply_token):
            error_response = ErrorResponse(
                error_code="PROCESSING_ERROR",
                message=f"處理訊息時發生錯誤: {str(e)}",
                user_message="抱歉，處理您的訊息時發生錯誤，請稍後再試。"
            )
            await line_service.reply_error(event.reply_token, error_response)


async def process_text_message(event):
    """處理文字訊息"""
    try:
        text_content = event.text_content
        if not text_content:
            return
        
        logger.info(f"收到文字訊息：{text_content}")
        
        # 檢查是否為幫助指令
        if text_content.lower().strip() in ["help", "幫助", "說明", "?"]:
            await line_service.reply_help_message(event.reply_token)
            return
        
        # 提取搜尋查詢
        search_query = line_service.extract_search_query(text_content)
        
        if not search_query:
            await _reply_invalid_query(event)
            return
        
        # 執行搜尋
        logger.info(f"執行搜尋：{search_query}")
        search_response = await notion_service.search_database(search_query)
        
        # 回覆搜尋結果
        await line_service.reply_search_results(event.reply_token, search_response)
        
        # 記錄搜尋統計
        logger.info(f"搜尋完成 - 查詢：{search_query}，結果數：{search_response.total_count}")
        
    except Exception as e:
        logger.error(f"處理文字訊息時發生錯誤", error=e)
        raise


async def _reply_unsupported_message(event):
    """回覆不支援的訊息類型"""
    try:
        if event.reply_token and line_service.is_valid_reply_token(event.reply_token):
            message = "抱歉，我目前只支援文字訊息。請輸入您想搜尋的關鍵字。"
            await line_service.reply_message(event.reply_token, [message])
    except Exception as e:
        logger.error(f"回覆不支援訊息時發生錯誤", error=e)


async def _reply_invalid_query(event):
    """回覆無效的查詢"""
    try:
        if event.reply_token and line_service.is_valid_reply_token(event.reply_token):
            message = """請輸入您想搜尋的關鍵字。

例如：
• Python
• API 設計
• 資料庫

輸入「幫助」查看詳細使用說明。"""
            await line_service.reply_message(event.reply_token, [message])
    except Exception as e:
        logger.error(f"回覆無效查詢時發生錯誤", error=e)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全域例外處理器"""
    logger.error(f"未處理的例外：{str(exc)}", error=exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error" if is_production() else str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=not is_production(),
        log_level="info" if is_production() else "debug"
    )