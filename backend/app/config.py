"""
工程项目流水账管理系统 - 配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "工程项目流水账管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "fince_project_prod"
    DB_USER: str = "fince_app_project"
    DB_PASSWORD: str = "Fince_project_5%8*6^9(3#0)"
    
    @property
    def DATABASE_URL(self) -> str:
        """构建异步数据库URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """构建同步数据库URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT安全配置
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时，方便开发调试
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30天，方便开发调试
    
    # 加密配置
    ENCRYPTION_KEY: Optional[str] = None
    ENCRYPTION_SALT: str = "project-ledger-salt"
    
    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # 邮件配置
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # 第三方API配置
    BAIDU_OCR_API_KEY: Optional[str] = None
    BAIDU_OCR_SECRET_KEY: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 租户配置
    DEFAULT_STORAGE_LIMIT: int = 5 * 1024 * 1024 * 1024  # 5GB
    DEFAULT_API_CALLS_LIMIT: int = 10000
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 创建全局配置实例
settings = Settings()

# 开发环境特殊配置
if os.getenv("ENVIRONMENT") == "development":
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    
    @property
    def DATABASE_URL(self) -> str:
        """构建异步数据库URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """构建同步数据库URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
