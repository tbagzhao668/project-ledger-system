"""
监控系统API接口
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, Date
from typing import List, Optional, Dict, Any
import asyncio
import time
import logging
from datetime import datetime, date, timedelta

from ...core.database import get_db
from ...core.auth import get_current_user, require_super_admin
from ...models.monitoring import MonitoringData, AdminOperationLog, SystemStatistics, TenantActivity, HealthCheck
from ...models.user import User
from ...models.tenant import Tenant
from ...models.project import Project
from ...models.transaction import Transaction

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """系统健康检查"""
    try:
        # 检查数据库连接
        db_start = time.time()
        db_result = await db.execute(select(1))
        db_time = int((time.time() - db_start) * 1000)
        
        # 检查关键服务
        services_status = {
            "database": {
                "status": "healthy" if db_result else "unhealthy",
                "response_time": db_time,
                "last_check": time.time()
            }
        }
        
        # 记录健康检查结果
        health_check = HealthCheck(
            service_name="system_overall",
            status="healthy" if db_result else "unhealthy",
            response_time=db_time,
            check_details=services_status
        )
        db.add(health_check)
        await db.commit()
        
        return {
            "status": "healthy" if db_result else "unhealthy",
            "services": services_status,
            "timestamp": time.time(),
            "response_time": db_time
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")

@router.get("/health/api-endpoints")
async def api_endpoints_health_check(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """API端点健康检查"""
    try:
        import httpx
        from ...main import app
        
        # 获取所有注册的路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/v1'):
                routes.append({
                    'path': route.path,
                    'name': route.name or 'Unknown',
                    'methods': [method for method in route.methods if method != 'HEAD'] if hasattr(route, 'methods') else []
                })
        
        # 定义需要测试的API端点
        api_endpoints = [
            {"path": "/api/v1/auth/login", "method": "POST", "name": "用户登录"},
            {"path": "/api/v1/projects", "method": "GET", "name": "项目列表"},
            {"path": "/api/v1/transactions", "method": "GET", "name": "财务记录列表"},
            {"path": "/api/v1/categories", "method": "GET", "name": "分类列表"},
            {"path": "/api/v1/suppliers", "method": "GET", "name": "供应商列表"},
            {"path": "/api/v1/admin/tenants", "method": "GET", "name": "租户管理"},
            {"path": "/api/v1/admin/health", "method": "GET", "name": "系统监控"},
            {"path": "/api/v1/monitoring/login", "method": "POST", "name": "监控系统登录"},
        ]
        
        endpoint_status = []
        overall_status = "healthy"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in api_endpoints:
                try:
                    start_time = time.time()
                    
                    # 对于GET端点，尝试不同的检查方法
                    if endpoint["method"] == "GET":
                        try:
                            # 首先尝试HEAD请求
                            response = await client.head(f"http://localhost:8000{endpoint['path']}")
                            status_code = response.status_code
                        except:
                            # 如果HEAD失败，尝试GET请求
                            try:
                                response = await client.get(f"http://localhost:8000{endpoint['path']}")
                                status_code = response.status_code
                            except:
                                response = None
                                status_code = "ERROR"
                        
                        response_time = int((time.time() - start_time) * 1000)
                        
                        # 检查状态码
                        if status_code in [200, 401, 403]:  # 200成功，401/403需要认证
                            status = "healthy"
                        elif status_code == 307:  # 重定向，通常是正常的
                            status = "healthy"
                        elif status_code == 405:  # 方法不允许，但端点存在
                            status = "healthy"
                        elif status_code == 404:
                            status = "not_found"
                        else:
                            status = "unhealthy"
                            overall_status = "unhealthy"
                    else:
                        # 对于POST等需要认证的端点，检查路由是否存在
                        status = "requires_auth"
                        response_time = 0
                        status_code = "N/A"
                    
                    endpoint_status.append({
                        "endpoint": endpoint["name"],
                        "path": endpoint["path"],
                        "method": endpoint["method"],
                        "status": status,
                        "status_code": status_code,
                        "response_time": response_time,
                        "last_check": time.time()
                    })
                    
                except Exception as e:
                    endpoint_status.append({
                        "endpoint": endpoint["name"],
                        "path": endpoint["path"],
                        "method": endpoint["method"],
                        "status": "error",
                        "status_code": "ERROR",
                        "response_time": 0,
                        "last_check": time.time(),
                        "error": str(e)
                    })
                    overall_status = "unhealthy"
        
        # 记录API端点健康检查结果
        health_check = HealthCheck(
            service_name="api_endpoints",
            status=overall_status,
            response_time=0,
            check_details={"endpoints": endpoint_status}
        )
        db.add(health_check)
        await db.commit()
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "total_endpoints": len(api_endpoints),
            "healthy_endpoints": len([ep for ep in endpoint_status if ep["status"] == "healthy"]),
            "unhealthy_endpoints": len([ep for ep in endpoint_status if ep["status"] == "unhealthy"]),
            "endpoints": endpoint_status
        }
        
    except Exception as e:
        logger.error(f"API端点健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="API端点健康检查失败")

@router.get("/health/detailed")
async def detailed_health_check(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """详细健康检查（包含所有检查项）"""
    try:
        # 执行基础健康检查
        basic_health = await health_check(current_user, db)
        
        # 执行API端点健康检查
        api_health = await api_endpoints_health_check(current_user, db)
        
        # 获取系统资源状态
        import psutil
        system_status = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_connections": len(psutil.net_connections()),
            "process_count": len(psutil.pids())
        }
        
        # 检查Redis连接（如果配置了）
        redis_status = {"status": "not_configured"}
        try:
            from ...core.config import settings
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                import redis
                r = redis.Redis.from_url(settings.REDIS_URL)
                r.ping()
                redis_status = {"status": "healthy", "response_time": 0}
            else:
                redis_status = {"status": "not_configured"}
        except Exception:
            redis_status = {"status": "unhealthy"}
        
        # 综合状态
        overall_status = "healthy"
        if (basic_health["status"] == "unhealthy" or 
            api_health["status"] == "unhealthy" or
            system_status["cpu_percent"] > 90 or
            system_status["memory_percent"] > 90 or
            system_status["disk_percent"] > 90):
            overall_status = "unhealthy"
        
        detailed_status = {
            "status": overall_status,
            "timestamp": time.time(),
            "basic_health": basic_health,
            "api_endpoints": api_health,
            "system_resources": system_status,
            "redis": redis_status
        }
        
        # 记录详细健康检查结果
        detailed_health_record = HealthCheck(
            service_name="detailed_system_check",
            status=overall_status,
            response_time=0,
            check_details=detailed_status
        )
        db.add(detailed_health_record)
        await db.commit()
        
        return detailed_status
        
    except Exception as e:
        logger.error(f"详细健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="详细健康检查失败")

@router.get("/overview")
async def get_system_overview(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统概览统计"""
    try:
        # 获取基础统计
        total_tenants_result = await db.execute(select(func.count(Tenant.id)))
        total_tenants = total_tenants_result.scalar() or 0
        
        total_projects_result = await db.execute(select(func.count(Project.id)))
        total_projects = total_projects_result.scalar() or 0
        
        total_transactions_result = await db.execute(select(func.count(Transaction.id)))
        total_transactions = total_transactions_result.scalar() or 0
        
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0
        
        # 获取今日新增租户数
        from datetime import date
        today = date.today()
        today_tenants_result = await db.execute(
            select(func.count(Tenant.id)).where(
                func.date_trunc('day', Tenant.created_at) == today
            )
        )
        today_new_tenants = today_tenants_result.scalar() or 0
        
        # 获取活跃租户数（最近7天有登录的）
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_tenants_result = await db.execute(
            select(func.count(func.distinct(User.tenant_id))).where(
                User.last_login >= seven_days_ago
            )
        )
        active_tenants = active_tenants_result.scalar() or 0
        
        overview = {
            "total_tenants": total_tenants,
            "total_projects": total_projects,
            "total_transactions": total_transactions,
            "total_users": total_users,
            "today_new_tenants": today_new_tenants,
            "active_tenants": active_tenants,
            "system_uptime": time.time(),
            "last_updated": time.time()
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"获取系统概览失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取系统概览失败")

