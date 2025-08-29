"""
监控系统独立认证接口
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional
import logging

from ...core.database import get_db
from ...core.auth import auth_manager
from ...models.user import User
from ...models.tenant import Tenant
from ...models.monitoring import AdminOperationLog

logger = logging.getLogger(__name__)
router = APIRouter()

# 监控系统默认管理员账号
MONITORING_ADMIN_EMAIL = "admin@monitoring.local"
MONITORING_ADMIN_PASSWORD = "Lovelewis@586930"

@router.post("/login")
async def monitoring_login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """监控系统管理员登录"""
    try:
        # 检查是否是监控系统管理员
        if email != MONITORING_ADMIN_EMAIL:
            raise HTTPException(
                status_code=401,
                detail="无效的管理员账号"
            )
        
        # 查询或创建默认管理员账号
        result = await db.execute(
            select(User).where(User.email == MONITORING_ADMIN_EMAIL)
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            # 创建默认管理员账号
            admin_user = await create_default_monitoring_admin(db)
        
        # 验证密码
        if not auth_manager.verify_password(password, admin_user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="密码错误"
            )
        
        # 检查用户状态
        if not admin_user.is_active:
            raise HTTPException(
                status_code=401,
                detail="账号已被禁用"
            )
        
        # 更新最后登录时间
        await db.execute(
            update(User)
            .where(User.id == admin_user.id)
            .values(last_login=datetime.utcnow())
        )
        await db.commit()
        
        # 生成访问令牌
        access_token = auth_manager.create_access_token(
            data={"sub": str(admin_user.id), "role": admin_user.role}
        )
        
        return {
            "success": True,
            "message": "登录成功",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(admin_user.id),
                "email": admin_user.email,
                "role": admin_user.role,
                "username": admin_user.username
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"监控系统登录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="登录失败")

async def create_default_monitoring_admin(db: AsyncSession) -> User:
    """创建默认监控系统管理员账号"""
    try:
        # 检查是否存在监控系统租户
        result = await db.execute(
            select(Tenant).where(Tenant.name == "监控系统")
        )
        monitoring_tenant = result.scalar_one_or_none()
        
        if not monitoring_tenant:
            # 创建监控系统租户
            monitoring_tenant = Tenant(
                name="监控系统",
                domain="monitoring.local",
                status="active"
            )
            db.add(monitoring_tenant)
            await db.flush()
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email=MONITORING_ADMIN_EMAIL,
            role="super_admin",
            is_active=True,
            tenant_id=monitoring_tenant.id,
            password_hash=auth_manager.get_password_hash(MONITORING_ADMIN_PASSWORD)
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        logger.info("默认监控系统管理员账号创建成功")
        return admin_user
        
    except Exception as e:
        logger.error(f"创建默认监控系统管理员失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建管理员账号失败")

@router.get("/profile")
async def get_monitoring_profile(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
):
    """获取监控系统管理员信息"""
    try:
        # 验证令牌
        payload = auth_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的令牌")
        
        # 查询用户
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        # 检查是否是监控系统管理员
        if user.email != MONITORING_ADMIN_EMAIL:
            raise HTTPException(status_code=403, detail="无权访问")
        
        return {
            "success": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "name": user.name,
                "last_login_at": user.last_login_at,
                "created_at": user.created_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取监控系统管理员信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")
