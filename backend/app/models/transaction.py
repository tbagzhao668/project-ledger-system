"""
交易记录数据模型
"""
from sqlalchemy import Column, String, Text, Date, DECIMAL, UUID, ForeignKey, UniqueConstraint, Enum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
import uuid

class Category(BaseModel):
    """交易分类模型"""
    __tablename__ = "categories"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, comment="租户ID")
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), comment="父分类ID")
    icon = Column(String(50), comment="图标")
    color = Column(String(7), comment="颜色")
    is_system = Column(String(1), default='0', comment="是否系统预设分类")
    is_active = Column(String(1), default='1', comment="是否激活")
    sort_order = Column(String(10), default='0', comment="排序")
    
    # 唯一约束：租户内分类名称唯一
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_tenant_category_name'),
    )
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    children = relationship("Category")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Transaction(BaseModel):
    """交易记录模型"""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="交易ID")
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, comment="租户ID")
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), comment="关联项目ID")
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id'), comment="关联供应商ID")
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), comment="分类ID")
    transaction_date = Column(Date, nullable=False, comment="交易日期")
    type = Column(String(10), nullable=False, comment="交易类型: income/expense")
    amount = Column(DECIMAL(15, 2), nullable=False, comment="交易金额")
    currency = Column(String(10), default='CNY', comment="货币类型")
    exchange_rate = Column(DECIMAL(10, 6), default=1.000000, comment="汇率")
    description = Column(Text, comment="交易描述")
    notes = Column(Text, comment="备注")
    tags = Column(JSONB, comment="标签")
    payment_method = Column(String(50), comment="支付方式")
    status = Column(String(20), default='pending', comment="交易状态")
    attachment_url = Column(String(500), comment="附件链接")
    reference_number = Column(String(100), comment="参考编号")
    approved_by = Column(String(100), comment="审批人")
    approved_at = Column(DateTime, comment="审批时间")
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), comment="创建人")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    tenant = relationship("Tenant", back_populates="transactions")
    project = relationship("Project", back_populates="transactions")
    supplier = relationship("Supplier", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="created_transactions")
    
    def __repr__(self):
        return f"<Transaction(type='{self.type}', amount={self.amount}, date='{self.transaction_date}')>"

class Supplier(BaseModel):
    """供应商模型"""
    __tablename__ = "suppliers"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, comment="租户ID")
    name = Column(String(200), nullable=False, comment="供应商名称")
    code = Column(String(50), comment="供应商编码")
    contact_person = Column(String(100), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    address = Column(Text, comment="地址")
    business_scope = Column(Text, comment="经营范围")
    qualification = Column(Text, comment="资质证书")
    credit_rating = Column(String(10), comment="信用等级")
    payment_terms = Column(String(200), comment="付款条件")
    is_active = Column(String(1), default='1', comment="是否激活")
    notes = Column(Text, comment="备注")
    
    # 关系
    tenant = relationship("Tenant", back_populates="suppliers")
    transactions = relationship("Transaction", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"
