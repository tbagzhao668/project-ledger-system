"""
财务记录管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, extract, case
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid

from ...core.auth import get_current_user, require_permissions
from ...core.database import get_db
from ...models.user import User
from ...models.project import Project
from ...models.transaction import Transaction, Category, Supplier
from ...schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionApproval, TransactionResponse,
    TransactionListResponse, TransactionStatistics, MonthlyFinancialReport,
    TransactionQueryParams, TransactionTypeEnum, TransactionStatusEnum,
    ApprovalStatusEnum, PaymentMethodEnum
)

router = APIRouter(prefix="/transactions", tags=["财务记录"])

@router.post("/", response_model=TransactionResponse, summary="创建财务记录")
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(require_permissions(["transaction_create"])),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的财务记录
    
    需要权限: transaction_create
    """
    try:
        # 验证项目是否存在且属于当前租户
        project_result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == transaction_data.project_id,
                    Project.tenant_id == current_user.tenant_id
                )
            )
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在或无权限访问"
            )
        
        # 验证供应商是否存在
        if transaction_data.supplier_id:
            supplier_result = await db.execute(
                select(Supplier).where(
                    and_(
                        Supplier.id == transaction_data.supplier_id,
                        Supplier.tenant_id == current_user.tenant_id
                    )
                )
            )
            supplier = supplier_result.scalar_one_or_none()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="供应商不存在"
                )
        
        # 验证分类是否存在（如果提供了分类ID）
        category = None
        category_id = transaction_data.category_id if transaction_data.category_id and transaction_data.category_id.strip() else None
        
        if category_id:
            category_result = await db.execute(
                select(Category).where(
                    and_(
                        Category.id == category_id,
                        Category.tenant_id == current_user.tenant_id,
                        Category.is_active == '1'
                    )
                )
            )
            category = category_result.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="分类不存在"
                )
        
        # 处理可选的supplier_id
        supplier_id = None
        if transaction_data.supplier_id and transaction_data.supplier_id.strip():
            supplier_id = transaction_data.supplier_id
        
        # 创建财务记录
        new_transaction = Transaction(
            tenant_id=current_user.tenant_id,
            project_id=transaction_data.project_id,
            supplier_id=supplier_id,
            category_id=category_id,
            type=transaction_data.type.value if hasattr(transaction_data.type, 'value') else transaction_data.type,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            exchange_rate=transaction_data.exchange_rate,
            description=transaction_data.description,
            notes=transaction_data.notes,
            tags=transaction_data.tags or [],
            payment_method=transaction_data.payment_method.value if hasattr(transaction_data.payment_method, 'value') else transaction_data.payment_method,
            transaction_date=transaction_data.transaction_date,
            status='confirmed',
            created_by=current_user.id
        )
        
        db.add(new_transaction)
        await db.flush()
        await db.refresh(new_transaction)
        
        # 更新项目实际成本（如果是支出）
        if transaction_data.type == TransactionTypeEnum.EXPENSE:
            # 确保类型一致，都转换为Decimal
            from decimal import Decimal
            current_cost = Decimal(str(project.actual_cost or 0))
            transaction_amount = Decimal(str(transaction_data.amount))
            project.actual_cost = current_cost + transaction_amount
        
        await db.commit()
        
        # 获取关联数据并构建响应
        transaction_dict = await _build_transaction_response(new_transaction, project, category, current_user, None)
        
        return TransactionResponse(**transaction_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建财务记录失败: {str(e)}"
        )

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    project_id: Optional[str] = Query(None, description="项目ID筛选"),
    category_id: Optional[str] = Query(None, description="分类ID筛选"),
    supplier_id: Optional[str] = Query(None, description="供应商ID筛选"),
    type: Optional[TransactionTypeEnum] = Query(None, description="交易类型筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取交易记录列表"""
    try:
        # 构建查询
        query = select(Transaction).where(Transaction.tenant_id == current_user.tenant_id)
        
        # 添加筛选条件
        if project_id:
            query = query.where(Transaction.project_id == project_id)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if supplier_id:
            query = query.where(Transaction.supplier_id == supplier_id)
        if type:
            query = query.where(Transaction.type == type)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        if search:
            search_filter = or_(
                Transaction.description.ilike(f"%{search}%"),
                Transaction.notes.ilike(f"%{search}%"),
                Transaction.reference_number.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # 排序和分页
        query = query.order_by(desc(Transaction.transaction_date)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        # 转换为响应格式
        response_transactions = []
        for transaction in transactions:
            # 获取关联数据
            project_name = None
            supplier_name = None
            category_name = None
            
            if transaction.project_id:
                project_result = await db.execute(
                    select(Project.name).where(Project.id == transaction.project_id)
                )
                project_name = project_result.scalar_one_or_none()
            
            if transaction.supplier_id:
                supplier_result = await db.execute(
                    select(Supplier.name).where(Supplier.id == transaction.supplier_id)
                )
                supplier_name = supplier_result.scalar_one_or_none()
            
            if transaction.category_id:
                category_result = await db.execute(
                    select(Category.name).where(Category.id == transaction.category_id)
                )
                category_name = category_result.scalar_one_or_none()
            
            transaction_dict = {
                "id": str(transaction.id),
                "tenant_id": str(transaction.tenant_id),
                "project_id": str(transaction.project_id) if transaction.project_id else None,
                "project_name": project_name,
                "supplier_id": str(transaction.supplier_id) if transaction.supplier_id else None,
                "supplier_name": supplier_name,
                "category_id": str(transaction.category_id) if transaction.category_id else None,
                "category_name": category_name,
                "transaction_date": transaction.transaction_date,
                "type": transaction.type,
                "amount": str(transaction.amount) if transaction.amount else "0.00",
                "currency": transaction.currency,
                "exchange_rate": float(transaction.exchange_rate) if transaction.exchange_rate else 1.0,
                "description": transaction.description,
                "notes": transaction.notes,
                "tags": transaction.tags or [],
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "attachment_url": transaction.attachment_url,
                "reference_number": transaction.reference_number,
                "approved_by": transaction.approved_by,
                "approved_at": transaction.approved_at.isoformat() if transaction.approved_at else None,
                "created_at": transaction.created_at.isoformat(),
                "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
            }
            response_transactions.append(transaction_dict)
        
        return response_transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取交易记录失败: {str(e)}"
        )

@router.get("/{transaction_id}", response_model=TransactionResponse, summary="获取财务记录详情")
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(require_permissions(["transaction_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取财务记录详情
    
    需要权限: transaction_read
    """
    try:
        transaction_result = await db.execute(
            select(Transaction)
            .options(
                joinedload(Transaction.project),
                joinedload(Transaction.category),
                joinedload(Transaction.created_by_user),
                joinedload(Transaction.approved_by_user)
            )
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.tenant_id == current_user.tenant_id
                )
            )
        )
        transaction = transaction_result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="财务记录不存在"
            )
        
        # 构建响应
        transaction_dict = await _build_transaction_response(
            transaction,
            transaction.project,
            transaction.category,
            transaction.created_by_user,
            transaction.approved_by_user
        )
        
        return TransactionResponse(**transaction_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取财务记录详情失败: {str(e)}"
        )

@router.put("/{transaction_id}", response_model=TransactionResponse, summary="更新财务记录")
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(require_permissions(["transaction_update"])),
    db: AsyncSession = Depends(get_db)
):
    """
    更新财务记录信息
    
    需要权限: transaction_update
    """
    try:
        transaction_result = await db.execute(
            select(Transaction)
            .options(joinedload(Transaction.project))
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.tenant_id == current_user.tenant_id
                )
            )
        )
        transaction = transaction_result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="财务记录不存在"
            )
        
        # 检查是否可以编辑（已审批的记录不能编辑金额等关键字段）
        if transaction.approval_status == 'approved':
            restricted_fields = ['amount', 'currency', 'exchange_rate', 'transaction_date']
            update_data = transaction_data.dict(exclude_unset=True)
            if any(field in update_data for field in restricted_fields):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="已审批的记录不能修改金额、货币、汇率和交易日期"
                )
        
        # 验证分类（如果有更新）
        category = None
        if transaction_data.category_id:
            category_result = await db.execute(
                select(Category).where(
                    and_(
                        Category.id == transaction_data.category_id,
                        Category.tenant_id == current_user.tenant_id,
                        Category.is_active == '1'
                    )
                )
            )
            category = category_result.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="分类不存在"
                )
        
        # 保存原始金额（用于更新项目成本）
        original_amount = transaction.amount
        
        # 更新字段
        update_data = transaction_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(transaction, field):
                if field in ['status'] and value and hasattr(value, 'value'):
                    setattr(transaction, field, value.value)
                else:
                    setattr(transaction, field, value)
        
        transaction.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # 更新项目实际成本（如果是支出且金额有变化）
        if transaction.type == 'expense':
            project = transaction.project
            if project and original_amount and transaction.amount:
                # 确保类型一致，都转换为Decimal
                from decimal import Decimal
                current_cost = Decimal(str(project.actual_cost or 0))
                new_amount = Decimal(str(transaction.amount))
                original_amount_decimal = Decimal(str(original_amount))
                cost_difference = new_amount - original_amount_decimal
                project.actual_cost = current_cost + cost_difference
        
        await db.refresh(transaction)
        await db.commit()
        
        # 重新加载关联数据
        transaction_result = await db.execute(
            select(Transaction)
            .options(
                joinedload(Transaction.project),
                joinedload(Transaction.category),
                joinedload(Transaction.created_by_user),
                joinedload(Transaction.approved_by_user)
            )
            .where(Transaction.id == transaction_id)
        )
        transaction = transaction_result.scalar_one()
        
        # 构建响应
        transaction_dict = await _build_transaction_response(
            transaction,
            transaction.project,
            transaction.category,
            transaction.created_by_user,
            transaction.approved_by_user
        )
        
        return TransactionResponse(**transaction_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新财务记录失败: {str(e)}"
        )

@router.post("/{transaction_id}/approve", summary="审批财务记录")
async def approve_transaction(
    transaction_id: str,
    approval_data: TransactionApproval,
    current_user: User = Depends(require_permissions(["transaction_approve"])),
    db: AsyncSession = Depends(get_db)
):
    """
    审批财务记录
    
    需要权限: transaction_approve
    """
    try:
        transaction_result = await db.execute(
            select(Transaction).where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.tenant_id == current_user.tenant_id
                )
            )
        )
        transaction = transaction_result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="财务记录不存在"
            )
        
        if transaction.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能审批待审批状态的记录"
            )
        
        # 更新审批信息
        transaction.status = approval_data.approval_status.value if hasattr(approval_data.approval_status, 'value') else approval_data.approval_status
        transaction.approved_by = current_user.id
        transaction.approved_at = datetime.utcnow()
        
        # 如果有审批备注，添加到描述中
        if approval_data.approval_note:
            transaction.description += f"\n[审批备注: {approval_data.approval_note}]"
        
        await db.commit()
        
        approval_status_text = approval_data.approval_status.value if hasattr(approval_data.approval_status, 'value') else approval_data.approval_status
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": f"财务记录已{approval_status_text}",
                "approval_status": approval_status_text,
                "approved_by": str(current_user.id),
                "approved_at": transaction.approved_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审批财务记录失败: {str(e)}"
        )

@router.delete("/{transaction_id}", summary="删除财务记录")
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(require_permissions(["transaction_delete"])),
    db: AsyncSession = Depends(get_db)
):
    """
    删除财务记录
    
    需要权限: transaction_delete
    """
    try:
        transaction_result = await db.execute(
            select(Transaction)
            .options(joinedload(Transaction.project))
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.tenant_id == current_user.tenant_id
                )
            )
        )
        transaction = transaction_result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="财务记录不存在"
            )
        
        # 检查是否可以删除（已审批的记录需要特殊权限）
        if transaction.status == 'confirmed':
            # 这里可以添加额外的权限检查
            pass
        
        # 更新项目实际成本（如果是支出）
        if transaction.type == 'expense':
            project = transaction.project
            if project and transaction.amount:
                # 确保类型一致，都转换为Decimal
                from decimal import Decimal
                current_cost = Decimal(str(project.actual_cost or 0))
                transaction_amount = Decimal(str(transaction.amount))
                project.actual_cost = current_cost - transaction_amount
        
        await db.delete(transaction)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "财务记录已删除"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除财务记录失败: {str(e)}"
        )

@router.get("/statistics/overview", response_model=TransactionStatistics, summary="获取财务统计")
async def get_transaction_statistics(
    project_id: Optional[str] = Query(None, description="项目ID筛选"),
    date_from: Optional[date] = Query(None, description="统计日期范围-起始"),
    date_to: Optional[date] = Query(None, description="统计日期范围-结束"),
    current_user: User = Depends(require_permissions(["transaction_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取财务统计数据
    
    需要权限: transaction_read
    """
    try:
        # 构建查询条件
        query_conditions = [Transaction.tenant_id == current_user.tenant_id]
        
        if project_id:
            query_conditions.append(Transaction.project_id == project_id)
        if date_from:
            query_conditions.append(Transaction.transaction_date >= date_from)
        if date_to:
            query_conditions.append(Transaction.transaction_date <= date_to)
        
        # 基础统计查询
        stats_query = await db.execute(
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('total_income'),
                func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('total_expense'),
                func.count(case((Transaction.type == 'income', 1))).label('income_count'),
                func.count(case((Transaction.type == 'expense', 1))).label('expense_count'),
                func.count(case((Transaction.status == 'pending', 1))).label('pending_count'),
                func.sum(case((Transaction.status == 'pending', Transaction.amount), else_=0)).label('pending_amount'),
                func.avg(Transaction.amount).label('avg_amount')
            ).where(and_(*query_conditions))
        )
        stats = stats_query.first()
        
        # 按状态分组统计
        status_query = await db.execute(
            select(
                Transaction.status,
                func.count(Transaction.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(Transaction.status)
        )
        transactions_by_status = {row.status: row.count for row in status_query.all()}
        
        # 按支付方式分组统计
        payment_method_query = await db.execute(
            select(
                Transaction.payment_method,
                func.count(Transaction.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(Transaction.payment_method)
        )
        transactions_by_payment_method = {
            row.payment_method or 'unknown': row.count 
            for row in payment_method_query.all()
        }
        
        # 月度趋势（最近6个月）
        monthly_trend_query = await db.execute(
            select(
                extract('year', Transaction.transaction_date).label('year'),
                extract('month', Transaction.transaction_date).label('month'),
                func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
                func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense'),
                func.count(Transaction.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(
                extract('year', Transaction.transaction_date),
                extract('month', Transaction.transaction_date)
            )
            .order_by(
                extract('year', Transaction.transaction_date).desc(),
                extract('month', Transaction.transaction_date).desc()
            )
            .limit(6)
        )
        
        monthly_trend = []
        for row in monthly_trend_query.all():
            monthly_trend.append({
                'year': int(row.year),
                'month': int(row.month),
                'income': float(row.income or 0),
                'expense': float(row.expense or 0),
                'net': float((row.income or 0) - (row.expense or 0)),
                'count': row.count
            })
        
        # 热门分类（Top 5）
        top_categories_query = await db.execute(
            select(
                Category.name,
                func.count(Transaction.id).label('count'),
                func.sum(Transaction.amount).label('total_amount')
            ).select_from(
                Transaction.__table__.join(
                    Category.__table__,
                    Transaction.category_id == Category.id
                )
            ).where(and_(*query_conditions))
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(5)
        )
        
        top_categories = []
        for row in top_categories_query.all():
            top_categories.append({
                'name': row.name,
                'count': row.count,
                'total_amount': float(row.total_amount)
            })
        
        # 最近的交易记录（5条）
        recent_transactions_result = await db.execute(
            select(Transaction)
            .options(
                joinedload(Transaction.project),
                joinedload(Transaction.category),
                joinedload(Transaction.created_by_user)
            )
            .where(and_(*query_conditions))
            .order_by(desc(Transaction.created_at))
            .limit(5)
        )
        recent_transactions_data = recent_transactions_result.scalars().all()
        
        recent_transactions = []
        for transaction in recent_transactions_data:
            transaction_dict = await _build_transaction_response(
                transaction,
                transaction.project,
                transaction.category,
                transaction.created_by_user,
                None
            )
            recent_transactions.append(TransactionResponse(**transaction_dict))
        
        # 计算统计数据
        total_income = float(stats.total_income or 0)
        total_expense = float(stats.total_expense or 0)
        net_amount = total_income - total_expense
        
        return TransactionStatistics(
            total_transactions=stats.total_transactions or 0,
            total_income=total_income,
            total_expense=total_expense,
            net_amount=net_amount,
            income_transactions=stats.income_count or 0,
            expense_transactions=stats.expense_count or 0,
            pending_approval_count=stats.pending_count or 0,
            pending_approval_amount=float(stats.pending_amount or 0),
            avg_transaction_amount=float(stats.avg_amount or 0),
            transactions_by_status=transactions_by_status,
            transactions_by_payment_method=transactions_by_payment_method,
            monthly_trend=monthly_trend,
            top_categories=top_categories,
            recent_transactions=recent_transactions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取财务统计失败: {str(e)}"
        )

@router.get("/statistics/charts", summary="获取图表统计数据")
async def get_chart_statistics(
    period: str = Query("month", description="统计周期: month/quarter/year"),
    date_from: Optional[str] = Query(None, description="统计日期范围-起始 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="统计日期范围-结束 (YYYY-MM-DD)"),
    current_user: User = Depends(require_permissions(["transaction_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取图表统计数据
    
    需要权限: transaction_read
    """
    try:
        print(f"开始处理图表统计请求: period={period}, date_from={date_from}, date_to={date_to}")
        
        # 构建查询条件
        query_conditions = [Transaction.tenant_id == current_user.tenant_id]
        
        # 处理日期参数
        parsed_date_from = None
        parsed_date_to = None
        
        if date_from:
            try:
                parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
                query_conditions.append(Transaction.transaction_date >= parsed_date_from)
                print(f"添加起始日期条件: {parsed_date_from}")
            except ValueError as e:
                print(f"日期格式错误 date_from: {date_from}, 错误: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"起始日期格式错误，请使用 YYYY-MM-DD 格式: {date_from}"
                )
        
        if date_to:
            try:
                parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
                query_conditions.append(Transaction.transaction_date <= parsed_date_to)
                print(f"添加结束日期条件: {parsed_date_to}")
            except ValueError as e:
                print(f"日期格式错误 date_to: {date_to}, 错误: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"结束日期格式错误，请使用 YYYY-MM-DD 格式: {date_to}"
                )
        
        print(f"查询条件数量: {len(query_conditions)}")
        
        # 1. 收支对比数据
        print("开始查询收支对比数据...")
        income_expense_query = await db.execute(
            select(
                func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('total_income'),
                func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('total_expense')
            ).where(and_(*query_conditions))
        )
        income_expense_data = income_expense_query.first()
        print(f"收支对比查询结果: income={income_expense_data.total_income}, expense={income_expense_data.total_expense}")
        
        # 2. 支出分类分布
        print("开始查询支出分类分布...")
        category_distribution_query = await db.execute(
            select(
                Category.name,
                func.sum(Transaction.amount).label('total_amount')
            ).select_from(
                Transaction.__table__.join(
                    Category.__table__,
                    Transaction.category_id == Category.id
                )
            ).where(
                and_(
                    *query_conditions,
                    Transaction.type == 'expense'
                )
            ).group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
        )
        
        category_distribution = []
        for row in category_distribution_query.all():
            category_distribution.append({
                'name': row.name,
                'value': float(row.total_amount or 0)
            })
        print(f"分类分布查询结果: {len(category_distribution)} 个分类")
        
        # 3. 月度趋势数据
        print(f"开始查询{period}趋势数据...")
        if period == "month":
            # 最近12个月
            trend_query = await db.execute(
                select(
                    extract('year', Transaction.transaction_date).label('year'),
                    extract('month', Transaction.transaction_date).label('month'),
                    func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
                    func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
                ).where(and_(*query_conditions))
                .group_by(
                    extract('year', Transaction.transaction_date),
                    extract('month', Transaction.transaction_date)
                )
                .order_by(
                    extract('year', Transaction.transaction_date).desc(),
                    extract('month', Transaction.transaction_date).desc()
                )
                .limit(12)
            )
        elif period == "quarter":
            # 最近4个季度
            trend_query = await db.execute(
                select(
                    extract('year', Transaction.transaction_date).label('year'),
                    extract('quarter', Transaction.transaction_date).label('quarter'),
                    func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
                    func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
                ).where(and_(*query_conditions))
                .group_by(
                    extract('year', Transaction.transaction_date),
                    extract('quarter', Transaction.transaction_date)
                )
                .order_by(
                    extract('year', Transaction.transaction_date).desc(),
                    extract('quarter', Transaction.transaction_date).desc()
                )
                .limit(4)
            )
        else:  # year
            # 最近5年
            trend_query = await db.execute(
                select(
                    extract('year', Transaction.transaction_date).label('year'),
                    func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
                    func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
                ).where(and_(*query_conditions))
                .group_by(extract('year', Transaction.transaction_date))
                .order_by(extract('year', Transaction.transaction_date).desc())
                .limit(5)
            )
        
        monthly_trend = []
        trend_rows = trend_query.all()
        print(f"趋势查询结果: {len(trend_rows)} 条记录")
        
        for row in trend_rows:
            if period == "month":
                month_names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
                label = f"{int(row.year)}年{month_names[int(row.month)-1]}"
            elif period == "quarter":
                label = f"{int(row.year)}年Q{int(row.quarter)}"
            else:
                label = f"{int(row.year)}年"
            
            monthly_trend.append({
                'label': label,
                'income': float(row.income or 0),
                'expense': float(row.expense or 0),
                'net': float((row.income or 0) - (row.expense or 0))
            })
        
        # 4. 供应商交易排行
        print("开始查询供应商交易排行...")
        supplier_ranking_query = await db.execute(
            select(
                Supplier.name,
                func.sum(Transaction.amount).label('total_amount'),
                func.count(Transaction.id).label('transaction_count')
            ).select_from(
                Transaction.__table__.join(
                    Supplier.__table__,
                    Transaction.supplier_id == Supplier.id
                )
            ).where(and_(*query_conditions))
            .group_by(Supplier.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(10)
        )
        
        supplier_ranking = []
        for row in supplier_ranking_query.all():
            supplier_ranking.append({
                'name': row.name,
                'value': float(row.total_amount or 0),
                'count': row.transaction_count
            })
        print(f"供应商排行查询结果: {len(supplier_ranking)} 个供应商")
        
        # 5. 项目财务分析
        print("开始查询项目财务分析...")
        project_analysis_query = await db.execute(
            select(
                Project.name,
                Project.budget,
                Project.contract_value,
                func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('actual_expense')
            ).select_from(
                Project.__table__.outerjoin(
                    Transaction.__table__,
                    Project.id == Transaction.project_id
                )
            ).where(
                and_(
                    Project.tenant_id == current_user.tenant_id,
                    *query_conditions
                )
            ).group_by(Project.id, Project.name, Project.budget, Project.contract_value)
            .order_by(func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).desc())
            .limit(10)
        )
        
        project_analysis = []
        for row in project_analysis_query.all():
            budget = float(row.budget or 0)
            actual_expense = float(row.actual_expense or 0)
            profit = budget - actual_expense
            
            project_analysis.append({
                'name': row.name,
                'budget': budget,
                'actual_expense': actual_expense,
                'profit': profit
            })
        print(f"项目分析查询结果: {len(project_analysis)} 个项目")
        
        # 6. 支付方式分析
        print("开始查询支付方式分析...")
        payment_method_query = await db.execute(
            select(
                Transaction.payment_method,
                func.sum(Transaction.amount).label('total_amount'),
                func.count(Transaction.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(Transaction.payment_method)
            .order_by(func.sum(Transaction.amount).desc())
        )
        
        payment_method_analysis = []
        for row in payment_method_query.all():
            payment_method_analysis.append({
                'name': row.payment_method or '其他',
                'value': float(row.total_amount or 0),
                'count': row.count
            })
        print(f"支付方式分析查询结果: {len(payment_method_analysis)} 种方式")
        
        # 构建响应数据
        response_data = {
            "income_expense": {
                "income": float(income_expense_data.total_income or 0),
                "expense": float(income_expense_data.total_expense or 0),
                "net": float((income_expense_data.total_income or 0) - (income_expense_data.total_expense or 0))
            },
            "category_distribution": category_distribution,
            "monthly_trend": monthly_trend,
            "supplier_ranking": supplier_ranking,
            "project_analysis": project_analysis,
            "payment_method_analysis": payment_method_analysis
        }
        
        print("图表统计数据处理完成，准备返回响应")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"图表统计处理异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表统计失败: {str(e)}"
        )

@router.get("/statistics/table", summary="获取表格统计数据")
async def get_table_statistics(
    date_from: Optional[date] = Query(None, description="统计日期范围-起始"),
    date_to: Optional[date] = Query(None, description="统计日期范围-结束"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    current_user: User = Depends(require_permissions(["transaction_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取表格统计数据
    
    需要权限: transaction_read
    """
    try:
        # 构建查询条件
        query_conditions = [Transaction.tenant_id == current_user.tenant_id]
        
        if date_from:
            query_conditions.append(Transaction.transaction_date >= date_from)
        if date_to:
            query_conditions.append(Transaction.transaction_date <= date_to)
        
        # 获取总数
        total_query = await db.execute(
            select(func.count(Transaction.id)).where(and_(*query_conditions))
        )
        total = total_query.scalar()
        
        # 获取分页数据
        transactions_query = await db.execute(
            select(Transaction)
            .options(
                joinedload(Transaction.project),
                joinedload(Transaction.category),
                joinedload(Transaction.supplier)
            )
            .where(and_(*query_conditions))
            .order_by(desc(Transaction.transaction_date))
            .offset(skip)
            .limit(limit)
        )
        
        transactions_data = transactions_query.scalars().all()
        
        # 构建响应数据
        table_data = []
        for transaction in transactions_data:
            table_data.append({
                "id": str(transaction.id),
                "transaction_date": transaction.transaction_date.isoformat(),
                "type": transaction.type,
                "description": transaction.description,
                "category_name": transaction.category.name if transaction.category else None,
                "project_name": transaction.project.name if transaction.project else None,
                "supplier_name": transaction.supplier.name if transaction.supplier else None,
                "amount": float(transaction.amount),
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat()
            })
        
        return {
            "total": total,
            "data": table_data,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表格统计失败: {str(e)}"
        )

async def _build_transaction_response(
    transaction: Transaction,
    project: Project = None,
    category: Category = None,
    created_by_user: User = None,
    approved_by_user: User = None
) -> dict:
    """构建财务记录响应数据"""
    return {
        "id": str(transaction.id),
        "tenant_id": str(transaction.tenant_id),
        "project_id": str(transaction.project_id) if transaction.project_id else None,
        "project_name": project.name if project else None,
        "supplier_id": str(transaction.supplier_id) if transaction.supplier_id else None,
        "supplier_name": None,  # 需要从查询中获取
        "type": transaction.type,
        "category_id": str(transaction.category_id) if transaction.category_id else None,
        "category_name": category.name if category else None,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "exchange_rate": transaction.exchange_rate,
        "description": transaction.description,
        "notes": transaction.notes,
        "tags": transaction.tags or [],
        "payment_method": transaction.payment_method,
        "attachment_url": transaction.attachment_url,
        "reference_number": transaction.reference_number,
        "transaction_date": transaction.transaction_date,
        "status": transaction.status,
        "approved_by": str(transaction.approved_by) if transaction.approved_by else None,
        "approved_by_name": approved_by_user.username if approved_by_user else None,
        "approved_at": transaction.approved_at,
        "created_by": str(transaction.created_by),
        "created_by_name": created_by_user.username if created_by_user else None,
        "created_at": transaction.created_at.isoformat(),
        "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
    }
