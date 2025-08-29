#!/usr/bin/env python3
"""
调试应用启动
"""

import asyncio
from app.main import app
from app.api.v1.admin import router as admin_router

async def debug_startup():
    """调试应用启动"""
    print("🔍 调试应用启动...")
    
    print(f"应用对象: {app}")
    print(f"应用标题: {app.title}")
    
    # 检查admin路由
    print(f"\nAdmin路由对象: {admin_router}")
    print(f"Admin路由数量: {len(admin_router.routes)}")
    
    # 检查admin路由详情
    print(f"\nAdmin路由详情:")
    for route in admin_router.routes:
        print(f"  - {route.path} [{route.methods}] -> {route.name}")
    
    # 检查应用中的admin路由
    print(f"\n应用中的admin路由:")
    admin_routes = [r for r in app.routes if hasattr(r, 'path') and '/admin' in r.path]
    for route in admin_routes:
        print(f"  - {route.path} [{route.methods}] -> {route.name}")
    
    print(f"\n应用中的admin路由数量: {len(admin_routes)}")
    
    # 检查是否有重复路由
    paths = [r.path for r in app.routes if hasattr(r, 'path')]
    duplicates = [p for p in set(paths) if paths.count(p) > 1]
    if duplicates:
        print(f"\n⚠️ 发现重复路由: {duplicates}")
    else:
        print(f"\n✅ 没有重复路由")

if __name__ == "__main__":
    asyncio.run(debug_startup())
