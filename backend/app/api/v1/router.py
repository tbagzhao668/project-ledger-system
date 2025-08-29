"""
API v1 路由集合
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from .auth import router as auth_router, login as auth_login
from .projects import router as projects_router
from .transactions import router as transactions_router
from .categories import router as categories_router
from .suppliers import router as suppliers_router
from .settings import router as settings_router
from .admin import router as admin_router
from .monitoring import router as monitoring_router
from .admin_auth import router as admin_auth_router
from ...core.database import get_db
from ...schemas.auth import UserLogin, TokenResponse

# 创建API v1路由器
api_router = APIRouter(prefix="/api/v1")

# 添加直接的登录端点（为了兼容前端）
@api_router.post("/login", response_model=TokenResponse, summary="用户登录")
async def direct_login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """直接登录端点（不带/auth前缀）"""
    return await auth_login(login_data, db)

# 注册各个模块的路由
api_router.include_router(auth_router, tags=["认证"])
api_router.include_router(projects_router, tags=["项目管理"])
api_router.include_router(transactions_router, tags=["财务记录"])
api_router.include_router(categories_router, tags=["分类管理"])
api_router.include_router(suppliers_router, tags=["供应商管理"])
api_router.include_router(settings_router, tags=["系统设置"])
api_router.include_router(admin_auth_router, prefix="/monitoring", tags=["监控系统认证"])
api_router.include_router(admin_router, prefix="/admin", tags=["租户管理"])
api_router.include_router(monitoring_router, prefix="/admin", tags=["系统监控"])

# 稍后添加其他路由
# api_router.include_router(reports_router, tags=["报表分析"])
