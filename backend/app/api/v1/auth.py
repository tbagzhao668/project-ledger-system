"""
认证API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import uuid

from ...core.auth import auth_manager, get_current_user, security
from ...core.database import get_db
from ...models.user import User
from ...models.tenant import Tenant
from ...schemas.auth import (
    UserLogin, UserRegister, TenantRegister,
    TokenResponse, RefreshTokenRequest,
    PasswordReset, PasswordResetConfirm,
    TenantResponse, UserResponse
)

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=dict, summary="租户注册")
async def register_tenant(
    register_data: TenantRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    租户注册 - 创建新的租户和管理员账号
    """
    # 验证密码匹配
    register_data.validate_passwords_match()
    
    # 检查邮箱是否已存在
    existing_user = await db.execute(
        select(User).where(User.email == register_data.admin_email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 生成租户域名 (简化版，基于企业名称)
    tenant_domain = register_data.company_name.lower().replace(" ", "")[:10]
    
    # 检查域名是否已存在
    existing_tenant = await db.execute(
        select(Tenant).where(Tenant.domain == tenant_domain)
    )
    if existing_tenant.scalar_one_or_none():
        # 如果域名冲突，添加随机后缀
        tenant_domain += str(uuid.uuid4().hex)[:6]
    
    try:
        # 创建租户
        new_tenant = Tenant(
            name=register_data.company_name,
            domain=tenant_domain,
            plan_type="trial",  # 默认试用版
            settings={
                "industry_type": register_data.industry_type,
                "company_size": register_data.company_size
            }
        )
        db.add(new_tenant)
        await db.flush()  # 获取租户ID
        
        # 创建管理员用户
        admin_user = User(
            tenant_id=new_tenant.id,
            username=register_data.admin_name,
            email=register_data.admin_email,
            password_hash=auth_manager.get_password_hash(register_data.password),
            role="super_admin",
            permissions=["*"],  # 超级管理员拥有所有权限
            profile={
                "name": register_data.admin_name,
                "phone": register_data.admin_phone
            },
            is_active=True,
            email_verified=False  # 需要邮箱验证
        )
        db.add(admin_user)
        
        await db.commit()
        await db.refresh(new_tenant)
        await db.refresh(admin_user)
        
        return {
            "success": True,
            "message": "注册成功！请查收邮箱验证邮件",
            "data": {
                "tenant_id": str(new_tenant.id),
                "domain": new_tenant.domain,
                "admin_email": admin_user.email,
                "trial_expires": "30天后"
            }
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录 - 验证用户名密码并返回JWT令牌
    """
    # 认证用户
    user = await auth_manager.authenticate_user(
        db, login_data.email, login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取租户信息
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == user.tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    
    if not tenant or tenant.status != "active":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="租户账号已停用"
        )
    
    # 生成令牌
    access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
    access_token = auth_manager.create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id)},
        expires_delta=access_token_expires
    )
    
    refresh_token = auth_manager.create_refresh_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id)}
    )
    
    # 在事务内获取所有需要的属性，避免延迟加载
    user_data = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "permissions": user.permissions or [],
        "profile": user.profile or {},
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "login_count": user.login_count,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "two_factor_enabled": user.two_factor_enabled,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }
    
    # 更新登录信息
    user.login_count += 1
    user.last_login = datetime.utcnow()
    user_data["login_count"] = user.login_count
    user_data["last_login"] = user.last_login.isoformat()
    
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=user_data
    )

@router.post("/refresh", response_model=TokenResponse, summary="刷新令牌")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    """
    try:
        # 验证刷新令牌
        payload = auth_manager.verify_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        # 查询用户
        user_result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已停用"
            )
        
        # 查询租户
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant or tenant.status != "active":
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="租户账号已停用"
            )
        
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        new_access_token = auth_manager.create_access_token(
            data={"sub": str(user.id), "tenant_id": str(tenant.id)},
            expires_delta=access_token_expires
        )
        
        # 在事务内获取用户数据
        user_data = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "permissions": user.permissions or [],
            "profile": user.profile or {},
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_data.refresh_token,  # 刷新令牌保持不变
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="令牌刷新失败"
        )

@router.post("/logout", summary="用户登出")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    用户登出 - 在实际应用中，这里可以将令牌加入黑名单
    """
    # TODO: 将令牌加入Redis黑名单
    return {
        "success": True,
        "message": "登出成功"
    }

@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前认证用户的详细信息
    """
    # 在事务内获取所有用户数据，避免延迟加载
    user_data = {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "permissions": current_user.permissions or [],
        "profile": current_user.profile or {},
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "login_count": current_user.login_count,
        "is_active": current_user.is_active,
        "email_verified": current_user.email_verified,
        "two_factor_enabled": current_user.two_factor_enabled,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }
    
    # 获取租户信息
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = tenant_result.scalar_one()
    
    return user_data

