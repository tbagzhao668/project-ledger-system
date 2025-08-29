#!/usr/bin/env python3
"""
调试路由注册
"""

import asyncio
from app.main import app

async def debug_routes():
    """调试路由"""
    print("🔍 调试路由注册...")
    
    print(f"应用对象: {app}")
    print(f"应用标题: {app.title}")
    
    # 检查所有路由
    print(f"\n所有路由:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.path} [{getattr(route, 'methods', ['N/A'])}] -> {getattr(route, 'name', 'N/A')}")
    
    print(f"\n总路由数: {len(app.routes)}")
    
    # 检查API路由
    print(f"\nAPI路由:")
    for route in app.routes:
        if hasattr(route, 'path') and route.path.startswith('/api'):
            print(f"  - {route.path} [{getattr(route, 'methods', ['N/A'])}] -> {getattr(route, 'name', 'N/A')}")
    
    # 检查admin路由
    print(f"\nAdmin路由:")
    for route in app.routes:
        if hasattr(route, 'path') and '/admin' in route.path:
            print(f"  - {route.path} [{getattr(route, 'methods', ['N/A'])}] -> {getattr(route, 'name', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(debug_routes())
