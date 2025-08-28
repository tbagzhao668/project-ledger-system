#!/usr/bin/env python3
"""
直接创建项目数据的脚本
"""

import asyncio
import asyncpg
from datetime import date

async def create_projects_direct():
    """直接创建项目数据"""
    print("🚀 开始创建项目数据...")
    
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
        
        # 获取租户ID
        tenant_result = await conn.fetchrow(
            "SELECT id FROM tenants WHERE name = '测试租户' LIMIT 1"
        )
        
        if not tenant_result:
            print("❌ 未找到测试租户，请先创建租户")
            return
        
        tenant_id = tenant_result['id']
        print(f"✅ 使用租户ID: {tenant_id}")
        
        # 获取用户ID
        user_result = await conn.fetchrow(
            "SELECT id FROM users WHERE email = 'user123@example.com' LIMIT 1"
        )
        
        if not user_result:
            print("❌ 未找到测试用户，请先创建用户")
            return
        
        user_id = user_result['id']
        print(f"✅ 使用用户ID: {user_id}")
        
        # 创建项目
        print("\n📝 创建项目...")
        projects = [
            ('上海浦东办公楼', 'SHPD001', '建筑工程', 'high', date(2024, 1, 1), date(2024, 12, 31), '张经理'),
            ('北京地铁站装修', 'BJDT001', '装修工程', 'medium', date(2024, 2, 1), date(2024, 8, 31), '李经理'),
            ('广州设备安装', 'GZSBAZ001', '设备安装', 'low', date(2024, 3, 1), date(2024, 6, 30), '王经理'),
            ('深圳市政道路', 'SZSZDL001', '市政工程', 'high', date(2024, 4, 1), date(2024, 11, 30), '陈经理')
        ]
        
        for name, code, category, priority, start_date, end_date, manager_name in projects:
            existing = await conn.fetchrow(
                "SELECT id FROM projects WHERE name = $1 AND tenant_id = $2",
                name, tenant_id
            )
            if not existing:
                await conn.execute(
                    """
                    INSERT INTO projects (
                        id, tenant_id, name, project_code, category, priority,
                        start_date, end_date, manager_name, status, created_by, updated_by,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, 'active', $9, $9, NOW(), NOW()
                    )
                    """,
                    tenant_id, name, code, category, priority, start_date, end_date, 
                    manager_name, user_id
                )
                print(f"✅ 项目创建成功: {name}")
            else:
                print(f"✅ 项目已存在: {name}")
        
        # 检查项目数量
        project_count = await conn.fetchval(
            "SELECT COUNT(*) FROM projects WHERE tenant_id = $1",
            tenant_id
        )
        print(f"\n📊 当前项目总数: {project_count}")
        
        await conn.close()
        print("\n🎉 项目数据创建完成！")
        
    except Exception as e:
        print(f"❌ 创建项目数据失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_projects_direct())
