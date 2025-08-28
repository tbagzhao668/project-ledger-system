"""
供应商管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, extract, case, text
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid

from ...core.auth import get_current_user, require_permissions
from ...core.database import get_db
from ...models.user import User
from ...models.transaction import Supplier, Transaction
from ...schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplierStatistics, SupplierSearchRequest, SupplierTransactionHistory,
    SupplierBatchRequest, SupplierRating, SupplierImport, SupplierExportRequest,
    CreditRatingEnum
)

router = APIRouter(prefix="/suppliers", tags=["供应商管理"])

@router.post("/", response_model=SupplierResponse, summary="创建供应商")
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_permissions(["supplier_create"])),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新供应商
    
    需要权限: supplier_create
    """
    try:
        # 检查供应商名称是否已存在
        existing_supplier_query = select(Supplier).where(
            and_(
                Supplier.tenant_id == current_user.tenant_id,
                Supplier.name == supplier_data.name
            )
        )
        existing_supplier_result = await db.execute(existing_supplier_query)
        existing_supplier = existing_supplier_result.scalar_one_or_none()
        
        if existing_supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="供应商名称已存在"
            )
        
        # 创建供应商
        new_supplier = Supplier(
            tenant_id=current_user.tenant_id,
            name=supplier_data.name,
            code=supplier_data.code,
            contact_person=supplier_data.contact_person,
            phone=supplier_data.phone,
            email=supplier_data.email,
            address=supplier_data.address,
            business_scope=supplier_data.business_scope,
            qualification=supplier_data.qualification,
            credit_rating=supplier_data.credit_rating.value if supplier_data.credit_rating else None,
            payment_terms=supplier_data.payment_terms,
            notes=supplier_data.notes,
            is_active='1' if supplier_data.is_active else '0'
        )
        
        db.add(new_supplier)
        await db.flush()
        await db.refresh(new_supplier)
        
        # 构建响应
        supplier_dict = {
            "id": str(new_supplier.id),
            "tenant_id": str(new_supplier.tenant_id),
            "name": new_supplier.name,
            "code": new_supplier.code,
            "contact_person": new_supplier.contact_person,
            "phone": new_supplier.phone,
            "email": new_supplier.email,
            "address": new_supplier.address,
            "business_scope": new_supplier.business_scope,
            "qualification": new_supplier.qualification,
            "credit_rating": new_supplier.credit_rating,
            "payment_terms": new_supplier.payment_terms,
            "notes": new_supplier.notes,
            "total_amount": "0.00",
            "transaction_count": 0,
            "is_active": new_supplier.is_active == '1',
            "created_at": new_supplier.created_at.isoformat(),
            "updated_at": new_supplier.updated_at.isoformat() if new_supplier.updated_at else None
        }
        
        await db.commit()
        return supplier_dict
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建供应商失败: {str(e)}"
        )

