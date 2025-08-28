#!/usr/bin/env python3
"""
检查数据库中的数据
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append('.')

async def check_data():
    try:
        from app.core.database import db_manager
        from app.models.project import Project
        from app.models.user import User
        from sqlalchemy import select
        
        # 初始化数据库连接
        db_manager.initialize()
        
        async with db_manager.engine.begin() as conn:
            print("检查数据库中的数据...")
            
            # 检查项目
            projects_result = await conn.execute(
                select(Project.tenant_id, Project.name).limit(3)
            )
            projects = projects_result.fetchall()
            print(f"找到 {len(projects)} 个项目:")
            for p in projects:
                print(f"  租户ID: {p.tenant_id}, 项目名: {p.name}")
            
            # 检查用户
            users_result = await conn.execute(
                select(User.tenant_id, User.username).limit(3)
            )
            users = users_result.fetchall()
            print(f"找到 {len(users)} 个用户:")
            for u in users:
                print(f"  租户ID: {u.tenant_id}, 用户名: {u.username}")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_data())
