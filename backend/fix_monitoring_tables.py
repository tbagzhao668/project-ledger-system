#!/usr/bin/env python3
"""
修复监控系统数据库表字段的脚本
"""
import asyncio
import asyncpg
import os

# 数据库连接配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/project_ledger")

async def fix_monitoring_tables():
    """修复监控系统相关的数据库表字段"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # 修复健康检查表
        await conn.execute("""
            ALTER TABLE health_checks 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """)
        print("✅ 健康检查表字段修复成功")
        
        # 修复监控数据表
        await conn.execute("""
            ALTER TABLE monitoring_data 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """)
        print("✅ 监控数据表字段修复成功")
        
        # 修复系统统计表
        await conn.execute("""
            ALTER TABLE system_statistics 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """)
        print("✅ 系统统计表字段修复成功")
        
        # 修复租户活跃度表
        await conn.execute("""
            ALTER TABLE tenant_activity 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """)
        print("✅ 租户活跃度表字段修复成功")
        
        # 修复管理员操作日志表
        await conn.execute("""
            ALTER TABLE admin_operation_logs 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """)
        print("✅ 管理员操作日志表字段修复成功")
        
        print("\n🎉 所有监控系统表字段修复完成！")
        
    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_monitoring_tables())