@router.get("/", response_model=List[SupplierResponse], summary="获取供应商列表")
async def get_suppliers(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    credit_rating: Optional[CreditRatingEnum] = Query(None, description="信用等级筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(require_permissions(["supplier_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商列表
    
    支持关键词搜索、筛选和排序
    需要权限: supplier_read
    """
    try:
        # 构建查询条件
        query_conditions = [Supplier.tenant_id == current_user.tenant_id]
        
        # 关键词搜索
        if keyword:
            keyword_condition = or_(
                Supplier.name.ilike(f"%{keyword}%"),
                Supplier.contact_person.ilike(f"%{keyword}%"),
                Supplier.phone.ilike(f"%{keyword}%"),
                Supplier.email.ilike(f"%{keyword}%")
            )
            query_conditions.append(keyword_condition)
        
        # 信用等级筛选
        if credit_rating:
            query_conditions.append(Supplier.credit_rating == credit_rating.value)
        
        # 激活状态筛选
        if is_active is not None:
            query_conditions.append(Supplier.is_active == ('1' if is_active else '0'))
        
        # 构建基础查询
        base_query = select(Supplier).where(and_(*query_conditions))
        
        # 排序
        if sort_by == "name":
            order_column = Supplier.name
        elif sort_by == "total_amount":
            order_column = Supplier.total_amount
        elif sort_by == "transaction_count":
            order_column = func.cast(Supplier.transaction_count, func.INTEGER())
        elif sort_by == "credit_rating":
            order_column = Supplier.credit_rating
        else:
            order_column = Supplier.created_at
        
        if sort_order == "desc":
            base_query = base_query.order_by(desc(order_column))
        else:
            base_query = base_query.order_by(asc(order_column))
        
        # 分页
        offset = (page - 1) * size
        suppliers_query = base_query.offset(offset).limit(size)
        
        suppliers_result = await db.execute(suppliers_query)
        suppliers = suppliers_result.scalars().all()
        
        # 构建响应
        suppliers_list = []
        for supplier in suppliers:
            # 动态计算交易统计信息
            transaction_stats_query = select(
                func.count(Transaction.id).label('transaction_count'),
                func.sum(Transaction.amount).label('total_amount')
            ).where(
                and_(
                    Transaction.supplier_id == supplier.id,
                    Transaction.tenant_id == current_user.tenant_id
                )
            )
            
            stats_result = await db.execute(transaction_stats_query)
            stats = stats_result.first()
            
            transaction_count = int(stats.transaction_count or 0)
            total_amount = float(stats.total_amount or 0)
            
            supplier_dict = {
                "id": str(supplier.id),
                "tenant_id": str(supplier.tenant_id),
                "name": supplier.name,
                "code": supplier.code,
                "contact_person": supplier.contact_person,
                "phone": supplier.phone,
                "email": supplier.email,
                "address": supplier.address,
                "business_scope": supplier.business_scope,
                "qualification": supplier.qualification,
                "credit_rating": supplier.credit_rating,
                "payment_terms": supplier.payment_terms,
                "notes": supplier.notes,
                "total_amount": f"{total_amount:.2f}",
                "transaction_count": transaction_count,
                "is_active": supplier.is_active == '1',
                "created_at": supplier.created_at.isoformat(),
                "updated_at": supplier.updated_at.isoformat() if supplier.updated_at else None
            }
            suppliers_list.append(supplier_dict)
        
        return suppliers_list
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取供应商列表失败: {str(e)}"
        )

@router.get("/{supplier_id}", response_model=SupplierResponse, summary="获取供应商详情")
async def get_supplier(
    supplier_id: str,
    current_user: User = Depends(require_permissions(["supplier_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定供应商的详细信息
    
    需要权限: supplier_read
    """
    try:
        supplier_query = select(Supplier).where(
            and_(
                Supplier.id == supplier_id,
                Supplier.tenant_id == current_user.tenant_id
            )
        )
        
        supplier_result = await db.execute(supplier_query)
        supplier = supplier_result.scalar_one_or_none()
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # 动态计算交易统计信息
        transaction_stats_query = select(
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).where(
            and_(
                Transaction.supplier_id == supplier.id,
                Transaction.tenant_id == current_user.tenant_id
            )
        )
        
        stats_result = await db.execute(transaction_stats_query)
        stats = stats_result.first()
        
        transaction_count = int(stats.transaction_count or 0)
        total_amount = float(stats.total_amount or 0)
        
        # 构建响应
        supplier_dict = {
            "id": str(supplier.id),
            "tenant_id": str(supplier.tenant_id),
            "name": supplier.name,
            "code": supplier.code,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "email": supplier.email,
            "address": supplier.address,
            "business_scope": supplier.business_scope,
            "qualification": supplier.qualification,
            "credit_rating": supplier.credit_rating,
            "payment_terms": supplier.payment_terms,
            "notes": supplier.notes,
            "total_amount": f"{total_amount:.2f}",
            "transaction_count": transaction_count,
            "is_active": supplier.is_active == '1',
            "created_at": supplier.created_at.isoformat(),
            "updated_at": supplier.updated_at.isoformat() if supplier.updated_at else None
        }
        
        return supplier_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取供应商详情失败: {str(e)}"
        )

@router.put("/{supplier_id}", response_model=SupplierResponse, summary="更新供应商")
async def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    current_user: User = Depends(require_permissions(["supplier_update"])),
    db: AsyncSession = Depends(get_db)
):
    """
    更新供应商信息
    
    需要权限: supplier_update
    """
    try:
        # 获取供应商
        supplier_query = select(Supplier).where(
            and_(
                Supplier.id == supplier_id,
                Supplier.tenant_id == current_user.tenant_id
            )
        )
        
        supplier_result = await db.execute(supplier_query)
        supplier = supplier_result.scalar_one_or_none()
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # 检查名称是否冲突
        if supplier_data.name and supplier_data.name != supplier.name:
            existing_supplier_query = select(Supplier).where(
                and_(
                    Supplier.tenant_id == current_user.tenant_id,
                    Supplier.name == supplier_data.name,
                    Supplier.id != supplier_id
                )
            )
            existing_supplier_result = await db.execute(existing_supplier_query)
            existing_supplier = existing_supplier_result.scalar_one_or_none()
            
            if existing_supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="供应商名称已存在"
                )
        
        # 更新字段
        update_data = supplier_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "credit_rating" and value:
                setattr(supplier, field, value.value if hasattr(value, 'value') else value)
            elif field == "is_active":
                setattr(supplier, field, '1' if value else '0')
            else:
                setattr(supplier, field, value)
        
        await db.flush()
        await db.refresh(supplier)
        
        # 动态计算交易统计信息
        transaction_stats_query = select(
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).where(
            and_(
                Transaction.supplier_id == supplier.id,
                Transaction.tenant_id == current_user.tenant_id
            )
        )
        
        stats_result = await db.execute(transaction_stats_query)
        stats = stats_result.first()
        
        transaction_count = int(stats.transaction_count or 0)
        total_amount = float(stats.total_amount or 0)
        
        # 构建响应
        supplier_dict = {
            "id": str(supplier.id),
            "tenant_id": str(supplier.tenant_id),
            "name": supplier.name,
            "code": supplier.code,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "email": supplier.email,
            "address": supplier.address,
            "business_scope": supplier.business_scope,
            "qualification": supplier.qualification,
            "credit_rating": supplier.credit_rating,
            "payment_terms": supplier.payment_terms,
            "notes": supplier.notes,
            "total_amount": f"{total_amount:.2f}",
            "transaction_count": transaction_count,
            "is_active": supplier.is_active == '1',
            "created_at": supplier.created_at.isoformat(),
            "updated_at": supplier.updated_at.isoformat() if supplier.updated_at else None
        }
        
        await db.commit()
        return supplier_dict
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新供应商失败: {str(e)}"
        )

