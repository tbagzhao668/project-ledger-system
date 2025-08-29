#!/usr/bin/env python3
"""
检查项目分类表的脚本
"""

import asyncio
import asyncpg

async def check_project_categories():
    """检查项目分类表"""
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='project_ledger'
        )
        
        print("🔍 检查所有表...")
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
        )
        
        print("📋 数据库中的表:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # 检查是否有project_categories表
        print("\n🔍 检查项目分类相关表...")
        project_categories_tables = [t for t in tables if 'project' in t['table_name'].lower() and 'categor' in t['table_name'].lower()]
        
        if project_categories_tables:
            print("📋 找到项目分类相关表:")
            for table in project_categories_tables:
                print(f"   - {table['table_name']}")
        else:
            print("❌ 没有找到项目分类表")
        
        # 检查projects表结构
        print("\n🔍 检查projects表结构...")
        try:
            project_columns = await conn.fetch(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'projects' ORDER BY ordinal_position"
            )
            print("📋 projects表列信息:")
            for col in project_columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"   {col['column_name']}: {col['data_type']} {nullable}")
        except Exception as e:
            print(f"❌ 检查projects表失败: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 检查项目分类表失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_project_categories())
