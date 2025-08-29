#!/usr/bin/env python3
"""
创建基础数据库表的脚本
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从环境变量获取数据库配置
from app.config import settings

def create_basic_tables():
    """创建基础表结构"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "fince_project_prod"),
            user=os.getenv("DB_USER", "fince_app_project"),
            password=os.getenv("DB_PASSWORD", "Fince_project_5%8*6^9(3#0)")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("开始创建基础表...")
        
        # 创建租户表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                domain VARCHAR(100) UNIQUE,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 租户表创建成功")
        
        # 创建用户表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                permissions TEXT[],
                profile JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                two_factor_enabled BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                tenant_id UUID REFERENCES tenants(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 用户表创建成功")
        
        # 创建项目表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'active',
                priority VARCHAR(20) DEFAULT 'medium',
                start_date DATE,
                end_date DATE,
                budget DECIMAL(15,2),
                contract_amount DECIMAL(15,2),
                manager_id UUID REFERENCES users(id),
                manager_name VARCHAR(100),
                tenant_id UUID REFERENCES tenants(id),
                created_by UUID REFERENCES users(id),
                updated_by UUID REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 项目表创建成功")
        
        # 创建分类表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT,
                type VARCHAR(50),
                parent_id UUID REFERENCES categories(id),
                tenant_id UUID REFERENCES tenants(id),
                created_by UUID REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 分类表创建成功")
        
        # 创建交易记录表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                amount DECIMAL(15,2) NOT NULL,
                type VARCHAR(20) NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                category_id UUID REFERENCES categories(id),
                project_id UUID REFERENCES projects(id),
                supplier_id UUID,
                tenant_id UUID REFERENCES tenants(id),
                created_by UUID REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 交易记录表创建成功")
        
        # 创建默认租户
        cur.execute("""
            INSERT INTO tenants (name, domain, status) 
            VALUES ('默认租户', 'default', 'active')
            ON CONFLICT (domain) DO NOTHING
        """)
        
        # 获取默认租户ID
        cur.execute("SELECT id FROM tenants WHERE domain = 'default'")
        tenant_id = cur.fetchone()[0]
        
        # 创建默认管理员用户
        from app.core.auth import AuthManager
        auth_manager = AuthManager()
        admin_password_hash = auth_manager.get_password_hash("admin123")
        
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, is_active, tenant_id) 
            VALUES ('admin', 'admin@example.com', %s, 'admin', TRUE, %s)
            ON CONFLICT (email) DO NOTHING
        """, (admin_password_hash, tenant_id))
        
        print("✅ 默认租户和管理员用户创建成功")
        
        cur.close()
        conn.close()
        
        print("🎉 所有基础表创建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False

if __name__ == "__main__":
    create_basic_tables()