@router.get("/monitoring")
async def get_monitoring_data(
    service_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取监控数据"""
    try:
        query = select(MonitoringData).order_by(desc(MonitoringData.created_at))
        
        if service_name:
            query = query.where(MonitoringData.service_name == service_name)
        if status:
            query = query.where(MonitoringData.status == status)
            
        query = query.limit(limit)
        
        result = await db.execute(query)
        monitoring_data = result.scalars().all()
        
        return [
            {
                "id": str(item.id),
                "tenant_id": str(item.tenant_id) if item.tenant_id else None,
                "service_name": item.service_name,
                "status": item.status,
                "response_time": item.response_time,
                "error_message": item.error_message,
                "extra_data": item.extra_data,
                "created_at": item.created_at
            }
            for item in monitoring_data
        ]
        
    except Exception as e:
        logger.error(f"获取监控数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取监控数据失败")

@router.get("/admin-logs")
async def get_admin_operation_logs(
    operation_type: Optional[str] = None,
    target_type: Optional[str] = None,
    admin_user_id: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取管理员操作日志"""
    try:
        query = select(AdminOperationLog).order_by(desc(AdminOperationLog.created_at))
        
        if operation_type:
            query = query.where(AdminOperationLog.operation_type == operation_type)
        if target_type:
            query = query.where(AdminOperationLog.target_type == target_type)
        if admin_user_id:
            query = query.where(AdminOperationLog.admin_user_id == admin_user_id)
            
        query = query.limit(limit)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "id": str(item.id),
                "admin_user_id": str(item.admin_user_id),
                "operation_type": item.operation_type,
                "target_type": item.target_type,
                "target_id": str(item.target_id) if item.target_id else None,
                "operation_details": item.operation_details,
                "ip_address": str(item.ip_address) if item.ip_address else None,
                "user_agent": item.user_agent,
                "created_at": item.created_at
            }
            for item in logs
        ]
        
    except Exception as e:
        logger.error(f"获取管理员操作日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取管理员操作日志失败")

@router.post("/log-operation")
async def log_admin_operation(
    operation_type: str,
    target_type: str,
    target_id: Optional[str] = None,
    operation_details: Optional[Dict[str, Any]] = None,
    request: Request = None,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
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
            admin_user_id=current_user.id,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            operation_details=operation_details,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        db.add(log)
        await db.commit()
        
        return {"success": True, "message": "操作日志记录成功"}
        
    except Exception as e:
        logger.error(f"记录操作日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail="记录操作日志失败")
