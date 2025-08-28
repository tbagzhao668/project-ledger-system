"""
租户管理API接口
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import secrets
import string
import time
import logging

from ...core.database import get_db
from ...core.auth import require_super_admin
from ...models.monitoring import AdminOperationLog
from ...models.user import User
from ...models.tenant import Tenant
from ...models.project import Project
from ...models.transaction import Transaction
logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/tenants")
async def get_tenants(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取租户列表"""
    try:
        # 构建查询
        query = select(Tenant).options(
            selectinload(Tenant.users),
            selectinload(Tenant.projects)
        )
        
        # 添加筛选条件
        if status:
            query = query.where(Tenant.status == status)
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Tenant.name.ilike(search_filter)) |
                (Tenant.domain.ilike(search_filter))
            )
        
        # 获取总数
        count_query = select(func.count(Tenant.id))
        if status:
            count_query = count_query.where(Tenant.status == status)
        if search:
            search_filter = f"%{search}%"
            count_query = count_query.where(
                (Tenant.name.ilike(search_filter)) |
                (Tenant.domain.ilike(search_filter))
            )
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(desc(Tenant.created_at))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        tenants = result.scalars().all()
        
        # 构建响应数据
        tenant_list = []
        for tenant in tenants:
            # 获取租户统计信息
            users_count = len(tenant.users) if tenant.users else 0
            projects_count = len(tenant.projects) if tenant.projects else 0
            
            # 获取最后登录时间
            last_login = None
            if tenant.users:
                last_login = max(
                    (user.last_login for user in tenant.users if user.last_login),
                    default=None
                )
            
            tenant_info = {
                "id": str(tenant.id),
                "name": tenant.name,
                "domain": tenant.domain,
                "status": tenant.status,
                "created_at": tenant.created_at,
                "last_login": last_login,
                "users_count": users_count,
                "projects_count": projects_count
            }
            tenant_list.append(tenant_info)
        
        return {
            "tenants": tenant_list,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"获取租户列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取租户列表失败")

