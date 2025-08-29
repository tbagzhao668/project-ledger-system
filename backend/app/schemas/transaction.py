"""
财务记录相关数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class TransactionTypeEnum(str, Enum):
    """交易类型枚举"""
    INCOME = "income"      # 收入
    EXPENSE = "expense"    # 支出

class TransactionStatusEnum(str, Enum):
    """交易状态枚举"""
    DRAFT = "draft"           # 草稿
    CONFIRMED = "confirmed"   # 已确认
    CANCELLED = "cancelled"   # 已取消

class ApprovalStatusEnum(str, Enum):
    """审批状态枚举"""
    PENDING = "pending"       # 待审批
    APPROVED = "approved"     # 已审批
    REJECTED = "rejected"     # 已拒绝
    CANCELLED = "cancelled"   # 已取消

class PaymentMethodEnum(str, Enum):
    """支付方式枚举"""
    CASH = "cash"               # 现金
    BANK_TRANSFER = "bank_transfer"  # 银行转账
    CREDIT_CARD = "credit_card"      # 信用卡
    DEBIT_CARD = "debit_card"        # 借记卡
    CHECK = "check"                  # 支票
    ALIPAY = "alipay"               # 支付宝
    WECHAT_PAY = "wechat_pay"       # 微信支付
    OTHER = "other"                 # 其他

# 财务记录创建请求
class TransactionCreate(BaseModel):
    """交易记录创建请求"""
    project_id: Optional[str] = Field(None, description="关联项目ID")
    supplier_id: Optional[str] = Field(None, description="关联供应商ID")
    category_id: Optional[str] = Field(None, description="分类ID")
    transaction_date: date = Field(..., description="交易日期")
    type: TransactionTypeEnum = Field(..., description="交易类型")
    amount: Decimal = Field(..., gt=0, description="交易金额")
    currency: str = Field("CNY", max_length=10, description="货币类型")
    exchange_rate: Decimal = Field(1.000000, ge=0, description="汇率")
    description: str = Field(..., min_length=1, max_length=500, description="交易描述")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")
    tags: Optional[List[str]] = Field(None, description="标签")
    payment_method: Optional[str] = Field(None, max_length=50, description="支付方式")
    status: TransactionStatusEnum = Field(TransactionStatusEnum.DRAFT, description="交易状态")
    attachment_url: Optional[str] = Field(None, max_length=500, description="附件链接")
    reference_number: Optional[str] = Field(None, max_length=100, description="参考编号")


# 财务记录更新请求
class TransactionUpdate(BaseModel):
    """财务记录更新请求"""
    category_id: Optional[str] = Field(None, description="分类ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="金额")
    currency: Optional[str] = Field(None, description="货币类型")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="汇率")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="描述")
    tags: Optional[List[str]] = Field(None, description="标签")
    supplier_info: Optional[Dict[str, Any]] = Field(None, description="供应商信息")
    payment_method: Optional[PaymentMethodEnum] = Field(None, description="支付方式")
    receipt_urls: Optional[List[str]] = Field(None, description="票据图片URLs")
    invoice_info: Optional[Dict[str, Any]] = Field(None, description="发票信息")
    location: Optional[Dict[str, Any]] = Field(None, description="位置信息")
    transaction_date: Optional[date] = Field(None, description="交易日期")
    status: Optional[TransactionStatusEnum] = Field(None, description="状态")

# 财务记录审批请求
class TransactionApproval(BaseModel):
    """财务记录审批请求"""
    approval_status: ApprovalStatusEnum = Field(..., description="审批状态")
    approval_note: Optional[str] = Field(None, max_length=500, description="审批备注")

# 财务记录响应
class TransactionResponse(BaseModel):
    """交易记录响应"""
    id: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    transaction_date: date
    type: TransactionTypeEnum
    amount: Decimal
    currency: str
    exchange_rate: Decimal
    description: str
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    payment_method: Optional[str] = None
    status: TransactionStatusEnum
    attachment_url: Optional[str] = None
    reference_number: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 财务记录列表响应
class TransactionListResponse(BaseModel):
    """财务记录列表响应"""
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
    transactions: List[TransactionResponse] = Field(..., description="财务记录列表")
    total_income: Decimal = Field(..., description="总收入")
    total_expense: Decimal = Field(..., description="总支出")
    net_amount: Decimal = Field(..., description="净额")

# 财务统计
class TransactionStatistics(BaseModel):
    """财务统计数据"""
    total_transactions: int = Field(..., description="交易总数")
    total_income: Decimal = Field(..., description="总收入")
    total_expense: Decimal = Field(..., description="总支出")
    net_amount: Decimal = Field(..., description="净额")
    income_transactions: int = Field(..., description="收入交易数")
    expense_transactions: int = Field(..., description="支出交易数")
    pending_approval_count: int = Field(..., description="待审批数量")
    pending_approval_amount: Decimal = Field(..., description="待审批金额")
    avg_transaction_amount: Decimal = Field(..., description="平均交易金额")
    transactions_by_status: Dict[str, int] = Field(..., description="按状态分组的交易数")
    transactions_by_payment_method: Dict[str, int] = Field(..., description="按支付方式分组的交易数")
    monthly_trend: List[Dict[str, Any]] = Field(..., description="月度趋势数据")
    top_categories: List[Dict[str, Any]] = Field(..., description="热门分类")
    recent_transactions: List[TransactionResponse] = Field(..., description="最近的交易记录")

# 月度财务报表
class MonthlyFinancialReport(BaseModel):
    """月度财务报表"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    total_income: Decimal = Field(..., description="总收入")
    total_expense: Decimal = Field(..., description="总支出")
    net_amount: Decimal = Field(..., description="净额")
    transaction_count: int = Field(..., description="交易笔数")
    income_by_category: Dict[str, Decimal] = Field(..., description="按分类的收入")
    expense_by_category: Dict[str, Decimal] = Field(..., description="按分类的支出")
    expense_by_project: Dict[str, Decimal] = Field(..., description="按项目的支出")

