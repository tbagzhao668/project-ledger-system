"""
监控系统数据模型
"""
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel, Base
import uuid

class MonitoringData(BaseModel):
    """监控数据表"""
    __tablename__ = "monitoring_data"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, comment="租户ID")
    service_name = Column(String(50), nullable=False, comment="服务名称")
    status = Column(String(20), nullable=False, comment="服务状态")
    response_time = Column(Integer, nullable=True, comment="响应时间(毫秒)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    extra_data = Column(JSON, nullable=True, comment="额外监控数据")
    
    # 关系
    tenant = relationship("Tenant", back_populates="monitoring_data")
    
    def __repr__(self):
        return f"<MonitoringData(service={self.service_name}, status={self.status})>"

class AdminOperationLog(BaseModel):
    """管理员操作日志表"""
    __tablename__ = "admin_operation_logs"
    
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="管理员用户ID")
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    target_type = Column(String(50), nullable=False, comment="目标类型")
    target_id = Column(UUID(as_uuid=True), nullable=True, comment="目标ID")
    operation_details = Column(JSON, nullable=True, comment="操作详情")
    ip_address = Column(INET, nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    
    # 关系
    admin_user = relationship("User", back_populates="admin_operations")
    
    def __repr__(self):
        return f"<AdminOperationLog(type={self.operation_type}, target={self.target_type})>"

class SystemStatistics(BaseModel):
    """系统统计表"""
    __tablename__ = "system_statistics"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, comment="租户ID")
    stat_date = Column(Date, nullable=False, comment="统计日期")
    stat_type = Column(String(50), nullable=False, comment="统计类型")
    stat_data = Column(JSON, nullable=False, comment="统计数据")
    
    # 关系
    tenant = relationship("Tenant", back_populates="system_statistics")
    
    def __repr__(self):
        return f"<SystemStatistics(date={self.stat_date}, type={self.stat_type})>"

class TenantActivity(BaseModel):
    """租户活跃度表"""
    __tablename__ = "tenant_activity"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, comment="租户ID")
    activity_date = Column(Date, nullable=False, comment="活跃日期")
    login_count = Column(Integer, default=0, comment="登录次数")
    project_operations = Column(Integer, default=0, comment="项目操作次数")
    transaction_operations = Column(Integer, default=0, comment="财务操作次数")
    supplier_operations = Column(Integer, default=0, comment="供应商操作次数")
    last_activity_at = Column(DateTime, nullable=True, comment="最后活跃时间")
    activity_score = Column(Integer, default=0, comment="活跃度评分(0-100)")
    
    # 关系
    tenant = relationship("Tenant", back_populates="activity_records")
    
    def __repr__(self):
        return f"<TenantActivity(tenant={self.tenant_id}, score={self.activity_score})>"

class HealthCheck(BaseModel):
    """健康检查记录表"""
    __tablename__ = "health_checks"
    
    service_name = Column(String(50), nullable=False, comment="服务名称")
    status = Column(String(20), nullable=False, comment="检查状态")
    response_time = Column(Integer, nullable=True, comment="响应时间(毫秒)")
    error_details = Column(Text, nullable=True, comment="错误详情")
    check_details = Column(JSON, nullable=True, comment="检查详情")
    
    def __repr__(self):
        return f"<HealthCheck(service={self.service_name}, status={self.status})>"
