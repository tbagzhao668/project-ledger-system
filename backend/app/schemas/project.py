"""
项目相关数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# 项目状态枚举
class ProjectStatusEnum(str, Enum):
    """项目状态枚举"""
    PLANNING = "planning"         # 规划中
    IN_PROGRESS = "in_progress"   # 进行中
    ON_HOLD = "on_hold"          # 暂停
    COMPLETED = "completed"       # 已完成
    CANCELLED = "cancelled"       # 已取消

# 项目类型枚举
class ProjectTypeEnum(str, Enum):
    """项目类型枚举"""
    MUNICIPAL = "municipal"               # 市政工程
    DECORATION = "decoration"             # 装饰工程
    CONSTRUCTION = "construction"         # 建筑工程
    WATER_CONSERVANCY = "water_conservancy"  # 水利水电工程
    INSTALLATION = "installation"         # 安装工程
    HIGHWAY = "highway"                   # 公路工程
    BRIDGE = "bridge"                     # 桥梁工程
    TUNNEL = "tunnel"                     # 隧道工程
    MECHANICAL_ELECTRICAL = "mechanical_electrical"  # 机电工程
    OTHER = "other"                       # 其他

# 项目优先级枚举
class ProjectPriorityEnum(str, Enum):
    """项目优先级枚举"""
    LOW = "low"                   # 低
    MEDIUM = "medium"             # 中
    HIGH = "high"                 # 高
    URGENT = "urgent"             # 紧急



# 项目创建请求
class ProjectCreate(BaseModel):
    """项目创建请求"""
    name: str = Field(..., min_length=2, max_length=100, description="项目名称")
    project_code: str = Field(..., min_length=2, max_length=50, description="项目代码")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")
    project_type: ProjectTypeEnum = Field(..., description="项目类型")
    priority: ProjectPriorityEnum = Field(ProjectPriorityEnum.MEDIUM, description="项目优先级")
    status: ProjectStatusEnum = Field(ProjectStatusEnum.PLANNING, description="项目状态")
    
    # 时间相关
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="计划结束日期")
    
    # 预算相关
    budget: Optional[Decimal] = Field(None, ge=0, description="项目预算")
    contract_amount: Optional[Decimal] = Field(None, ge=0, description="合同金额")
    
    # 位置信息
    address: Optional[str] = Field("", max_length=500, description="项目地址")
    
    # 人员管理
    manager_name: str = Field(..., max_length=100, description="项目经理姓名")
    
    # 联系人信息
    client_name: Optional[str] = Field("", max_length=100, description="客户名称")
    client_contact: Optional[str] = Field("", max_length=100, description="客户联系人")
    client_phone: Optional[str] = Field("", max_length=20, description="客户电话")
    
    # 其他信息
    tags: Optional[List[str]] = Field([], description="项目标签")

# 项目更新请求
class ProjectUpdate(BaseModel):
    """项目更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")
    project_type: Optional[ProjectTypeEnum] = Field(None, description="项目类型")
    priority: Optional[ProjectPriorityEnum] = Field(None, description="项目优先级")
    status: Optional[ProjectStatusEnum] = Field(None, description="项目状态")
    
    # 时间相关
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="计划结束日期")
    planned_end_date: Optional[date] = Field(None, description="计划结束日期")
    actual_end_date: Optional[date] = Field(None, description="实际结束日期")
    
    # 预算相关
    budget: Optional[Decimal] = Field(None, ge=0, description="项目预算")
    contract_amount: Optional[Decimal] = Field(None, ge=0, description="合同金额")
    actual_cost: Optional[Decimal] = Field(None, ge=0, description="实际成本")
    actual_expenses: Optional[Decimal] = Field(None, ge=0, description="实际支出")
    
    # 位置信息
    location: Optional[str] = Field(None, max_length=200, description="项目地点")
    address: Optional[str] = Field(None, max_length=500, description="项目地址")
    
    # 人员管理
    manager_name: Optional[str] = Field(None, max_length=100, description="项目经理姓名")
    
    # 联系人信息
    client_name: Optional[str] = Field(None, max_length=100, description="客户名称")
    client_contact: Optional[str] = Field(None, max_length=100, description="客户联系人")
    client_phone: Optional[str] = Field(None, max_length=20, description="客户电话")
    
    # 其他信息
    tags: Optional[List[str]] = Field(None, description="项目标签")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")
    
    # 变更原因相关
    budget_change_reason: Optional[str] = Field(None, max_length=200, description="预算变更原因")
    contract_change_reason: Optional[str] = Field(None, max_length=200, description="合同变更原因")
    change_description: Optional[str] = Field(None, max_length=500, description="变更详细说明")

