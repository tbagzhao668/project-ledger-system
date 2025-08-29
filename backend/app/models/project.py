"""
项目数据模型 - 完整版本
"""
from sqlalchemy import Column, String, Text, Date, Integer, DECIMAL, UUID, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel



class ProjectChangeLog(BaseModel):
    """项目变更记录模型"""
    __tablename__ = "project_change_logs"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, comment="租户ID")
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, comment="项目ID")
    change_type = Column(String(50), nullable=False, comment="变更类型")
    field_name = Column(String(100), comment="变更字段名")
    old_value = Column(Text, comment="原值")
    new_value = Column(Text, comment="新值")
    change_description = Column(Text, comment="变更描述")
    change_reason = Column(Text, comment="变更原因")
    changed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), comment="变更人")
    
    # 关联关系
    project = relationship("Project", back_populates="change_logs")
    changed_by_user = relationship("User", back_populates="project_changes")
    
    def __repr__(self):
        return f"<ProjectChangeLog(type='{self.change_type}', field='{self.field_name}')>"



class Project(BaseModel):
    """项目模型 - 完整字段版本"""
    __tablename__ = "projects"
    
    # ==================== 基础信息 ====================
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, comment="租户ID")
    name = Column(String(200), nullable=False, comment="项目名称")
    project_code = Column(String(50), unique=True, comment="项目编号")
    description = Column(Text, comment="项目描述")
    
    # ==================== 项目分类 ====================
    project_type = Column(String(50), default='other', comment="项目类型")
    category = Column(String(100), comment="项目分类")
    tags = Column(JSONB, default=[], comment="项目标签")
    
    # ==================== 项目状态 ====================
    status = Column(String(20), default='planning', comment="项目状态")
    priority = Column(String(20), default='medium', comment="项目优先级")
    progress = Column(Integer, default=0, comment="项目进度(0-100)")
    health_status = Column(String(20), default='healthy', comment="项目健康状态")
    
    # ==================== 时间管理 ====================
    start_date = Column(Date, comment="计划开始日期")
    end_date = Column(Date, comment="计划结束日期")
    actual_start_date = Column(Date, comment="实际开始日期")
    actual_end_date = Column(Date, comment="实际结束日期")
    estimated_duration = Column(Integer, comment="预计工期(天)")
    actual_duration = Column(Integer, comment="实际工期(天)")
    
    # ==================== 财务信息 ====================
    budget = Column(DECIMAL(15, 2), comment="项目预算")
    actual_cost = Column(DECIMAL(15, 2), default=0, comment="实际成本")
    estimated_cost = Column(DECIMAL(15, 2), comment="预估成本")
    cost_variance = Column(DECIMAL(15, 2), comment="成本偏差")
    budget_utilization = Column(DECIMAL(5, 2), comment="预算使用率(%)")
    
    # ==================== 人员管理 ====================
    manager_name = Column(String(100), comment="项目经理姓名")
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), comment="项目经理ID")
    team_size = Column(Integer, default=1, comment="团队规模")
    assigned_users = Column(JSONB, default=[], comment="分配的用户ID列表")
    
    # ==================== 位置和联系信息 ====================
    location = Column(JSONB, default={}, comment="项目位置信息")
    address = Column(String(500), comment="项目地址")
    coordinates = Column(JSONB, comment="地理坐标")
    
    # ==================== 客户和合同信息 ====================
    client_info = Column(JSONB, default={}, comment="客户信息")
    contract_info = Column(JSONB, default={}, comment="合同信息")
    contract_number = Column(String(100), comment="合同编号")
    contract_value = Column(DECIMAL(15, 2), comment="合同金额")
    payment_terms = Column(JSONB, comment="付款条件")
    
    # ==================== 技术规格 ====================
    technical_specs = Column(JSONB, comment="技术规格")
    requirements = Column(JSONB, comment="项目需求")
    deliverables = Column(JSONB, comment="交付物")
    quality_standards = Column(JSONB, comment="质量标准")
    
    # ==================== 风险管理 ====================
    risk_level = Column(String(20), default='low', comment="风险等级")
    risk_factors = Column(JSONB, comment="风险因素")
    mitigation_plans = Column(JSONB, comment="风险缓解计划")
    
    # ==================== 变更原因相关 ====================
    budget_change_reason = Column(String(200), comment="预算变更原因")
    contract_change_reason = Column(String(200), comment="合同变更原因")
    change_description = Column(Text, comment="变更详细说明")
    
    # ==================== 文档和附件 ====================
    documents = Column(JSONB, default=[], comment="相关文档")
    attachments = Column(JSONB, default=[], comment="附件信息")
    
    # ==================== 审批和流程 ====================
    approval_status = Column(String(20), default='pending', comment="审批状态")
    approval_history = Column(JSONB, comment="审批历史")
    workflow_stage = Column(String(50), comment="工作流阶段")
    
    # ==================== 监控和报告 ====================
    last_review_date = Column(Date, comment="最后评审日期")
    next_review_date = Column(Date, comment="下次评审日期")
    review_cycle = Column(String(20), comment="评审周期")
    reporting_frequency = Column(String(20), comment="报告频率")
    
    # ==================== 系统字段 ====================
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), comment="创建人")
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), comment="最后更新人")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_template = Column(Boolean, default=False, comment="是否为模板项目")
    
    # ==================== 关联关系 ====================
    tenant = relationship("Tenant", back_populates="projects")
    created_by_user = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    updated_by_user = relationship("User", back_populates="updated_projects", foreign_keys=[updated_by])
    manager = relationship("User", back_populates="managed_projects", foreign_keys=[manager_id])
    transactions = relationship("Transaction", back_populates="project", cascade="all, delete-orphan")

    change_logs = relationship("ProjectChangeLog", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(name='{self.name}', code='{self.project_code}', status='{self.status}')>"
