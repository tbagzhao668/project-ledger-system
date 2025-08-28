#!/usr/bin/env python3
"""
检查数据库表结构脚本
"""

import asyncio
import asyncpg

async def check_table_structure():
    """检查数据库表结构"""
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='project_ledger'
        )
        
        print("🔍 检查users表结构...")
        result = await conn.fetch(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
        )
        
        print("📋 users表列信息:")
        for row in result:
            print(f"   {row['column_name']}: {row['data_type']}")
        
        print("\n🔍 检查tenants表结构...")
        result = await conn.fetch(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tenants' ORDER BY ordinal_position"
        )
        
        print("📋 tenants表列信息:")
        for row in result:
            print(f"   {row['column_name']}: {row['data_type']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_table_structure())
