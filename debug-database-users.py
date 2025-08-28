#!/usr/bin/env python3
"""
检查数据库中的用户数据
"""
import asyncio
import asyncpg
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "123456",
    "database": "project_ledger"
}

async def check_database_users():
    """检查数据库中的用户数据"""
    print("🔍 检查数据库中的用户数据...")
    print("=" * 50)
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        
        # 1. 检查用户表结构
        print("\n1. 检查用户表结构...")
        table_info = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        print(f"   - 用户表有 {len(table_info)} 个字段:")
        for col in table_info:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"     - {col['column_name']}: {col['data_type']} {nullable} {default}")
        
        # 2. 检查用户数量
        print("\n2. 检查用户数量...")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"   - 总用户数: {user_count}")
        
        # 3. 检查具体用户数据
        print("\n3. 检查具体用户数据...")
        users = await conn.fetch("""
            SELECT id, email, username, role, is_active, created_at, tenant_id
            FROM users 
            ORDER BY created_at DESC
        """)
        
        if users:
            print(f"   - 找到 {len(users)} 个用户:")
            for user in users:
                print(f"     - ID: {user['id']}")
                print(f"       - 邮箱: {user['email']}")
                print(f"       - 用户名: {user['username']}")
                print(f"       - 角色: {user['role']}")
                print(f"       - 是否激活: {user['is_active']}")
                print(f"       - 租户ID: {user['tenant_id']}")
                print(f"       - 创建时间: {user['created_at']}")
                print()
        else:
            print("   ❌ 没有找到用户数据")
        
        # 4. 检查租户数据
        print("4. 检查租户数据...")
        tenant_count = await conn.fetchval("SELECT COUNT(*) FROM tenants")
        print(f"   - 总租户数: {tenant_count}")
        
        tenants = await conn.fetch("SELECT id, name, domain FROM tenants")
        if tenants:
            print(f"   - 租户列表:")
            for tenant in tenants:
                print(f"     - ID: {tenant['id']}")
                print(f"       - 名称: {tenant['name']}")
                print(f"       - 域名: {tenant['domain']}")
                print()
        
        # 5. 检查项目数据
        print("5. 检查项目数据...")
        project_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        print(f"   - 总项目数: {project_count}")
        
        if project_count > 0:
            projects = await conn.fetch("""
                SELECT id, name, project_code, tenant_id, status, created_at
                FROM projects 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            print(f"   - 最近的项目:")
            for project in projects:
                print(f"     - ID: {project['id']}")
                print(f"       - 名称: {project['name']}")
                print(f"       - 编号: {project['project_code']}")
                print(f"       - 租户ID: {project['tenant_id']}")
                print(f"       - 状态: {project['status']}")
                print(f"       - 创建时间: {project['created_at']}")
                print()
        
        # 6. 尝试创建一个测试用户
        print("6. 尝试创建测试用户...")
        try:
            # 检查是否已存在测试用户
            existing_user = await conn.fetchval(
                "SELECT id FROM users WHERE email = $1",
                "testuser@example.com"
            )
            
            if existing_user:
                print("   - 测试用户已存在，跳过创建")
            else:
                # 创建测试用户
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed_password = pwd_context.hash("test123456")
                
                # 获取第一个租户ID
                tenant_id = await conn.fetchval("SELECT id FROM tenants LIMIT 1")
                if not tenant_id:
                    print("   ❌ 没有找到租户，无法创建用户")
                else:
                    # 插入测试用户
                    user_id = await conn.fetchval("""
                        INSERT INTO users (email, username, password_hash, role, is_active, tenant_id, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING id
                    """, "testuser@example.com", "testuser", hashed_password, "admin", True, tenant_id, datetime.utcnow())
                    
                    print(f"   ✅ 测试用户创建成功，ID: {user_id}")
                    print(f"   - 邮箱: testuser@example.com")
                    print(f"   - 密码: test123456")
                    print(f"   - 角色: admin")
                    print(f"   - 租户ID: {tenant_id}")
        except Exception as e:
            print(f"   ❌ 创建测试用户失败: {e}")
        
        await conn.close()
        print("\n✅ 数据库检查完成")
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

async def main():
    """主函数"""
    print("🚀 开始检查数据库用户数据")
    print("=" * 60)
    
    await check_database_users()
    
    print("\n🎉 检查完成!")
    print("\n📝 请根据上述信息分析用户数据问题")

if __name__ == "__main__":
    asyncio.run(main())
