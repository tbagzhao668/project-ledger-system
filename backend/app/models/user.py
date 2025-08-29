"""
用户数据模型
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, comment="租户ID")
    username = Column(String(50), nullable=False, comment="用户名")
    email = Column(String(100), nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(String(20), nullable=False, comment="用户角色")
    permissions = Column(JSONB, default=[], comment="用户权限")
    profile = Column(JSONB, default={}, comment="用户资料")
    last_login = Column(DateTime, comment="最后登录时间")
    login_count = Column(Integer, default=0, comment="登录次数")
    is_active = Column(Boolean, default=True, comment="是否激活")
    email_verified = Column(Boolean, default=False, comment="邮箱是否验证")
    two_factor_enabled = Column(Boolean, default=False, comment="是否启用两步验证")
    
    # 唯一约束：租户内邮箱唯一
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_tenant_user_email'),
    )
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="users")
    created_projects = relationship("Project", foreign_keys="Project.created_by", back_populates="created_by_user")
    updated_projects = relationship("Project", foreign_keys="Project.updated_by", back_populates="updated_by_user")
    managed_projects = relationship("Project", foreign_keys="Project.manager_id", back_populates="manager")
    created_transactions = relationship("Transaction", foreign_keys="Transaction.created_by", back_populates="created_by_user")
    project_changes = relationship("ProjectChangeLog", foreign_keys="ProjectChangeLog.changed_by", back_populates="changed_by_user")
    
    # 监控系统关联关系
    admin_operations = relationship("AdminOperationLog", back_populates="admin_user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