@router.delete("/{supplier_id}", summary="删除供应商")
async def delete_supplier(
    supplier_id: str,
    current_user: User = Depends(require_permissions(["supplier_delete"])),
    db: AsyncSession = Depends(get_db)
):
    """
    删除供应商
    
    需要权限: supplier_delete
    """
    try:
        # 获取供应商
        supplier_query = select(Supplier).where(
            and_(
                Supplier.id == supplier_id,
                Supplier.tenant_id == current_user.tenant_id
            )
        )
        
        supplier_result = await db.execute(supplier_query)
        supplier = supplier_result.scalar_one_or_none()
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # 检查是否有关联的交易记录
        transaction_count_query = select(func.count(Transaction.id)).where(
            and_(
                Transaction.supplier_id == supplier_id,
                Transaction.tenant_id == current_user.tenant_id
            )
        )
        
        transaction_count_result = await db.execute(transaction_count_query)
        transaction_count = transaction_count_result.scalar() or 0
        
        if transaction_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除供应商，存在 {transaction_count} 条关联的交易记录"
            )
        
        # 删除供应商
        await db.delete(supplier)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "供应商删除成功"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除供应商失败: {str(e)}"
        )

@router.get("/statistics/overview", response_model=SupplierStatistics, summary="获取供应商统计")
async def get_supplier_statistics(
    current_user: User = Depends(require_permissions(["supplier_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商统计信息
    
    需要权限: supplier_read
    """
    try:
        # 基础统计查询
        base_query = select(
            func.count(Supplier.id).label('total_suppliers'),
            func.count(case((Supplier.is_active == '1', 1))).label('active_suppliers'),
            func.count(case((Supplier.is_active == '0', 1))).label('inactive_suppliers'),
            func.coalesce(func.sum(Supplier.total_amount), 0).label('total_transaction_amount'),
            func.coalesce(func.sum(func.cast(Supplier.transaction_count, func.INTEGER())), 0).label('total_transaction_count')
        ).where(Supplier.tenant_id == current_user.tenant_id)
        
        base_result = await db.execute(base_query)
        base_stats = base_result.first()
        
        # 计算平均交易金额
        avg_amount = 0
        if base_stats.total_transaction_count > 0:
            avg_amount = float(base_stats.total_transaction_amount) / base_stats.total_transaction_count
        
        # 信用等级分布
        credit_rating_query = select(
            func.coalesce(Supplier.credit_rating, 'unknown').label('credit_rating'),
            func.count(Supplier.id).label('count')
        ).where(
            Supplier.tenant_id == current_user.tenant_id
        ).group_by(func.coalesce(Supplier.credit_rating, 'unknown'))
        
        credit_rating_result = await db.execute(credit_rating_query)
        credit_rating_data = credit_rating_result.all()
        
        credit_rating_distribution = {}
        for row in credit_rating_data:
            credit_rating_distribution[row.credit_rating] = row.count
        
        # Top供应商查询
        top_suppliers_query = select(
            Supplier.id,
            Supplier.name,
            Supplier.total_amount,
            Supplier.transaction_count
        ).where(
            Supplier.tenant_id == current_user.tenant_id
        ).order_by(desc(Supplier.total_amount)).limit(10)
        
        top_suppliers_result = await db.execute(top_suppliers_query)
        top_suppliers_data = top_suppliers_result.all()
        
        top_suppliers = []
        for row in top_suppliers_data:
            top_suppliers.append({
                "id": str(row.id),
                "name": row.name,
                "total_amount": str(row.total_amount or 0),
                "transaction_count": int(row.transaction_count or 0)
            })
        
        # 月度趋势（最近12个月）  
        from datetime import timedelta
        twelve_months_ago = datetime.now() - timedelta(days=365)
        
        monthly_trend_query = select(
            extract('year', Supplier.created_at).label('year'),
            extract('month', Supplier.created_at).label('month'),
            func.count(Supplier.id).label('new_suppliers')
        ).where(
            and_(
                Supplier.tenant_id == current_user.tenant_id,
                Supplier.created_at >= twelve_months_ago
            )
        ).group_by(
            extract('year', Supplier.created_at),
            extract('month', Supplier.created_at)
        ).order_by(
            extract('year', Supplier.created_at),
            extract('month', Supplier.created_at)
        )
        
        monthly_trend_result = await db.execute(monthly_trend_query)
        monthly_trend_data = monthly_trend_result.all()
        
        monthly_trend = []
        for row in monthly_trend_data:
            monthly_trend.append({
                "year": int(row.year),
                "month": int(row.month),
                "new_suppliers": row.new_suppliers
            })
        
        # 构建响应
        statistics = {
            "total_suppliers": base_stats.total_suppliers,
            "active_suppliers": base_stats.active_suppliers,
            "inactive_suppliers": base_stats.inactive_suppliers,
            "total_transaction_amount": str(base_stats.total_transaction_amount),
            "total_transaction_count": base_stats.total_transaction_count,
            "average_transaction_amount": f"{avg_amount:.2f}",
            "credit_rating_distribution": credit_rating_distribution,
            "top_suppliers": top_suppliers,
            "monthly_trend": monthly_trend
        }
        
        return statistics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取供应商统计失败: {str(e)}"
        )

@router.get("/{supplier_id}/transactions", response_model=SupplierTransactionHistory, summary="获取供应商交易历史")
async def get_supplier_transactions(
    supplier_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(require_permissions(["supplier_read", "transaction_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商的交易历史记录
    
    需要权限: supplier_read, transaction_read
    """
    try:
        # 验证供应商存在
        supplier_query = select(Supplier).where(
            and_(
                Supplier.id == supplier_id,
                Supplier.tenant_id == current_user.tenant_id
            )
        )
        
        supplier_result = await db.execute(supplier_query)
        supplier = supplier_result.scalar_one_or_none()
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # 查询交易记录
        offset = (page - 1) * size
        transactions_query = select(Transaction).where(
            and_(
                Transaction.supplier_info.op('->>')('id') == supplier_id,
                Transaction.tenant_id == current_user.tenant_id
            )
        ).order_by(desc(Transaction.transaction_date)).offset(offset).limit(size)
        
        transactions_result = await db.execute(transactions_query)
        transactions = transactions_result.scalars().all()
        
        # 统计信息查询
        stats_query = select(
            func.coalesce(func.sum(Transaction.amount_base), 0).label('total_amount'),
            func.count(Transaction.id).label('transaction_count'),
            func.min(Transaction.transaction_date).label('first_date'),
            func.max(Transaction.transaction_date).label('last_date')
        ).where(
            and_(
                Transaction.supplier_info.op('->>')('id') == supplier_id,
                Transaction.tenant_id == current_user.tenant_id
            )
        )
        
        stats_result = await db.execute(stats_query)
        stats = stats_result.first()
        
        # 计算平均金额
        avg_amount = 0
        if stats.transaction_count > 0:
            avg_amount = float(stats.total_amount) / stats.transaction_count
        
        # 构建交易列表
        transactions_list = []
        for transaction in transactions:
            transaction_dict = {
                "id": str(transaction.id),
                "type": transaction.type,
                "amount": str(transaction.amount),
                "currency": transaction.currency,
                "description": transaction.description,
                "transaction_date": transaction.transaction_date.isoformat(),
                "status": transaction.status,
                "approval_status": transaction.approval_status
            }
            transactions_list.append(transaction_dict)
        
        # 构建响应
        response = {
            "supplier_id": supplier_id,
            "supplier_name": supplier.name,
            "transactions": transactions_list,
            "total_amount": str(stats.total_amount),
            "transaction_count": stats.transaction_count,
            "first_transaction_date": stats.first_date.isoformat() if stats.first_date else None,
            "last_transaction_date": stats.last_date.isoformat() if stats.last_date else None,
            "average_amount": f"{avg_amount:.2f}"
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取供应商交易历史失败: {str(e)}"
        )

@router.post("/batch", summary="批量操作供应商")
async def batch_supplier_operations(
    batch_request: SupplierBatchRequest,
    current_user: User = Depends(require_permissions(["supplier_update", "supplier_delete"])),
    db: AsyncSession = Depends(get_db)
):
    """
    批量操作供应商（激活、停用、删除）
    
    需要权限: supplier_update, supplier_delete
    """
    try:
        # 验证供应商存在
        suppliers_query = select(Supplier).where(
            and_(
                Supplier.id.in_(batch_request.supplier_ids),
                Supplier.tenant_id == current_user.tenant_id
            )
        )
        
        suppliers_result = await db.execute(suppliers_query)
        suppliers = suppliers_result.scalars().all()
        
        if len(suppliers) != len(batch_request.supplier_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部分供应商不存在"
            )
        
        success_count = 0
        error_messages = []
        
        for supplier in suppliers:
            try:
                if batch_request.action == "activate":
                    supplier.is_active = '1'
                    success_count += 1
                elif batch_request.action == "deactivate":
                    supplier.is_active = '0'
                    success_count += 1
                elif batch_request.action == "delete":
                    # 检查是否有关联交易
                    transaction_count_query = select(func.count(Transaction.id)).where(
                        and_(
                            Transaction.supplier_info.op('->>')('id') == str(supplier.id),
                            Transaction.tenant_id == current_user.tenant_id
                        )
                    )
                    
                    transaction_count_result = await db.execute(transaction_count_query)
                    transaction_count = transaction_count_result.scalar() or 0
                    
                    if transaction_count > 0:
                        error_messages.append(f"供应商 '{supplier.name}' 有 {transaction_count} 条关联交易，无法删除")
                    else:
                        await db.delete(supplier)
                        success_count += 1
                        
            except Exception as e:
                error_messages.append(f"处理供应商 '{supplier.name}' 时出错: {str(e)}")
        
        await db.commit()
        
        response_data = {
            "success_count": success_count,
            "total_count": len(batch_request.supplier_ids),
            "action": batch_request.action
        }
        
        if error_messages:
            response_data["errors"] = error_messages
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量操作失败: {str(e)}"
        )
