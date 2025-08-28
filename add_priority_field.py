#!/usr/bin/env python3
"""
添加priority字段的数据库迁移脚本
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append('.')

async def add_priority_field():
    try:
        from app.core.database import db_manager
        from sqlalchemy import text
        
        # 初始化数据库连接
        db_manager.initialize()
        
        async with db_manager.engine.begin() as conn:
            print("开始添加priority字段...")
            
            # 检查priority字段是否存在
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'projects' AND column_name = 'priority'
            """))
            
            if not result.fetchone():
                print("添加 priority 字段...")
                await conn.execute(text("""
                    ALTER TABLE projects 
                    ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'
                """))
                print("✅ priority 字段添加成功")
            else:
                print("✅ priority 字段已存在")
            
            # 验证字段是否添加成功
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                AND column_name = 'priority'
            """))
            
            columns = result.fetchall()
            print("\npriority字段验证:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} (可空: {col[2]}, 默认值: {col[3]})")
            
            # 更新现有项目的默认值
            print("\n更新现有项目数据...")
            await conn.execute(text("""
                UPDATE projects 
                SET priority = 'medium' 
                WHERE priority IS NULL
            """))
            
            print("✅ 数据库迁移完成！")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_priority_field())
