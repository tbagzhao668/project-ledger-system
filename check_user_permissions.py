#!/usr/bin/env python3
"""
检查用户权限配置的脚本
"""

import asyncio
import asyncpg

async def check_user_permissions():
    """检查用户权限配置"""
    print("🔍 检查用户权限配置...")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='project_ledger'
        )
        print("✅ 数据库连接成功")
        
        # 检查用户权限
        print("\n1. 👥 用户权限信息:")
        users = await conn.fetch("""
            SELECT id, username, email, role, permissions, is_active 
            FROM users 
            ORDER BY created_at
        """)
        
        for user in users:
            print(f"\n   - 用户: {user['username']} ({user['email']})")
            print(f"     角色: {user['role']}")
            print(f"     权限: {user['permissions']}")
            print(f"     状态: {'激活' if user['is_active'] else '未激活'}")
        
        # 检查租户信息
        print("\n2. 🏢 租户信息:")
        tenants = await conn.fetch("SELECT id, name, domain, status FROM tenants")
        for tenant in tenants:
            print(f"   - {tenant['name']} ({tenant['domain']}) - {tenant['status']}")
        
        # 检查是否有超级管理员权限的用户
        print("\n3. 🔑 超级管理员检查:")
        super_admin = await conn.fetchrow("""
            SELECT username, email, permissions 
            FROM users 
            WHERE role = 'admin' AND permissions::text LIKE '%*%'
            LIMIT 1
        """)
        
        if super_admin:
            print(f"   ✅ 找到超级管理员: {super_admin['username']}")
            print(f"      权限: {super_admin['permissions']}")
        else:
            print("   ❌ 没有找到超级管理员权限的用户")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 检查用户权限失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user_permissions())
