"""
供应商相关数据模式
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

class CreditRatingEnum(str, Enum):
    """信用等级枚举"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"           # 良好
    FAIR = "fair"           # 一般
    POOR = "poor"           # 较差
    UNKNOWN = "unknown"     # 未知

# 供应商创建请求
class SupplierCreate(BaseModel):
    """供应商创建请求"""
    name: str = Field(..., min_length=1, max_length=200, description="供应商名称")
    code: Optional[str] = Field(None, max_length=50, description="供应商编码")
    contact_person: Optional[str] = Field(None, max_length=100, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, max_length=500, description="地址")
    business_scope: Optional[str] = Field(None, max_length=1000, description="经营范围")
    qualification: Optional[str] = Field(None, max_length=1000, description="资质证书")
    credit_rating: Optional[CreditRatingEnum] = Field(None, description="信用等级")
    payment_terms: Optional[str] = Field(None, max_length=200, description="付款条件")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")
    is_active: bool = Field(True, description="是否激活")

# 供应商更新请求
class SupplierUpdate(BaseModel):
    """供应商更新请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="供应商名称")
    code: Optional[str] = Field(None, max_length=50, description="供应商编码")
    contact_person: Optional[str] = Field(None, max_length=100, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, max_length=500, description="地址")
    business_scope: Optional[str] = Field(None, max_length=1000, description="经营范围")
    qualification: Optional[str] = Field(None, max_length=1000, description="资质证书")
    credit_rating: Optional[CreditRatingEnum] = Field(None, description="信用等级")
    payment_terms: Optional[str] = Field(None, max_length=200, description="付款条件")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")
    is_active: Optional[bool] = Field(None, description="是否激活")

# 供应商响应模型
class SupplierResponse(BaseModel):
    """供应商响应模型"""
    id: str = Field(..., description="供应商ID")
    tenant_id: str = Field(..., description="租户ID")
    name: str = Field(..., description="供应商名称")
    code: Optional[str] = Field(None, description="供应商编码")
    contact_person: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    business_scope: Optional[str] = Field(None, description="经营范围")
    qualification: Optional[str] = Field(None, description="资质证书")
    credit_rating: Optional[str] = Field(None, description="信用等级")
    payment_terms: Optional[str] = Field(None, description="付款条件")
    notes: Optional[str] = Field(None, description="备注")
    total_amount: str = Field(..., description="累计交易金额")
    transaction_count: int = Field(..., description="交易次数")
    is_active: bool = Field(..., description="是否激活")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

# 供应商统计模型
class SupplierStatistics(BaseModel):
    """供应商统计模型"""
    total_suppliers: int = Field(..., description="供应商总数")
    active_suppliers: int = Field(..., description="活跃供应商数")
    inactive_suppliers: int = Field(..., description="停用供应商数")
    total_transaction_amount: str = Field(..., description="总交易金额")
    total_transaction_count: int = Field(..., description="总交易次数")
    average_transaction_amount: str = Field(..., description="平均交易金额")
    credit_rating_distribution: Dict[str, int] = Field(..., description="信用等级分布")
    top_suppliers: List[Dict[str, Any]] = Field(..., description="top供应商列表")
    monthly_trend: List[Dict[str, Any]] = Field(..., description="月度趋势")

# 供应商搜索请求
class SupplierSearchRequest(BaseModel):
    """供应商搜索请求"""
    keyword: Optional[str] = Field(None, description="关键词搜索")
    credit_rating: Optional[CreditRatingEnum] = Field(None, description="信用等级筛选")
    is_active: Optional[bool] = Field(None, description="激活状态筛选")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小交易金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大交易金额")
    min_transactions: Optional[int] = Field(None, ge=0, description="最小交易次数")
    max_transactions: Optional[int] = Field(None, ge=0, description="最大交易次数")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="排序方向")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")

# 供应商交易历史
class SupplierTransactionHistory(BaseModel):
    """供应商交易历史"""
    supplier_id: str = Field(..., description="供应商ID")
    supplier_name: str = Field(..., description="供应商名称")
    transactions: List[Dict[str, Any]] = Field(..., description="交易记录列表")
    total_amount: str = Field(..., description="总交易金额")
    transaction_count: int = Field(..., description="交易次数")
    first_transaction_date: Optional[str] = Field(None, description="首次交易日期")
    last_transaction_date: Optional[str] = Field(None, description="最近交易日期")
    average_amount: str = Field(..., description="平均交易金额")

# 批量操作请求
class SupplierBatchRequest(BaseModel):
    """供应商批量操作请求"""
    supplier_ids: List[str] = Field(..., min_items=1, description="供应商ID列表")
    action: str = Field(..., pattern="^(activate|deactivate|delete)$", description="操作类型")

# 供应商评价模型
class SupplierRating(BaseModel):
    """供应商评价模型"""
    supplier_id: str = Field(..., description="供应商ID")
    quality_rating: int = Field(..., ge=1, le=5, description="质量评级(1-5)")
    delivery_rating: int = Field(..., ge=1, le=5, description="交付评级(1-5)")
    service_rating: int = Field(..., ge=1, le=5, description="服务评级(1-5)")
    price_rating: int = Field(..., ge=1, le=5, description="价格评级(1-5)")
    overall_rating: float = Field(..., ge=1.0, le=5.0, description="综合评级")
    comment: Optional[str] = Field(None, max_length=500, description="评价备注")
    project_id: Optional[str] = Field(None, description="项目ID")

# 供应商导入模型
class SupplierImport(BaseModel):
    """供应商导入模型"""
    suppliers: List[SupplierCreate] = Field(..., min_items=1, description="供应商列表")
    skip_duplicates: bool = Field(True, description="是否跳过重复项")
    update_existing: bool = Field(False, description="是否更新已存在的供应商")

# 供应商导出请求
class SupplierExportRequest(BaseModel):
    """供应商导出请求"""
    supplier_ids: Optional[List[str]] = Field(None, description="指定供应商ID列表，为空则导出全部")
    include_transactions: bool = Field(False, description="是否包含交易记录")
    include_statistics: bool = Field(True, description="是否包含统计信息")
    format: str = Field("excel", pattern="^(excel|csv|pdf)$", description="导出格式")
