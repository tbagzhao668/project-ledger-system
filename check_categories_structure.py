#!/usr/bin/env python3
"""
检查categories表结构的脚本
"""

import asyncio
import asyncpg

async def check_categories_structure():
    """检查categories表结构"""
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='project_ledger'
        )
        
        print("🔍 检查categories表结构...")
        result = await conn.fetch(
            "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'categories' ORDER BY ordinal_position"
        )
        
        print("📋 categories表列信息:")
        for row in result:
            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   {row['column_name']}: {row['data_type']} {nullable}")
        
        # 检查categories表中的数据
        print("\n🔍 检查categories表中的数据...")
        categories_data = await conn.fetch("SELECT * FROM categories LIMIT 5")
        print(f"📊 找到 {len(categories_data)} 个分类")
        
        if categories_data:
            for cat in categories_data:
                print(f"   - {cat}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 检查categories表结构失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_categories_structure())
