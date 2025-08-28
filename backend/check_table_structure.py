#!/usr/bin/env python3
"""
检查数据库表结构的脚本
"""
import asyncio
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

async def check_table_structure():
    """检查数据库表结构"""
    # 数据库连接配置
    DATABASE_URL = "postgresql://postgres:123456@localhost:5432/project_ledger"
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 检查projects表结构
        print("=== 检查projects表结构 ===")
        result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'projects' 
            ORDER BY ordinal_position
        """)
        
        for row in result:
            print(f"{row['column_name']:<25} {row['data_type']:<20} {'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL':<10} {row['column_default'] or '':<20} {row['character_maximum_length'] or '':<10}")
        
        print("\n=== 检查projects表索引 ===")
        index_result = await conn.fetch("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'projects'
        """)
        
        for row in index_result:
            print(f"{row['indexname']}: {row['indexdef']}")
        
        # 检查表数据
        print("\n=== 检查projects表数据 ===")
        count_result = await conn.fetch("SELECT COUNT(*) as count FROM projects")
        print(f"项目总数: {count_result[0]['count']}")
        
        if count_result[0]['count'] > 0:
            sample_result = await conn.fetch("SELECT id, name, project_code, status, manager_name FROM projects LIMIT 5")
            print("\n示例项目:")
            for row in sample_result:
                print(f"ID: {row['id']}, 名称: {row['name']}, 编号: {row['project_code']}, 状态: {row['status']}, 经理: {row['manager_name']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"检查数据库结构时出错: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure())
