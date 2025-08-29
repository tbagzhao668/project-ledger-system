#!/usr/bin/env python3
"""
检查项目表中的manager_name字段
"""

import asyncio
import asyncpg

async def check_manager_field():
    """检查manager_name字段是否存在"""
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="123456",
            database="project_management"
        )
        
        # 检查字段是否存在
        result = await conn.fetchrow("""
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'manager_name'
        """)
        
        if result:
            print("✅ manager_name字段已成功添加:")
            print(f"   字段名: {result['column_name']}")
            print(f"   数据类型: {result['data_type']}")
            print(f"   是否可为空: {result['is_nullable']}")
            print(f"   默认值: {result['column_default']}")
            print(f"   最大长度: {result['character_maximum_length']}")
        else:
            print("❌ manager_name字段不存在")
        
        # 显示表结构
        print("\n📋 项目表结构:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'projects'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"   {col['column_name']:<20} {col['data_type']:<15} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_manager_field())
