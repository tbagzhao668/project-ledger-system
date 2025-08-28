from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SystemSettings(BaseModel):
    """系统设置模型"""
    system_name: str = Field(..., description="系统名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="系统描述", max_length=500)

class SecuritySettings(BaseModel):
    """安全设置模型"""
    session_timeout: int = Field(..., description="会话超时时间（分钟）", ge=15, le=1440)

class SettingsResponse(BaseModel):
    """设置响应模型"""
    success: bool
    message: str
    data: Dict[str, Any]