# 财务记录查询参数
class TransactionQueryParams(BaseModel):
    """财务记录查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词（描述、标签）")
    project_id: Optional[str] = Field(None, description="项目ID筛选")
    type: Optional[TransactionTypeEnum] = Field(None, description="交易类型筛选")
    category_id: Optional[str] = Field(None, description="分类筛选")
    status: Optional[TransactionStatusEnum] = Field(None, description="状态筛选")
    approval_status: Optional[ApprovalStatusEnum] = Field(None, description="审批状态筛选")
    payment_method: Optional[PaymentMethodEnum] = Field(None, description="支付方式筛选")
    date_from: Optional[date] = Field(None, description="交易日期范围-起始")
    date_to: Optional[date] = Field(None, description="交易日期范围-结束")
    amount_from: Optional[Decimal] = Field(None, description="金额范围-最小")
    amount_to: Optional[Decimal] = Field(None, description="金额范围-最大")
    created_by: Optional[str] = Field(None, description="创建人筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field("transaction_date", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向: asc/desc")

# 分类相关模式
class CategoryCreate(BaseModel):
    """分类创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    parent_id: Optional[str] = Field(None, description="父分类ID")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    color: Optional[str] = Field(None, max_length=7, description="颜色")
    sort_order: int = Field(0, description="排序")

class CategoryUpdate(BaseModel):
    """分类更新请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    parent_id: Optional[str] = Field(None, description="父分类ID")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    color: Optional[str] = Field(None, max_length=7, description="颜色")
    sort_order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否激活")

class CategoryResponse(BaseModel):
    """分类响应数据"""
    id: str = Field(..., description="分类ID")
    tenant_id: str = Field(..., description="租户ID")
    name: str = Field(..., description="分类名称")
    parent_id: Optional[str] = Field(None, description="父分类ID")
    parent_name: Optional[str] = Field(None, description="父分类名称")
    icon: Optional[str] = Field(None, description="图标")
    color: Optional[str] = Field(None, description="颜色")
    is_system: bool = Field(..., description="是否系统预设分类")
    is_active: bool = Field(..., description="是否激活")
    sort_order: int = Field(..., description="排序")
    transaction_count: int = Field(0, description="关联交易数量")
    total_amount: Decimal = Field(0, description="累计金额")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

# 批量导入
class TransactionImport(BaseModel):
    """财务记录批量导入"""
    transactions: List[TransactionCreate] = Field(..., description="交易记录列表")
    skip_validation: bool = Field(False, description="是否跳过验证")
    auto_approve: bool = Field(False, description="是否自动审批")

class ImportResult(BaseModel):
    """导入结果"""
    success_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="失败数量")
    total_count: int = Field(..., description="总数量")
    failed_records: List[Dict[str, Any]] = Field(..., description="失败记录详情")
    success_ids: List[str] = Field(..., description="成功导入的ID列表")
