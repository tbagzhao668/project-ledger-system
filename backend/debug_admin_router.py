#!/usr/bin/env python3
"""
调试admin路由
"""

import asyncio
from app.api.v1.admin import router

async def debug_router():
    """调试路由"""
    print("🔍 调试admin路由...")
    
    print(f"路由对象: {router}")
    print(f"路由前缀: {router.prefix}")
    print(f"路由标签: {router.tags}")
    
    # 检查路由列表
    print(f"\n路由列表:")
    for route in router.routes:
        print(f"  - {route.path} [{route.methods}] -> {route.name}")
    
    print(f"\n总路由数: {len(router.routes)}")

if __name__ == "__main__":
    asyncio.run(debug_router())
