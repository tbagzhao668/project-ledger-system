#!/usr/bin/env python3
"""
最终状态检查脚本
"""

import asyncio
import asyncpg

async def final_status_check():
    """最终状态检查"""
    print("🎯 最终状态检查")
    print("=" * 50)
    
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
        
        # 1. 检查租户
        print("\n1. 📋 租户信息:")
        tenants = await conn.fetch("SELECT id, name, domain, status FROM tenants")
        for tenant in tenants:
            print(f"   - {tenant['name']} ({tenant['domain']}) - {tenant['status']}")
        
        # 2. 检查用户
        print("\n2. 👥 用户信息:")
        users = await conn.fetch("SELECT username, email, role, is_active FROM users")
        for user in users:
            print(f"   - {user['username']} ({user['email']}) - {user['role']} - {'激活' if user['is_active'] else '未激活'}")
        
        # 3. 检查项目
        print("\n3. 🏗️ 项目信息:")
        projects = await conn.fetch("SELECT name, project_code, category, priority, status FROM projects")
        for project in projects:
            print(f"   - {project['name']} ({project['project_code']}) - {project['category']} - {project['priority']} - {project['status']}")
        
        # 4. 检查财务记录
        print("\n4. 💰 财务记录:")
        transactions = await conn.fetch("SELECT type, amount, description FROM transactions LIMIT 5")
        for trans in transactions:
            print(f"   - {trans['type']}: {trans['amount']} - {trans['description']}")
        
        # 5. 检查分类
        print("\n5. 🏷️ 财务分类:")
        categories = await conn.fetch("SELECT name, color FROM categories")
        for cat in categories:
            print(f"   - {cat['name']} ({cat['color']})")
        
        # 6. 统计信息
        print("\n6. 📊 统计信息:")
        tenant_count = await conn.fetchval("SELECT COUNT(*) FROM tenants")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        project_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        transaction_count = await conn.fetchval("SELECT COUNT(*) FROM transactions")
        category_count = await conn.fetchval("SELECT COUNT(*) FROM categories")
        
        print(f"   - 租户数量: {tenant_count}")
        print(f"   - 用户数量: {user_count}")
        print(f"   - 项目数量: {project_count}")
        print(f"   - 财务记录: {transaction_count}")
        print(f"   - 财务分类: {category_count}")
        
        await conn.close()
        
        print("\n" + "=" * 50)
        print("🎉 业务部署完成！")
        print("\n🌐 系统访问信息:")
        print("   - 前端地址: http://localhost:3000")
        print("   - 后端API: http://localhost:8000")
        print("   - API文档: http://localhost:8000/docs")
        print("   - 健康检查: http://localhost:8000/health")
        print("\n🔑 测试账号:")
        print("   - 管理员: admin@example.com / admin")
        print("   - 测试用户: user123@example.com / password123")
        
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(final_status_check())
