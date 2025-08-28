"""
分类管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, asc
from typing import Optional, List
from datetime import datetime

from ...core.auth import get_current_user, require_permissions
from ...core.database import get_db
from ...models.user import User
from ...models.transaction import Category, Transaction
from ...schemas.transaction import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TransactionTypeEnum
)

router = APIRouter(prefix="/categories", tags=["分类管理"])

@router.post("/", response_model=CategoryResponse, summary="创建分类")
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_permissions(["category_create"])),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的分类
    
    需要权限: category_create
    """
    try:
        # 检查分类名称是否已存在
        existing_category = await db.execute(
            select(Category).where(
                and_(
                    Category.tenant_id == current_user.tenant_id,
                    Category.name == category_data.name
                )
            )
        )
        if existing_category.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类名称 '{category_data.name}' 已存在"
            )
        
        # 验证父分类（如果提供）
        if category_data.parent_id:
            parent_result = await db.execute(
                select(Category).where(
                    and_(
                        Category.id == category_data.parent_id,
                        Category.tenant_id == current_user.tenant_id
                    )
                )
            )
            if not parent_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父分类不存在"
                )
        
        # 创建分类
        new_category = Category(
            tenant_id=current_user.tenant_id,
            name=category_data.name,
            parent_id=category_data.parent_id,
            icon=category_data.icon,
            color=category_data.color,
            is_system='0',  # 用户创建的分类
            is_active='1',
            sort_order=str(category_data.sort_order)
        )
        
        db.add(new_category)
        await db.flush()
        await db.refresh(new_category)
        
        # 获取父分类名称
        parent_name = None
        if new_category.parent_id:
            parent_result = await db.execute(
                select(Category.name).where(Category.id == new_category.parent_id)
            )
            parent_name = parent_result.scalar_one_or_none()
        
        # 构建响应
        category_dict = {
            "id": str(new_category.id),
            "tenant_id": str(new_category.tenant_id),
            "name": new_category.name,
            "parent_id": str(new_category.parent_id) if new_category.parent_id else None,
            "parent_name": parent_name,
            "icon": new_category.icon,
            "color": new_category.color,
            "is_system": new_category.is_system == '1',
            "is_active": new_category.is_active == '1',
            "sort_order": int(new_category.sort_order or 0),
            "transaction_count": 0,
            "total_amount": 0,
            "created_at": new_category.created_at.isoformat(),
            "updated_at": new_category.updated_at.isoformat() if new_category.updated_at else None
        }
        
        await db.commit()
        
        return CategoryResponse(**category_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分类失败: {str(e)}"
        )