@router.put("/me", summary="更新当前用户资料")
async def update_current_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前认证用户的个人资料
    
    注意：邮箱地址不可修改，只能修改其他个人信息
    """
    try:
        # 从profile_data中提取可更新的字段
        allowed_fields = {
            'name', 'phone', 'position', 'department', 'bio', 'avatar'
        }
        
        # 过滤只允许更新的字段
        update_data = {}
        for field, value in profile_data.items():
            if field in allowed_fields and value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="没有提供可更新的字段"
            )
        
        # 更新用户资料
        if not current_user.profile:
            current_user.profile = {}
        
        # 创建新的profile对象，确保PostgreSQL能正确识别变更
        new_profile = dict(current_user.profile)
        new_profile.update(update_data)
        
        # 直接赋值新的profile对象
        current_user.profile = new_profile
        current_user.updated_at = datetime.utcnow()
        
        print(f"DEBUG: 更新前profile: {current_user.profile}")
        
        await db.commit()
        
        print(f"DEBUG: 提交后profile: {current_user.profile}")
        
        # 重新查询以确保数据一致性
        await db.refresh(current_user)
        
        print(f"DEBUG: 刷新后profile: {current_user.profile}")
        
        return {
            "success": True,
            "message": "个人资料更新成功",
            "data": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role,
                "profile": current_user.profile or {},
                "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新个人资料失败: {str(e)}"
        )

@router.put("/me/password", summary="修改当前用户密码")
async def change_current_user_password(
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改当前认证用户的密码
    
    需要提供：旧密码、新密码、确认新密码
    """
    try:
        # 验证请求数据
        old_password = password_data.get('old_password')
        new_password = password_data.get('new_password')
        confirm_password = password_data.get('confirm_password')
        
        if not all([old_password, new_password, confirm_password]):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="请提供完整的密码信息：旧密码、新密码、确认新密码"
            )
        
        # 验证新密码和确认密码是否一致
        if new_password != confirm_password:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="新密码和确认密码不一致"
            )
        
        # 验证新密码长度
        if len(new_password) < 6:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="新密码长度不能少于6位"
            )
        
        # 验证旧密码是否正确
        if not auth_manager.verify_password(old_password, current_user.password_hash):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="旧密码不正确"
            )
        
        # 验证新密码不能与旧密码相同
        if old_password == new_password:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与旧密码相同"
            )
        
        # 更新密码
        current_user.password_hash = auth_manager.get_password_hash(new_password)
        current_user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(current_user)
        
        return {
            "success": True,
            "message": "密码修改成功",
            "data": {
                "id": str(current_user.id),
                "email": current_user.email,
                "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )

@router.get("/tenant", summary="获取当前用户所属租户信息")
async def get_current_user_tenant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前认证用户所属租户的详细信息
    """
    try:
        # 获取租户信息
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == current_user.tenant_id)
        )
        tenant = tenant_result.scalar_one()
        
        if not tenant:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="租户信息不存在"
            )
        
        return {
            "success": True,
            "data": {
                "id": str(tenant.id),
                "name": tenant.name,
                "domain": tenant.domain,
                "plan_type": tenant.plan_type,
                "settings": tenant.settings or {},
                "subscription_end": tenant.subscription_end.isoformat() if tenant.subscription_end else None,
                "storage_used": tenant.storage_used,
                "storage_limit": tenant.storage_limit,
                "api_calls_used": tenant.api_calls_used,
                "api_calls_limit": tenant.api_calls_limit,
                "status": tenant.status,
                "created_at": tenant.created_at.isoformat(),
                "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取租户信息失败: {str(e)}"
        )

@router.put("/tenant", summary="更新当前用户所属租户信息")
async def update_current_user_tenant(
    tenant_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前认证用户所属租户的信息
    
    注意：只有超级管理员可以更新租户信息
    """
    try:
        # 检查用户权限
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以更新租户信息"
            )
        
        # 获取租户信息
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == current_user.tenant_id)
        )
        tenant = tenant_result.scalar_one()
        
        if not tenant:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="租户信息不存在"
            )
        
        # 从tenant_data中提取可更新的字段
        allowed_fields = {
            'name', 'industry_type', 'company_size'
        }
        
        # 过滤只允许更新的字段
        update_data = {}
        for field, value in tenant_data.items():
            if field in allowed_fields and value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="没有提供可更新的字段"
            )
        
        # 更新租户信息
        if 'name' in update_data:
            tenant.name = update_data['name']
        
        # 更新租户设置
        if not tenant.settings:
            tenant.settings = {}
        
        # 创建新的settings字典，确保PostgreSQL能正确识别变更
        new_settings = dict(tenant.settings)
        
        if 'industry_type' in update_data:
            new_settings['industry_type'] = update_data['industry_type']
        
        if 'company_size' in update_data:
            new_settings['company_size'] = update_data['company_size']
        
        # 直接赋值新的settings对象
        tenant.settings = new_settings
        tenant.updated_at = datetime.utcnow()
        
        print(f"DEBUG: 更新前settings: {tenant.settings}")
        
        await db.commit()
        
        print(f"DEBUG: 提交后settings: {tenant.settings}")
        
        # 重新查询以确保数据一致性
        await db.refresh(tenant)
        
        print(f"DEBUG: 刷新后settings: {tenant.settings}")
        
        return {
            "success": True,
            "message": "租户信息更新成功",
            "data": {
                "id": str(tenant.id),
                "name": tenant.name,
                "settings": tenant.settings or {},
                "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新租户信息失败: {str(e)}"
        )
