#!/usr/bin/env python3
"""
创建测试用户脚本
"""

import asyncio
import asyncpg
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

async def create_test_user():
    """创建测试用户"""
    print("🔧 开始创建测试用户...")
    
    try:
        # 获取数据库连接
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': '123456',
            'database': 'project_ledger'
        }
        
        conn = await asyncpg.connect(**db_config)
        
        # 检查租户是否存在
        tenant_result = await conn.fetchrow(
            "SELECT id, name FROM tenants WHERE name = '测试租户' LIMIT 1"
        )
        
        if not tenant_result:
            print("📝 创建测试租户...")
            tenant_result = await conn.fetchrow(
                "INSERT INTO tenants (id, name, domain, plan_type, status, created_at) VALUES (gen_random_uuid(), '测试租户', 'test.local', 'basic', 'active', NOW()) RETURNING id, name"
            )
            print(f"✅ 租户创建成功: {tenant_result['name']}")
        else:
            print(f"✅ 租户已存在: {tenant_result['name']}")
        
        tenant_id = tenant_result['id']
        
        # 检查用户是否存在
        user_result = await conn.fetchrow(
            "SELECT id, username, email FROM users WHERE email = 'user123@example.com' LIMIT 1"
        )
        
        if not user_result:
            print("📝 创建测试用户...")
            hashed_password = get_password_hash("password123")
            
            user_result = await conn.fetchrow(
                """
                INSERT INTO users (
                    id, tenant_id, username, email, password_hash, 
                    role, permissions, is_active, email_verified, 
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), $1, 'user123', 'user123@example.com', $2,
                    'admin', $3, true, true, NOW(), NOW()
                ) RETURNING id, username, email
                """,
                tenant_id, hashed_password, '["project_create", "project_update", "project_delete"]'
            )
            print(f"✅ 用户创建成功: {user_result['username']} ({user_result['email']})")
        else:
            print(f"✅ 用户已存在: {user_result['username']} ({user_result['email']})")
        
        print("🎉 测试用户创建完成！")
        print(f"   用户名: user123")
        print(f"   邮箱: user123@example.com")
        print(f"   密码: password123")
        print(f"   角色: admin")
        print(f"   权限: project_create, project_update, project_delete")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 创建测试用户失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_user())
