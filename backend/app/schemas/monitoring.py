"""
监控系统数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    services: Dict[str, Any] = Field(..., description="各服务状态")
    timestamp: float = Field(..., description="检查时间戳")
    response_time: int = Field(..., description="响应时间(毫秒)")

class MonitoringDataResponse(BaseModel):
    """监控数据响应"""
    id: str = Field(..., description="监控数据ID")
    tenant_id: Optional[str] = Field(None, description="租户ID")
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    response_time: Optional[int] = Field(None, description="响应时间(毫秒)")
    error_message: Optional[str] = Field(None, description="错误信息")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")
    created_at: datetime = Field(..., description="创建时间")

class SystemOverviewResponse(BaseModel):
    """系统概览响应"""
    total_tenants: int = Field(..., description="总租户数")
    total_projects: int = Field(..., description="总项目数")
    total_transactions: int = Field(..., description="总财务记录数")
    total_users: int = Field(..., description="总用户数")
    today_new_tenants: int = Field(..., description="今日新增租户数")
    active_tenants: int = Field(..., description="活跃租户数")
    system_uptime: float = Field(..., description="系统运行时间")
    last_updated: float = Field(..., description="最后更新时间")

class TenantActivityResponse(BaseModel):
    """租户活跃度响应"""
    id: str = Field(..., description="活跃度记录ID")
    tenant_id: str = Field(..., description="租户ID")
    activity_date: date = Field(..., description="活跃日期")
    login_count: int = Field(..., description="登录次数")
    project_operations: int = Field(..., description="项目操作次数")
    transaction_operations: int = Field(..., description="财务操作次数")
    supplier_operations: int = Field(..., description="供应商操作次数")
    last_activity_at: Optional[datetime] = Field(None, description="最后活跃时间")
    activity_score: int = Field(..., description="活跃度评分")

class AdminOperationLogResponse(BaseModel):
    """管理员操作日志响应"""
    id: str = Field(..., description="日志ID")
    admin_user_id: str = Field(..., description="管理员用户ID")
    operation_type: str = Field(..., description="操作类型")
    target_type: str = Field(..., description="目标类型")
    target_id: Optional[str] = Field(None, description="目标ID")
    operation_details: Optional[Dict[str, Any]] = Field(None, description="操作详情")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    created_at: datetime = Field(..., description="创建时间")

class LogOperationRequest(BaseModel):
    """记录操作日志请求"""
    operation_type: str = Field(..., description="操作类型")
    target_type: str = Field(..., description="目标类型")
    target_id: Optional[str] = Field(None, description="目标ID")
    operation_details: Optional[Dict[str, Any]] = Field(None, description="操作详情")