@router.get("/tenants/{tenant_id}")
async def get_tenant_detail(
    tenant_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取租户详细信息"""
    try:
        # 查询租户
        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 获取租户统计信息
        users_result = await db.execute(
            select(User).where(User.tenant_id == tenant_id)
        )
        users = users_result.scalars().all()
        
        projects_result = await db.execute(
            select(Project).where(Project.tenant_id == tenant_id)
        )
        projects = projects_result.scalars().all()
        
        transactions_result = await db.execute(
            select(Transaction).where(Transaction.tenant_id == tenant_id)
        )
        transactions = transactions_result.scalars().all()
        
        # 构建响应数据
        tenant_detail = {
            "id": str(tenant.id),
            "name": tenant.name,
                            "domain": tenant.domain,
            "status": tenant.status,
            "created_at": tenant.created_at,
            "updated_at": tenant.updated_at,
            "statistics": {
                "users_count": len(users),
                "projects_count": len(projects),
                "transactions_count": len(transactions)
            },
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "last_login": user.last_login,
                    "created_at": user.created_at
                }
                for user in users
            ]
        }
        
        return tenant_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取租户详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取租户详情失败")

@router.put("/tenants/{tenant_id}/status")
async def update_tenant_status(
    tenant_id: str,
    status: str = Query(..., description="租户状态"),
    reason: str = Query("", description="操作原因"),
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """更新租户状态（启用/禁用）"""
    try:
        new_status = status
        
        if new_status not in ['active', 'disabled']:
            raise HTTPException(
                status_code=400,
                detail="状态值无效，必须是 'active' 或 'disabled'"
            )
        
        # 检查租户是否存在
        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 防止禁用监控系统租户
        if tenant.name == "监控系统" and new_status == "disabled":
            raise HTTPException(status_code=400, detail="不能禁用监控系统租户")
        
        # 获取租户当前状态
        old_status = tenant.status
        
        # 更新租户状态
        await db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(
                status=new_status,
                updated_at=func.now()
            )
        )
        
        # 如果禁用租户，同时禁用该租户下的所有用户
        if new_status == 'disabled':
            await db.execute(
                update(User)
                .where(User.tenant_id == tenant_id)
                .values(
                    is_active=False,
                    updated_at=func.now()
                )
            )
        # 如果启用租户，同时启用该租户下的所有用户
        elif new_status == 'active':
            await db.execute(
                update(User)
                .where(User.tenant_id == tenant_id)
                .values(
                    is_active=True,
                    updated_at=func.now()
                )
            )
        
        await db.commit()
        
        # 记录操作日志
        await log_admin_operation(
            operation_type="update_tenant_status",
            target_type="tenant",
            target_id=tenant_id,
            operation_details={
                "tenant_name": tenant.name,
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "users_affected": True  # 无论是启用还是禁用，都会影响用户状态
            },
            request=request,
            current_user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "message": f"租户状态更新成功",
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "old_status": old_status,
            "new_status": new_status,
            "reason": reason,
            "note": f"租户已{new_status == 'active' and '启用' or '禁用'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新租户状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新租户状态失败")

@router.post("/tenants/{tenant_id}/reset-password")
async def reset_tenant_password(
    tenant_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """重置租户密码"""
    try:
        # 查询租户
        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 生成新密码
        new_password = generate_secure_password()
        
        # 更新租户下所有用户的密码
        from ...core.auth import auth_manager
        hashed_password = auth_manager.get_password_hash(new_password)
        
        # 先查询租户下的所有用户
        users_result = await db.execute(
            select(User).where(User.tenant_id == tenant_id)
        )
        users = users_result.scalars().all()
        
        if not users:
            raise HTTPException(status_code=404, detail="租户下没有用户")
        
        # 更新所有用户的密码
        for user in users:
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(password_hash=hashed_password, updated_at=func.now())
            )
        
        await db.commit()
        
        # 记录操作日志
        await log_admin_operation(
            operation_type="reset_tenant_password",
            target_type="tenant",
            target_id=tenant_id,
            operation_details={
                "tenant_name": tenant.name,
                "password_reset": True
            },
            request=request,
            current_user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "message": "租户密码重置成功",
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "new_password": new_password,
            "note": "请将新密码安全地发送给租户"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置租户密码失败: {str(e)}")
        raise HTTPException(status_code=500, detail="重置租户密码失败")

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """删除租户（危险操作）"""
    try:
        # 检查租户是否存在
        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 防止删除监控系统租户
        if tenant.name == "监控系统":
            raise HTTPException(status_code=400, detail="不能删除监控系统租户")
        
        # 获取租户下的所有数据统计
        users_count = await db.execute(
            select(func.count(User.id)).where(User.tenant_id == tenant_id)
        )
        users_count = users_count.scalar() or 0
        
        projects_count = await db.execute(
            select(func.count(Project.id)).where(Project.tenant_id == tenant_id)
        )
        projects_count = projects_count.scalar() or 0
        
        transactions_count = await db.execute(
            select(func.count(Transaction.id)).where(Transaction.tenant_id == tenant_id)
        )
        transactions_count = transactions_count.scalar() or 0
        
        # 记录删除前的租户信息
        tenant_info = {
            "id": str(tenant.id),
            "name": tenant.name,
            "domain": tenant.domain,
            "users_count": users_count,
            "projects_count": projects_count,
            "transactions_count": transactions_count
        }
        
        # 执行删除操作（级联删除）
        # 注意：这里使用原生SQL来确保级联删除
        async with db.begin():
            # 删除财务记录
            await db.execute(
                "DELETE FROM transactions WHERE tenant_id = $1",
                tenant_id
            )
            
            # 删除项目
            await db.execute(
                "DELETE FROM projects WHERE tenant_id = $1",
                tenant_id
            )
            
            # 删除分类
            await db.execute(
                "DELETE FROM categories WHERE tenant_id = $1",
                tenant_id
            )
            
            # 删除供应商
            await db.execute(
                "DELETE FROM suppliers WHERE tenant_id = $1",
                tenant_id
            )
            
            # 删除用户
            await db.execute(
                "DELETE FROM users WHERE tenant_id = $1",
                tenant_id
            )
            
            # 删除租户
            await db.execute(
                "DELETE FROM tenants WHERE id = $1",
                tenant_id
            )
        
        # 记录操作日志
        await log_admin_operation(
            operation_type="delete_tenant",
            target_type="tenant",
            target_id=tenant_id,
            operation_details={
                "tenant_info": tenant_info,
                "deleted_data": {
                    "users": users_count,
                    "projects": projects_count,
                    "transactions": transactions_count
                }
            },
            request=request,
            current_user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "message": "租户删除成功",
            "deleted_tenant": tenant_info,
            "warning": "此操作不可逆，所有相关数据已被永久删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除租户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除租户失败")

def generate_secure_password(length: int = 12) -> str:
    """生成安全密码"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    # 确保密码包含至少一个大写字母、小写字母和数字
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    
    return password

async def log_admin_operation(
    operation_type: str,
    target_type: str,
    target_id: Optional[str] = None,
    operation_details: Optional[Dict[str, Any]] = None,
    request: Request = None,
    current_user: User = None,
    db: AsyncSession = None
):
    """记录管理员操作日志"""
    try:
        # 获取客户端IP和用户代理
        client_ip = None
        user_agent = None
        
        if request:
            client_ip = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        # 创建操作日志
        log = AdminOperationLog(
            admin_user_id=current_user.id if current_user else None,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            operation_details=operation_details,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        if db:
            db.add(log)
            await db.commit()
        
    except Exception as e:
        logger.error(f"记录操作日志失败: {str(e)}")
        # 不抛出异常，避免影响主要业务逻辑

@router.put("/tenants/{tenant_id}/users/{user_id}/status")
async def update_user_status(
    tenant_id: str,
    user_id: str,
    is_active: bool = Query(..., description="用户状态"),
    reason: str = Query("", description="操作原因"),
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """更新用户状态（启用/禁用）"""
    try:
        # 检查租户是否存在
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 检查用户是否存在且属于该租户
        user_result = await db.execute(
            select(User).where(
                User.id == user_id,
                User.tenant_id == tenant_id
            )
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在或不属于该租户")
        
        # 防止禁用监控系统管理员账号
        if user.email == "admin@monitoring.local" and not is_active:
            raise HTTPException(
                status_code=400, 
                detail="不能禁用监控系统管理员账号"
            )
        
        # 记录旧状态
        old_status = user.is_active
        
        # 更新用户状态
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                is_active=is_active,
                updated_at=func.now()
            )
        )
        
        await db.commit()
        
        # 记录操作日志
        await log_admin_operation(
            operation_type="update_user_status",
            target_type="user",
            target_id=user_id,
            operation_details={
                "tenant_id": tenant_id,
                "tenant_name": tenant.name,
                "user_email": user.email,
                "old_status": old_status,
                "new_status": is_active,
                "reason": reason
            },
            request=request,
            current_user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "message": f"用户状态更新成功",
            "user_id": user_id,
            "user_email": user.email,
            "tenant_name": tenant.name,
            "old_status": old_status,
            "new_status": is_active,
            "reason": reason,
            "note": f"用户已{'启用' if is_active else '禁用'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新用户状态失败")

@router.delete("/tenants/{tenant_id}/users/{user_id}")
async def delete_user(
    tenant_id: str,
    user_id: str,
    reason: str = Query("", description="删除原因"),
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """删除用户"""
    try:
        # 检查租户是否存在
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 检查用户是否存在且属于该租户
        user_result = await db.execute(
            select(User).where(
                User.id == user_id,
                User.tenant_id == tenant_id
            )
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在或不属于该租户")
        
        # 防止删除监控系统管理员账号
        if user.email == "admin@monitoring.local":
            raise HTTPException(
                status_code=400, 
                detail="不能删除监控系统管理员账号"
            )
        
        # 记录删除前的用户信息
        user_info = {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
        
        # 删除用户
        await db.execute(
            "DELETE FROM users WHERE id = $1",
            user_id
        )
        
        await db.commit()
        
        # 记录操作日志
        await log_admin_operation(
            operation_type="delete_user",
            target_type="user",
            target_id=user_id,
            operation_details={
                "tenant_id": tenant_id,
                "tenant_name": tenant.name,
                "deleted_user": user_info,
                "reason": reason
            },
            request=request,
            current_user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "message": "用户删除成功",
            "deleted_user": user_info,
            "tenant_name": tenant.name,
            "reason": reason,
            "warning": "此操作不可逆，用户已被永久删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除用户失败")

@router.put("/tenants/{tenant_id}/users/{user_id}/role")
async def update_user_role(
    tenant_id: str,
    user_id: str,
    role: str = Query(..., description="新角色"),
    reason: str = Query("", description="修改原因"),
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """更新用户角色"""
    try:
        # 验证角色是否有效
        valid_roles = ["super_admin", "admin", "user", "viewer"]
        if role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"角色值无效，必须是以下之一: {', '.join(valid_roles)}"
            )
        
        # 检查租户是否存在
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
        
        # 检查用户是否存在且属于该租户
        user_result = await db.execute(
            select(User).where(
                User.id == user_id,
                User.tenant_id == tenant_id
            )
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在或不属于该租户")
        
        # 防止修改监控系统管理员账号角色
        if user.email == "admin@monitoring.local" and role != "super_admin":
            raise HTTPException(
                status_code=400, 
                detail="不能修改监控系统管理员账号角色"
            )
        
        # 记录旧角色
        old_role = user.role
        
        # 更新用户角色
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                role=role,
                updated_at=func.now()
            )
        )
        
        await db.commit()
        
        # 记录操作日志
        await log_admin_operation(
            operation_type="update_user_role",
            target_type="user",
            target_id=user_id,
            operation_details={
                "tenant_id": tenant_id,
                "tenant_name": tenant.name,
                "user_email": user.email,
                "old_role": old_role,
                "new_role": role,
                "reason": reason
            },
            request=request,
            current_user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "message": "用户角色更新成功",
            "user_id": user_id,
            "user_email": user.email,
            "tenant_name": tenant.name,
            "old_role": old_role,
            "new_role": role,
            "reason": reason,
            "note": f"用户角色已从 {old_role} 更改为 {role}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户角色失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新用户角色失败")