@router.get("/", response_model=List[CategoryResponse], summary="获取分类列表")
async def get_categories(
    parent_id: Optional[str] = Query(None, description="父分类ID筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    current_user: User = Depends(require_permissions(["category_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取分类列表
    
    需要权限: category_read
    """
    try:
        # 构建查询条件
        query_conditions = [Category.tenant_id == current_user.tenant_id]
        
        if parent_id:
            query_conditions.append(Category.parent_id == parent_id)
        elif parent_id == "":  # 查询顶级分类
            query_conditions.append(Category.parent_id.is_(None))
        
        if is_active is not None:
            query_conditions.append(Category.is_active == ('1' if is_active else '0'))
        
        # 查询分类（包含交易统计）
        categories_query = select(
            Category,
            func.count(Transaction.id).label('transaction_count'),
            func.coalesce(func.sum(Transaction.amount), 0).label('total_amount')
        ).outerjoin(Transaction, Category.id == Transaction.category_id).where(
            and_(*query_conditions)
        ).group_by(Category.id).order_by(
            asc(Category.sort_order),
            asc(Category.name)
        )
        
        categories_result = await db.execute(categories_query)
        categories_data = categories_result.all()
        
        # 获取所有父分类信息（用于显示父分类名称）
        parent_categories = {}
        parent_ids = [cat.Category.parent_id for cat in categories_data if cat.Category.parent_id]
        if parent_ids:
            parent_result = await db.execute(
                select(Category.id, Category.name).where(Category.id.in_(parent_ids))
            )
            parent_categories = {str(row.id): row.name for row in parent_result.all()}
        
        # 转换为响应格式
        category_list = []
        for row in categories_data:
            category = row.Category
            category_dict = {
                "id": str(category.id),
                "tenant_id": str(category.tenant_id),
                "name": category.name,
                "parent_id": str(category.parent_id) if category.parent_id else None,
                "parent_name": parent_categories.get(str(category.parent_id)) if category.parent_id else None,
                "icon": category.icon,
                "color": category.color,
                "is_system": category.is_system == '1',
                "is_active": category.is_active == '1',
                "sort_order": int(category.sort_order or 0),
                "transaction_count": row.transaction_count or 0,
                "total_amount": float(row.total_amount or 0),
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat() if category.updated_at else None
            }
            category_list.append(CategoryResponse(**category_dict))
        
        return category_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类列表失败: {str(e)}"
        )

@router.get("/{category_id}", response_model=CategoryResponse, summary="获取分类详情")
async def get_category(
    category_id: str,
    current_user: User = Depends(require_permissions(["category_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取分类详情
    
    需要权限: category_read
    """
    try:
        # 查询分类（包含交易统计）
        category_query = select(
            Category,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).select_from(
            Category.__table__.outerjoin(Transaction.__table__)
        ).where(
            and_(
                Category.id == category_id,
                Category.tenant_id == current_user.tenant_id
            )
        ).group_by(Category.id)
        
        category_result = await db.execute(category_query)
        category_data = category_result.first()
        
        if not category_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        category = category_data.Category
        
        # 获取父分类名称
        parent_name = None
        if category.parent_id:
            parent_result = await db.execute(
                select(Category.name).where(Category.id == category.parent_id)
            )
            parent_name = parent_result.scalar_one_or_none()
        
        # 构建响应
        category_dict = {
            "id": str(category.id),
            "tenant_id": str(category.tenant_id),
            "name": category.name,
            "parent_id": str(category.parent_id) if category.parent_id else None,
            "parent_name": parent_name,
            "icon": category.icon,
            "color": category.color,
            "is_system": category.is_system == '1',
            "is_active": category.is_active == '1',
            "sort_order": int(category.sort_order or 0),
            "transaction_count": category_data.transaction_count or 0,
            "total_amount": float(category_data.total_amount or 0),
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        }
        
        return CategoryResponse(**category_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类详情失败: {str(e)}"
        )

@router.put("/{category_id}", response_model=CategoryResponse, summary="更新分类")
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_permissions(["category_update"])),
    db: AsyncSession = Depends(get_db)
):
    """
    更新分类信息
    
    需要权限: category_update
    """
    try:
        category_result = await db.execute(
            select(Category).where(
                and_(
                    Category.id == category_id,
                    Category.tenant_id == current_user.tenant_id
                )
            )
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        # 检查系统分类是否可以编辑
        if category.is_system == '1':
            # 系统分类只能修改部分字段
            allowed_fields = ['icon', 'color', 'sort_order', 'is_active']
            update_data = category_data.dict(exclude_unset=True)
            if any(field not in allowed_fields for field in update_data.keys()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="系统分类只能修改图标、颜色、排序和激活状态"
                )
        
        # 检查分类名称是否重复（如果有更新名称）
        if category_data.name and category_data.name != category.name:
            existing_category = await db.execute(
                select(Category).where(
                    and_(
                        Category.tenant_id == current_user.tenant_id,
                        Category.name == category_data.name,
                        Category.id != category_id
                    )
                )
            )
            if existing_category.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"分类名称 '{category_data.name}' 已存在"
                )
        
        # 验证父分类（如果有更新）
        if category_data.parent_id:
            if category_data.parent_id == category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类不能设置自己为父分类"
                )
            
            parent_result = await db.execute(
                select(Category).where(
                    and_(
                        Category.id == category_data.parent_id,
                        Category.tenant_id == current_user.tenant_id
                    )
                )
            )
            if not parent_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父分类不存在"
                )
        
        # 更新分类字段
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(category, field):
                if field == 'is_active':
                    setattr(category, field, '1' if value else '0')
                elif field == 'sort_order':
                    setattr(category, field, str(value))
                else:
                    setattr(category, field, value)
        
        category.updated_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(category)
        
        # 获取父分类名称和统计信息
        parent_name = None
        if category.parent_id:
            parent_result = await db.execute(
                select(Category.name).where(Category.id == category.parent_id)
            )
            parent_name = parent_result.scalar_one_or_none()
        
        # 获取交易统计
        stats_result = await db.execute(
            select(
                func.count(Transaction.id).label('transaction_count'),
                func.sum(Transaction.amount).label('total_amount')
            ).where(Transaction.category_id == category_id)
        )
        stats = stats_result.first()
        
        # 构建响应
        category_dict = {
            "id": str(category.id),
            "tenant_id": str(category.tenant_id),
            "name": category.name,
            "parent_id": str(category.parent_id) if category.parent_id else None,
            "parent_name": parent_name,
            "icon": category.icon,
            "color": category.color,
            "is_system": category.is_system == '1',
            "is_active": category.is_active == '1',
            "sort_order": int(category.sort_order or 0),
            "transaction_count": stats.transaction_count or 0,
            "total_amount": float(stats.total_amount or 0),
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        }
        
        await db.commit()
        
        return CategoryResponse(**category_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分类失败: {str(e)}"
        )

