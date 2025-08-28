#!/usr/bin/env python3
"""
创建监控系统数据库表的脚本
"""
import asyncio
import asyncpg
from datetime import datetime
import os

# 数据库连接配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/project_ledger")

async def create_monitoring_tables():
    """创建监控系统相关的数据库表"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # 创建监控数据表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
                service_name VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                response_time INTEGER,
                error_message TEXT,
                extra_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ 监控数据表创建成功")
        
        # 创建管理员操作日志表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_operation_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                admin_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                operation_type VARCHAR(50) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id UUID,
                operation_details JSONB,
                ip_address INET,
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ 管理员操作日志表创建成功")
        
        # 创建系统统计表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_statistics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
                stat_date DATE NOT NULL,
                stat_type VARCHAR(50) NOT NULL,
                stat_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(tenant_id, stat_date, stat_type)
            )
        """)
        print("✅ 系统统计表创建成功")
        
        # 创建租户活跃度表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tenant_activity (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
                activity_date DATE NOT NULL,
                login_count INTEGER DEFAULT 0,
                project_operations INTEGER DEFAULT 0,
                transaction_operations INTEGER DEFAULT 0,
                supplier_operations INTEGER DEFAULT 0,
                last_activity_at TIMESTAMP WITH TIME ZONE,
                activity_score INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(tenant_id, activity_date)
            )
        """)
        print("✅ 租户活跃度表创建成功")
        
        # 创建健康检查记录表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                service_name VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                response_time INTEGER,
                error_details TEXT,
                check_details JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ 健康检查记录表创建成功")
        
        # 创建索引
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_data_tenant ON monitoring_data(tenant_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_data_service ON monitoring_data(service_name)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_data_created ON monitoring_data(created_at)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_operation_logs(admin_user_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_logs_type ON admin_operation_logs(operation_type)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_logs_created ON admin_operation_logs(created_at)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_stats_tenant ON system_statistics(tenant_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_stats_date ON system_statistics(stat_date)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tenant_activity_tenant ON tenant_activity(tenant_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tenant_activity_date ON tenant_activity(activity_date)
        """)
        
        print("✅ 所有索引创建成功")
        
        # 插入一些初始数据
        await conn.execute("""
            INSERT INTO health_checks (service_name, status, response_time, check_details)
            VALUES 
                ('database', 'healthy', 15, '{"connection_pool": "active", "active_connections": 5}'),
                ('api_service', 'healthy', 5, '{"uptime": "0h 0m", "memory_usage": "0%"}')
            ON CONFLICT DO NOTHING
        """)
        print("✅ 初始健康检查数据插入成功")
        
        print("\n🎉 所有监控系统表创建完成！")
        
    except Exception as e:
        print(f"❌ 创建表时出错: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_monitoring_tables())
