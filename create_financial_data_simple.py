#!/usr/bin/env python3
"""
创建简单财务数据的脚本
"""

import asyncio
import asyncpg
from datetime import date
from decimal import Decimal

async def create_financial_data():
    """创建财务数据"""
    print("💰 开始创建财务数据...")
    
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
            print("❌ 未找到测试租户")
            return
        
        tenant_id = tenant_result['id']
        print(f"✅ 使用租户ID: {tenant_id}")
        
        # 获取用户ID
        user_result = await conn.fetchrow(
            "SELECT id FROM users WHERE email = 'user123@example.com' LIMIT 1"
        )
        
        if not user_result:
            print("❌ 未找到测试用户")
            return
        
        user_id = user_result['id']
        print(f"✅ 使用用户ID: {user_id}")
        
        # 获取项目列表
        projects = await conn.fetch(
            "SELECT id, name FROM projects WHERE tenant_id = $1 LIMIT 4",
            tenant_id
        )
        
        if not projects:
            print("❌ 未找到项目数据")
            return
        
        print(f"✅ 找到 {len(projects)} 个项目")
        
        # 创建财务记录
        print("\n📝 创建财务记录...")
        
        for project_id, project_name in projects:
            # 检查是否已有财务记录
            existing = await conn.fetchval(
                "SELECT COUNT(*) FROM transactions WHERE project_id = $1",
                project_id
            )
            
            if existing == 0:
                # 创建收入记录
                await conn.execute(
                    """
                    INSERT INTO transactions (
                        id, tenant_id, project_id, type, amount, currency, description,
                        transaction_date, status, created_by, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), $1, $2, 'income', $3, 'CNY', $4, $5, 'confirmed', $6, NOW(), NOW()
                    )
                    """,
                    tenant_id, project_id, Decimal('1000000.00'), f'{project_name}合同款', date.today(), user_id
                )
                
                # 创建支出记录
                await conn.execute(
                    """
                    INSERT INTO transactions (
                        id, tenant_id, project_id, type, amount, currency, description,
                        transaction_date, status, created_by, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), $1, $2, 'expense', $3, 'CNY', $4, $5, 'confirmed', $6, NOW(), NOW()
                    )
                    """,
                    tenant_id, project_id, Decimal('300000.00'), f'{project_name}材料费', date.today(), user_id
                )
                
                print(f"✅ 财务记录创建成功: {project_name}")
            else:
                print(f"✅ 财务记录已存在: {project_name}")
        
        # 检查财务记录数量
        transaction_count = await conn.fetchval(
            "SELECT COUNT(*) FROM transactions WHERE tenant_id = $1",
            tenant_id
        )
        print(f"\n📊 当前财务记录总数: {transaction_count}")
        
        await conn.close()
        print("\n🎉 财务数据创建完成！")
        
    except Exception as e:
        print(f"❌ 创建财务数据失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_financial_data())