@router.delete("/{category_id}", summary="删除分类")
async def delete_category(
    category_id: str,
    current_user: User = Depends(require_permissions(["category_delete"])),
    db: AsyncSession = Depends(get_db)
):
    """
    删除分类
    
    需要权限: category_delete
    """
    try:
        category_result = await db.execute(
            select(Category).where(
                and_(
                    Category.id == category_id,
                    Category.tenant_id == current_user.tenant_id
                )
            )
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        # 检查是否为系统分类
        if category.is_system == '1':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统分类不能删除"
            )
        
        # 检查是否有关联的交易记录
        transaction_count_result = await db.execute(
            select(func.count(Transaction.id)).where(Transaction.category_id == category_id)
        )
        transaction_count = transaction_count_result.scalar()
        
        if transaction_count > 0:
            # 如果有交易记录，执行软删除（设置为不激活）
            category.is_active = '0'
            category.updated_at = datetime.utcnow()
            await db.commit()
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "message": "分类已停用（因为存在关联的交易记录）",
                    "deleted": False,
                    "deactivated": True
                }
            )
        else:
            # 检查是否有子分类
            child_count_result = await db.execute(
                select(func.count(Category.id)).where(Category.parent_id == category_id)
            )
            child_count = child_count_result.scalar()
            
            if child_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该分类下还有子分类，无法删除"
                )
            
            # 可以真实删除
            await db.delete(category)
            await db.commit()
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "message": "分类已删除",
                    "deleted": True,
                    "deactivated": False
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分类失败: {str(e)}"
        )

@router.post("/initialize", summary="初始化系统分类")
async def initialize_system_categories(
    current_user: User = Depends(require_permissions(["category_create"])),
    db: AsyncSession = Depends(get_db)
):
    """
    为租户初始化系统默认分类
    
    需要权限: category_create
    """
    try:
        # 检查是否已经初始化过
        existing_count_result = await db.execute(
            select(func.count(Category.id)).where(
                and_(
                    Category.tenant_id == current_user.tenant_id,
                    Category.is_system == '1'
                )
            )
        )
        existing_count = existing_count_result.scalar()
        
        if existing_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统分类已经初始化过了"
            )
        
        # 系统默认分类定义
        default_categories = [
            {"name": "工程款收入", "icon": "💰", "color": "#52c41a", "sort": 1},
            {"name": "材料退款", "icon": "📦", "color": "#1890ff", "sort": 2},
            {"name": "其他收入", "icon": "💸", "color": "#722ed1", "sort": 3},
            {"name": "材料费", "icon": "🧱", "color": "#fa541c", "sort": 4},
            {"name": "人工费", "icon": "👷", "color": "#eb2f96", "sort": 5},
            {"name": "机械费", "icon": "🚛", "color": "#faad14", "sort": 6},
            {"name": "管理费", "icon": "📋", "color": "#13c2c2", "sort": 7},
            {"name": "差旅费", "icon": "✈️", "color": "#52c41a", "sort": 8},
            {"name": "办公费", "icon": "🏢", "color": "#1890ff", "sort": 9},
            {"name": "其他支出", "icon": "💳", "color": "#722ed1", "sort": 10},
        ]
        
        created_categories = []
        
        for cat_data in default_categories:
            new_category = Category(
                tenant_id=current_user.tenant_id,
                name=cat_data["name"],
                icon=cat_data["icon"],
                color=cat_data["color"],
                is_system='1',  # 系统分类
                is_active='1',
                sort_order=str(cat_data["sort"])
            )
            db.add(new_category)
            created_categories.append(cat_data["name"])
        
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "系统分类初始化完成",
                "created_count": len(created_categories),
                "categories": created_categories
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化系统分类失败: {str(e)}"
        )