# 项目响应数据
class ProjectResponse(BaseModel):
    """项目响应数据"""
    id: str = Field(..., description="项目ID")
    project_code: str = Field(..., description="项目代码")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    project_type: Optional[str] = Field(None, description="项目类型")
    priority: Optional[str] = Field(None, description="项目优先级")
    status: str = Field(..., description="项目状态")
    
    # 时间相关
    start_date: Optional[str] = Field(None, description="开始日期")
    planned_end_date: Optional[str] = Field(None, description="计划结束日期")
    actual_end_date: Optional[str] = Field(None, description="实际结束日期")
    
    # 预算相关
    budget: Optional[float] = Field(None, description="项目预算")
    contract_amount: Optional[float] = Field(None, description="合同金额")
    actual_expenses: Optional[float] = Field(None, description="实际支出")
    currency: Optional[str] = Field("CNY", description="货币单位")
    
    # 位置信息
    location: Optional[str] = Field(None, description="项目地点")
    
    # 联系人信息
    client_name: Optional[str] = Field(None, description="客户名称")
    client_contact: Optional[str] = Field(None, description="客户联系人")
    client_phone: Optional[str] = Field(None, description="客户电话")
    
    # 其他信息
    tags: Optional[List[str]] = Field(None, description="项目标签")
    notes: Optional[str] = Field(None, description="备注")
    
    # 关联信息
    manager_id: Optional[str] = Field(None, description="项目经理ID")
    manager_name: Optional[str] = Field(None, description="项目经理姓名")
    created_by: str = Field(..., description="创建人ID")
    created_by_name: str = Field(..., description="创建人姓名")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True

# 项目列表响应
class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
    projects: List[ProjectResponse] = Field(..., description="项目列表")

# 项目统计
class ProjectStatistics(BaseModel):
    """项目统计数据"""
    total_projects: int = Field(..., description="项目总数")
    active_projects: int = Field(..., description="进行中项目数")
    completed_projects: int = Field(..., description="已完成项目数")
    total_budget: Decimal = Field(..., description="总预算")
    total_actual_cost: Decimal = Field(..., description="总实际成本")
    budget_utilization: float = Field(..., description="预算使用率")
    projects_by_status: Dict[str, int] = Field(..., description="按状态分组的项目数")
    projects_by_type: Dict[str, int] = Field(..., description="按类型分组的项目数")
    recent_projects: List[ProjectResponse] = Field(..., description="最近的项目列表")



# 项目变更记录相关
class ChangeTypeEnum(str, Enum):
    """变更类型枚举"""
    CREATE = "create"              # 创建
    UPDATE = "update"              # 更新
    DELETE = "delete"              # 删除
    STATUS_CHANGE = "status_change"  # 状态变更
    BUDGET_CHANGE = "budget_change"  # 预算变更
    CONTRACT_CHANGE = "contract_change"  # 合同变更

class ChangeLogCreate(BaseModel):
    """变更记录创建请求"""
    change_type: ChangeTypeEnum = Field(..., description="变更类型")
    field_name: Optional[str] = Field(None, description="变更字段名")
    old_value: Optional[str] = Field(None, description="原值")
    new_value: Optional[str] = Field(None, description="新值")
    change_description: Optional[str] = Field(None, description="变更描述")
    change_reason: Optional[str] = Field(None, description="变更原因")

class ChangeLogResponse(BaseModel):
    """变更记录响应数据"""
    id: str = Field(..., description="变更记录ID")
    tenant_id: str = Field(..., description="租户ID")
    project_id: str = Field(..., description="项目ID")
    change_type: str = Field(..., description="变更类型")
    field_name: Optional[str] = Field(None, description="变更字段名")
    old_value: Optional[str] = Field(None, description="原值")
    new_value: Optional[str] = Field(None, description="新值")
    change_description: Optional[str] = Field(None, description="变更描述")
    change_reason: Optional[str] = Field(None, description="变更原因")
    changed_by: Optional[str] = Field(None, description="变更人ID")
    changed_by_name: Optional[str] = Field(None, description="变更人姓名")
    created_at: str = Field(..., description="变更时间")
    
    class Config:
        from_attributes = True

# 项目查询参数
class ProjectQueryParams(BaseModel):
    """项目查询参数"""
    page: Optional[int] = Field(1, ge=1, description="页码")
    per_page: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    status: Optional[ProjectStatusEnum] = Field(None, description="项目状态")
    project_type: Optional[ProjectTypeEnum] = Field(None, description="项目类型")
    priority: Optional[ProjectPriorityEnum] = Field(None, description="项目优先级")
    manager_id: Optional[str] = Field(None, description="项目经理ID")
    start_date_from: Optional[date] = Field(None, description="开始日期范围起始")
    start_date_to: Optional[date] = Field(None, description="开始日期范围结束")
    budget_min: Optional[Decimal] = Field(None, ge=0, description="预算最小值")
    budget_max: Optional[Decimal] = Field(None, ge=0, description="预算最大值")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")
