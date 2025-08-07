"""
應用程式配置管理模組
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """應用程式設定"""
    
    # Line Bot 設定
    line_channel_access_token: str = Field(..., env="LINE_CHANNEL_ACCESS_TOKEN")
    line_channel_secret: str = Field(..., env="LINE_CHANNEL_SECRET")
    
    # Notion API 設定
    notion_api_token: str = Field(..., env="NOTION_API_TOKEN")
    notion_database_id: str = Field(..., env="NOTION_DATABASE_ID")
    
    # GCP 設定
    gcp_project_id: str = Field(..., env="GCP_PROJECT_ID")
    google_application_credentials: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # 應用程式設定
    port: int = Field(8080, env="PORT")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # API 設定
    max_search_results: int = Field(5, env="MAX_SEARCH_RESULTS")
    response_timeout: int = Field(30, env="RESPONSE_TIMEOUT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全域設定實例
settings = Settings()


def get_settings() -> Settings:
    """取得應用程式設定"""
    return settings


def is_production() -> bool:
    """檢查是否為生產環境"""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """檢查是否為開發環境"""
    return settings.environment.lower() == "development"