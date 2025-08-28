#!/usr/bin/env python3
"""
测试登录功能的脚本
"""

import asyncio
import asyncpg

async def test_login():
    """测试登录功能"""
    print("🔐 测试登录功能...")
    
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
        
        # 测试用户列表
        test_users = [
            ('admin@example.com', 'admin'),
            ('user123@example.com', 'password123'),
            ('testuser@example.com', 'test123456')
        ]
        
        for email, password in test_users:
            print(f"\n🔑 测试用户: {email}")
            
            # 查找用户
            user = await conn.fetchrow("""
                SELECT id, username, email, password_hash, role, permissions, tenant_id, is_active
                FROM users 
                WHERE email = $1
            """, email)
            
            if not user:
                print(f"   ❌ 用户不存在: {email}")
                continue
            
            if not user['is_active']:
                print(f"   ❌ 用户未激活: {email}")
                continue
            
            print(f"   ✅ 用户存在: {user['username']}")
            print(f"   ✅ 角色: {user['role']}")
            print(f"   ✅ 权限数量: {len(user['permissions'])}")
            print(f"   ✅ 租户ID: {user['tenant_id']}")
            
            # 检查密码哈希（这里只是演示，实际应该验证密码）
            if user['password_hash']:
                print(f"   ✅ 密码哈希已设置")
            else:
                print(f"   ❌ 密码哈希未设置")
        
        await conn.close()
        print("\n🎉 登录测试完成！")
        
    except Exception as e:
        print(f"❌ 测试登录失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login())
