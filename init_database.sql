-- 工程项目流水账管理系统 - 数据库初始化脚本
-- 创建时间: 2025年8月29日
-- 版本: 1.0.0

-- 创建数据库用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'fince_app_project') THEN
        CREATE USER fince_app_project WITH PASSWORD 'postgres';
    END IF;
END
$$;

-- 创建数据库（如果不存在）
SELECT 'CREATE DATABASE fince_project_prod OWNER fince_app_project'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fince_project_prod')\gexec

-- 连接到新创建的数据库
\c fince_project_prod;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建tenants表
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(50) UNIQUE,
    plan_type VARCHAR(20) DEFAULT 'trial',
    settings JSONB DEFAULT '{}',
    subscription_end DATE,
    storage_used BIGINT DEFAULT 0,
    storage_limit BIGINT DEFAULT 5368709120,
    api_calls_used INTEGER DEFAULT 0,
    api_calls_limit INTEGER DEFAULT 1000,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建users表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    permissions JSONB DEFAULT '[]',
    profile JSONB DEFAULT '{}',
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建projects表
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(200) NOT NULL,
    project_code VARCHAR(50) UNIQUE,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'other',
    category VARCHAR(100),
    tags JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'planning',
    priority VARCHAR(20) DEFAULT 'medium',
    progress INTEGER DEFAULT 0,
    health_status VARCHAR(20) DEFAULT 'healthy',
    start_date DATE,
    end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    estimated_duration INTEGER,
    actual_duration INTEGER,
    budget DECIMAL(15,2),
    actual_cost DECIMAL(15,2) DEFAULT 0,
    estimated_cost DECIMAL(15,2),
    cost_variance DECIMAL(15,2),
    budget_utilization DECIMAL(5,2),
    manager_name VARCHAR(100),
    manager_id UUID REFERENCES users(id),
    team_size INTEGER DEFAULT 1,
    assigned_users JSONB DEFAULT '[]',
    location JSONB DEFAULT '{}',
    address VARCHAR(500),
    coordinates JSONB,
    client_info JSONB DEFAULT '{}',
    contract_info JSONB DEFAULT '{}',
    contract_number VARCHAR(100),
    contract_value DECIMAL(15,2),
    payment_terms JSONB,
    technical_specs JSONB,
    requirements JSONB,
    deliverables JSONB,
    quality_standards JSONB,
    risk_level VARCHAR(20) DEFAULT 'low',
    risk_factors JSONB,
    mitigation_plans JSONB,
    budget_change_reason VARCHAR(200),
    contract_change_reason VARCHAR(200),
    change_description TEXT,
    documents JSONB DEFAULT '[]',
    attachments JSONB DEFAULT '[]',
    approval_status VARCHAR(20) DEFAULT 'pending',
    approval_history JSONB,
    workflow_stage VARCHAR(50),
    last_review_date DATE,
    next_review_date DATE,
    review_cycle VARCHAR(20),
    reporting_frequency VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_template BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建categories表
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    icon VARCHAR(50),
    color VARCHAR(7),
    is_system VARCHAR(1) DEFAULT '0',
    is_active VARCHAR(1) DEFAULT '1',
    sort_order VARCHAR(10) DEFAULT '0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建suppliers表
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50),
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    business_scope TEXT,
    qualification TEXT,
    credit_rating VARCHAR(10),
    payment_terms VARCHAR(200),
    is_active VARCHAR(1) DEFAULT '1',
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建transactions表
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    project_id UUID REFERENCES projects(id),
    supplier_id UUID REFERENCES suppliers(id),
    category_id UUID REFERENCES categories(id),
    transaction_date DATE NOT NULL,
    type VARCHAR(10) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',
    exchange_rate DECIMAL(10,6) DEFAULT 1.000000,
    description TEXT,
    notes TEXT,
    tags JSONB,
    payment_method VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    attachment_url VARCHAR(500),
    reference_number VARCHAR(100),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_transactions_tenant_id ON transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_project_id ON transactions(project_id);
CREATE INDEX IF NOT EXISTS idx_categories_tenant_id ON categories(tenant_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_tenant_id ON suppliers(tenant_id);

-- 插入初始数据
INSERT INTO tenants (name, domain, plan_type, status) 
VALUES ('默认租户', 'default.local', 'trial', 'active')
ON CONFLICT (domain) DO NOTHING;

-- 设置权限
GRANT ALL PRIVILEGES ON DATABASE fince_project_prod TO fince_app_project;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fince_app_project;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fince_app_project;

-- 显示创建结果
SELECT '数据库初始化完成' as status;
SELECT COUNT(*) as tables_count FROM information_schema.tables WHERE table_schema = 'public';
