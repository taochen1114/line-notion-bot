"""
日誌工具模組
"""
import logging
import sys
from typing import Optional
from google.cloud import logging as cloud_logging
from ..config import get_settings, is_production


class Logger:
    """日誌管理器"""
    
    def __init__(self, name: str = __name__):
        self.settings = get_settings()
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """設定日誌記錄器"""
        # 設定日誌等級
        if self.settings.debug:
            level = logging.DEBUG
        elif is_production():
            level = logging.INFO
        else:
            level = logging.DEBUG
        
        self.logger.setLevel(level)
        
        # 避免重複添加 handler
        if self.logger.handlers:
            return
        
        # 設定格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Google Cloud Logging (僅在生產環境)
        if is_production():
            try:
                client = cloud_logging.Client(project=self.settings.gcp_project_id)
                cloud_handler = client.get_default_handler()
                cloud_handler.setLevel(level)
                self.logger.addHandler(cloud_handler)
            except Exception as e:
                self.logger.warning(f"無法設定 Google Cloud Logging: {e}")
    
    def debug(self, message: str, **kwargs):
        """記錄 DEBUG 等級日誌"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """記錄 INFO 等級日誌"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """記錄 WARNING 等級日誌"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """記錄 ERROR 等級日誌"""
        if error:
            self.logger.error(f"{message}: {str(error)}", exc_info=True, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """記錄 CRITICAL 等級日誌"""
        if error:
            self.logger.critical(f"{message}: {str(error)}", exc_info=True, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)


# 全域日誌實例
logger = Logger("line-notion-bot")


def get_logger(name: str = None) -> Logger:
    """取得日誌記錄器實例"""
    if name:
        return Logger(name)
    return logger