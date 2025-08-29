#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建监控系统所需的数据库表
"""

import asyncio
import asyncpg
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def create_monitoring_tables():
    """创建监控系统所需的表"""
    
    # 数据库连接配置
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'fince_project_prod',
        'user': 'fince_app_project',
        'password': 'Fince_project_5%8*6^9(3#0)'
    }
    
    try:
        # 连接数据库
        print("🔌 连接数据库...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        
        # 创建监控数据表
        print("📊 创建监控数据表...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID REFERENCES tenants(id),
                service_name VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                response_time INTEGER,
                error_message TEXT,
                extra_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✅ 监控数据表创建成功")
        
        # 创建管理员操作日志表
        print("📝 创建管理员操作日志表...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_operation_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                admin_user_id UUID NOT NULL REFERENCES users(id),
                operation_type VARCHAR(50) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id UUID,
                operation_details JSONB,
                ip_address INET,
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✅ 管理员操作日志表创建成功")
        
        # 创建系统统计表
        print("📈 创建系统统计表...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_statistics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID REFERENCES tenants(id),
                stat_date DATE NOT NULL,
                stat_type VARCHAR(50) NOT NULL,
                stat_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✅ 系统统计表创建成功")
        
        # 创建租户活跃度表
        print("🏃 创建租户活跃度表...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tenant_activity (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID NOT NULL REFERENCES tenants(id),
                activity_date DATE NOT NULL,
                login_count INTEGER DEFAULT 0,
                project_operations INTEGER DEFAULT 0,
                transaction_operations INTEGER DEFAULT 0,
                supplier_operations INTEGER DEFAULT 0,
                last_activity_at TIMESTAMP WITH TIME ZONE,
                activity_score INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✅ 租户活跃度表创建成功")
        
        # 创建健康检查记录表
        print("💚 创建健康检查记录表...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                service_name VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                response_time INTEGER,
                error_details TEXT,
                check_details JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✅ 健康检查记录表创建成功")
        
        # 创建索引
        print("🔍 创建索引...")
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_data_tenant_id ON monitoring_data(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_monitoring_data_service_name ON monitoring_data(service_name);
            CREATE INDEX IF NOT EXISTS idx_admin_operation_logs_admin_user_id ON admin_operation_logs(admin_user_id);
            CREATE INDEX IF NOT EXISTS idx_admin_operation_logs_operation_type ON admin_operation_logs(operation_type);
            CREATE INDEX IF NOT EXISTS idx_admin_operation_logs_target_type ON admin_operation_logs(target_type);
            CREATE INDEX IF NOT EXISTS idx_system_statistics_tenant_id ON system_statistics(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_system_statistics_date ON system_statistics(stat_date);
            CREATE INDEX IF NOT EXISTS idx_tenant_activity_tenant_id ON tenant_activity(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_tenant_activity_date ON tenant_activity(activity_date);
            CREATE INDEX IF NOT EXISTS idx_health_checks_service_name ON health_checks(service_name);
        """)
        print("✅ 索引创建成功")
        
        # 验证表是否创建成功
        print("🔍 验证表创建结果...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'monitoring_data', 
                'admin_operation_logs', 
                'system_statistics', 
                'tenant_activity', 
                'health_checks'
            )
            ORDER BY table_name;
        """)
        
        print(f"📋 成功创建的表:")
        for table in tables:
            print(f"   ✅ {table['table_name']}")
        
        print(f"\n🎉 监控系统表创建完成！共创建了 {len(tables)} 个表")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 创建监控表失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 开始创建监控系统数据库表...")
    asyncio.run(create_monitoring_tables())
