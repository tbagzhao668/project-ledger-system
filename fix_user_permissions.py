#!/usr/bin/env python3
"""
修复用户权限配置的脚本
"""

import asyncio
import asyncpg
import json

async def fix_user_permissions():
    """修复用户权限配置"""
    print("🔧 修复用户权限配置...")
    
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
        
        # 定义完整权限列表
        full_permissions = [
            "project_create", "project_read", "project_update", "project_delete",
            "transaction_create", "transaction_read", "transaction_update", "transaction_delete",
            "category_create", "category_read", "category_update", "category_delete",
            "supplier_create", "supplier_read", "supplier_update", "supplier_delete",
            "user_create", "user_read", "user_update", "user_delete",
            "tenant_read", "tenant_update",
            "report_read", "dashboard_read"
        ]
        
        # 修复admin用户权限
        print("\n1. 🔑 修复admin用户权限...")
        await conn.execute("""
            UPDATE users 
            SET permissions = $1::jsonb 
            WHERE email = 'admin@example.com'
        """, json.dumps(full_permissions))
        print("   ✅ admin用户权限已更新为完整权限")
        
        # 修复testuser用户权限
        print("\n2. 🔑 修复testuser用户权限...")
        await conn.execute("""
            UPDATE users 
            SET permissions = $1::jsonb 
            WHERE email = 'testuser@example.com'
        """, json.dumps(full_permissions))
        print("   ✅ testuser用户权限已更新为完整权限")
        
        # 扩展user123用户权限
        print("\n3. 🔑 扩展user123用户权限...")
        user123_permissions = [
            "project_create", "project_read", "project_update", "project_delete",
            "transaction_create", "transaction_read", "transaction_update", "transaction_delete",
            "category_read", "supplier_read", "report_read", "dashboard_read"
        ]
        await conn.execute("""
            UPDATE users 
            SET permissions = $1::jsonb 
            WHERE email = 'user123@example.com'
        """, json.dumps(user123_permissions))
        print("   ✅ user123用户权限已扩展")
        
        # 验证修复结果
        print("\n4. ✅ 验证修复结果...")
        users = await conn.fetch("""
            SELECT username, email, permissions 
            FROM users 
            ORDER BY created_at
        """)
        
        for user in users:
            print(f"   - {user['username']} ({user['email']}): {len(user['permissions'])} 个权限")
        
        await conn.close()
        print("\n🎉 用户权限修复完成！")
        
    except Exception as e:
        print(f"❌ 修复用户权限失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_user_permissions())
