"""
租户数据模型
"""
from sqlalchemy import Column, String, Date, BigInteger, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel

class Tenant(BaseModel):
    """租户模型"""
    __tablename__ = "tenants"
    
    name = Column(String(100), nullable=False, comment="企业名称")
    domain = Column(String(50), unique=True, comment="租户域名")
    plan_type = Column(String(20), default='trial', comment="订阅计划类型")
    settings = Column(JSONB, default={}, comment="租户设置")
    subscription_end = Column(Date, comment="订阅到期日期")
    storage_used = Column(BigInteger, default=0, comment="已使用存储空间(字节)")
    storage_limit = Column(BigInteger, default=5368709120, comment="存储空间限制(5GB)")
    api_calls_used = Column(Integer, default=0, comment="已使用API调用次数")
    api_calls_limit = Column(Integer, default=1000, comment="API调用次数限制")
    status = Column(String(20), default='active', comment="租户状态")
    
    # 关联关系
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="tenant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="tenant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    
    # 监控系统关联关系
    monitoring_data = relationship("MonitoringData", back_populates="tenant", cascade="all, delete-orphan")
    system_statistics = relationship("SystemStatistics", back_populates="tenant", cascade="all, delete-orphan")
    activity_records = relationship("TenantActivity", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(name='{self.name}', domain='{self.domain}')>"
