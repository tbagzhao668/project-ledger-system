#!/usr/bin/env python3
"""检查数据库用户数量"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def check_users():
    try:
        from app.core.database import db_manager
        from app.models.user import User
        from sqlalchemy import text
        
        # 初始化数据库连接
        await db_manager.initialize()
        
        # 获取会话
        async for session in db_manager.get_session():
            try:
                # 查询用户数量
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                print(f"数据库中的用户数量: {user_count}")
                
                # 查询前几个用户
                if user_count > 0:
                    result = await session.execute(text("SELECT id, username, email, role FROM users LIMIT 5"))
                    users = result.fetchall()
                    print("\n前5个用户:")
                    for user in users:
                        print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}")
                break
            except Exception as e:
                print(f"查询错误: {e}")
                break
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_users())
