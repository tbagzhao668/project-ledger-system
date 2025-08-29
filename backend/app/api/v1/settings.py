from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
import json

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.settings import SystemSettings, SecuritySettings, SettingsResponse

router = APIRouter()

@router.get("/system", response_model=SettingsResponse, summary="获取系统设置")
async def get_system_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前租户的系统设置
    """
    try:
        # 查询租户信息（确保租户隔离）
        tenant_result = await db.execute(
            select(Tenant).where(
                Tenant.id == current_user.tenant_id,
                Tenant.status == 'active'  # 只查询活跃租户
            )
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="租户不存在或已停用"
            )
        
        # 从租户设置中获取系统配置（确保租户隔离）
        settings = tenant.settings or {}
        
        system_settings = SystemSettings(
            system_name=settings.get('system_name', '工程项目流水账'),
            description=settings.get('description', '专业的工程项目财务管理系统')
        )
        
        security_settings = SecuritySettings(
            session_timeout=settings.get('session_timeout', 120)
        )
        
        return SettingsResponse(
            success=True,
            message="获取系统设置成功",
            data={
                "system": system_settings,
                "security": security_settings
            }
        )
        
    except Exception as e:
        print(f"获取系统设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统设置失败"
        )

@router.put("/system", response_model=SettingsResponse, summary="更新系统设置")
async def update_system_settings(
    system_settings: SystemSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前租户的系统设置
    """
    try:
        # 检查权限（只有super_admin可以修改系统设置）
        if current_user.role != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，只有超级管理员可以修改系统设置"
            )
        
        # 查询租户信息（确保租户隔离）
        tenant_result = await db.execute(
            select(Tenant).where(
                Tenant.id == current_user.tenant_id,
                Tenant.status == 'active'  # 只查询活跃租户
            )
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="租户不存在或已停用"
            )
        
        # 验证系统名称
        if not system_settings.system_name or not system_settings.system_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统名称不能为空"
            )
        
        # 更新租户设置（确保租户隔离）
        current_settings = tenant.settings or {}
        new_settings = {
            **current_settings,
            'system_name': system_settings.system_name.strip(),
            'description': system_settings.description or ''
        }
        
        # 更新数据库（确保租户隔离）
        tenant.settings = new_settings
        await db.commit()
        
        print(f"系统设置已更新: {new_settings}")
        
        return SettingsResponse(
            success=True,
            message="系统设置更新成功",
            data={
                "system": system_settings,
                "security": SecuritySettings(
                    session_timeout=current_settings.get('session_timeout', 120)
                )
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新系统设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新系统设置失败"
        )

@router.put("/security", response_model=SettingsResponse, summary="更新安全设置")
async def update_security_settings(
    security_settings: SecuritySettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前租户的安全设置
    """
    try:
        # 检查权限（只有super_admin可以修改安全设置）
        if current_user.role != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，只有超级管理员可以修改安全设置"
            )
        
        # 验证会话超时时间
        if not security_settings.session_timeout or security_settings.session_timeout < 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="会话超时时间不能少于15分钟"
            )
        
        if security_settings.session_timeout > 1440:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="会话超时时间不能超过1440分钟（24小时）"
            )
        
        # 查询租户信息（确保租户隔离）
        tenant_result = await db.execute(
            select(Tenant).where(
                Tenant.id == current_user.tenant_id,
                Tenant.status == 'active'  # 只查询活跃租户
            )
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="租户不存在或已停用"
            )
        
        # 更新租户设置（确保租户隔离）
        current_settings = tenant.settings or {}
        new_settings = {
            **current_settings,
            'session_timeout': security_settings.session_timeout
        }
        
        # 更新数据库（确保租户隔离）
        tenant.settings = new_settings
        await db.commit()
        
        print(f"安全设置已更新: {new_settings}")
        
        return SettingsResponse(
            success=True,
            message="安全设置更新成功",
            data={
                "system": SystemSettings(
                    system_name=current_settings.get('system_name', '工程项目流水账'),
                    description=current_settings.get('description', '专业的工程项目财务管理系统')
                ),
                "security": security_settings
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新安全设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新安全设置失败"
        )

@router.get("/test", summary="测试路由")
async def test_settings_route():
    """测试系统设置路由是否正常工作"""
    return {"message": "系统设置路由正常工作", "status": "success"}
