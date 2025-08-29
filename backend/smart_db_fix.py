#!/usr/bin/env python3
"""
智能数据库表结构修复脚本
基于项目代码中的模型定义自动修复数据库
基于实际修复经验优化，确保关键字段如contract_value正确添加
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

async def smart_fix_database():
    """智能修复数据库表结构"""
    try:
        # 连接数据库
        print("🔌 正在连接数据库...")
        conn = await asyncpg.connect(
            host="localhost",
            database=os.getenv("DB_NAME", "fince_project_prod"),
            user=os.getenv("DB_USER", "fince_app_project"),
            password=os.getenv("DB_PASSWORD", "Fince_project_5%8*6*9(3#0)")
        )
        print("✅ 数据库连接成功")
        
        print("🔍 开始智能检测和修复数据库表结构...")
        
        # 1. 修复tenants表 - 基于Tenant模型
        print("📋 修复tenants表...")
        tenant_fields = [
            ("name", "VARCHAR(100) NOT NULL", "企业名称"),
            ("domain", "VARCHAR(50) UNIQUE", "租户域名"),
            ("plan_type", "VARCHAR(20) DEFAULT 'trial'", "订阅计划类型"),
            ("settings", "JSONB DEFAULT '{}'", "租户设置"),
            ("subscription_end", "DATE", "订阅到期日期"),
            ("storage_used", "BIGINT DEFAULT 0", "已使用存储空间"),
            ("storage_limit", "BIGINT DEFAULT 5368709120", "存储空间限制"),
            ("api_calls_used", "INTEGER DEFAULT 0", "已使用API调用次数"),
            ("api_calls_limit", "INTEGER DEFAULT 1000", "API调用次数限制"),
            ("status", "VARCHAR(20) DEFAULT 'active'", "租户状态")
        ]
        
        for field_name, field_def, comment in tenant_fields:
            try:
                await conn.execute(f"ALTER TABLE tenants ADD COLUMN IF NOT EXISTS {field_name} {field_def};")
                print(f"  ✅ 添加字段: {field_name} - {comment}")
            except Exception as e:
                print(f"  ⚠️ 字段 {field_name} 已存在或添加失败: {e}")
        
        # 2. 修复users表 - 基于User模型
        print("👥 修复users表...")
        user_fields = [
            ("tenant_id", "UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL", "租户ID"),
            ("username", "VARCHAR(50) NOT NULL", "用户名"),
            ("email", "VARCHAR(100) NOT NULL", "邮箱"),
            ("password_hash", "VARCHAR(255) NOT NULL", "密码哈希"),
            ("role", "VARCHAR(20) DEFAULT 'user'", "用户角色"),
            ("permissions", "JSONB DEFAULT '[]'", "用户权限"),
            ("profile", "JSONB DEFAULT '{}'", "用户资料"),
            ("last_login", "TIMESTAMP", "最后登录时间"),
            ("login_count", "INTEGER DEFAULT 0", "登录次数"),
            ("is_active", "BOOLEAN DEFAULT TRUE", "是否激活"),
            ("email_verified", "BOOLEAN DEFAULT FALSE", "邮箱是否验证"),
            ("two_factor_enabled", "BOOLEAN DEFAULT FALSE", "是否启用两步验证")
        ]
        
        for field_name, field_def, comment in user_fields:
            try:
                await conn.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {field_name} {field_def};")
                print(f"  ✅ 添加字段: {field_name} - {comment}")
            except Exception as e:
                print(f"  ⚠️ 字段 {field_name} 已存在或添加失败: {e}")
        
        # 3. 修复projects表 - 基于Project模型
        print("🏗️ 修复projects表...")
        print("   特别注意：确保contract_value字段正确添加，这是前端API的关键字段")
        project_fields = [
            ("tenant_id", "UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL", "租户ID"),
            ("name", "VARCHAR(200) NOT NULL", "项目名称"),
            ("project_code", "VARCHAR(50) UNIQUE", "项目编号"),
            ("description", "TEXT", "项目描述"),
            ("project_type", "VARCHAR(50) DEFAULT 'other'", "项目类型"),
            ("category", "VARCHAR(100)", "项目分类"),
            ("tags", "JSONB DEFAULT '[]'", "项目标签"),
            ("status", "VARCHAR(20) DEFAULT 'planning'", "项目状态"),
            ("priority", "VARCHAR(20) DEFAULT 'medium'", "项目优先级"),
            ("progress", "INTEGER DEFAULT 0", "项目进度"),
            ("health_status", "VARCHAR(20) DEFAULT 'healthy'", "项目健康状态"),
            ("start_date", "DATE", "计划开始日期"),
            ("end_date", "DATE", "计划结束日期"),
            ("actual_start_date", "DATE", "实际开始日期"),
            ("actual_end_date", "DATE", "实际结束日期"),
            ("estimated_duration", "INTEGER", "预计工期"),
            ("actual_duration", "INTEGER", "实际工期"),
            ("budget", "DECIMAL(15,2)", "项目预算"),
            ("actual_cost", "DECIMAL(15,2) DEFAULT 0", "实际成本"),
            ("estimated_cost", "DECIMAL(15,2)", "预估成本"),
            ("cost_variance", "DECIMAL(15,2)", "成本偏差"),
            ("budget_utilization", "DECIMAL(5,2)", "预算使用率"),
            ("manager_name", "VARCHAR(100)", "项目经理姓名"),
            ("manager_id", "UUID REFERENCES users(id)", "项目经理ID"),
            ("team_size", "INTEGER DEFAULT 1", "团队规模"),
            ("assigned_users", "JSONB DEFAULT '[]'", "分配的用户ID列表"),
            ("location", "JSONB DEFAULT '{}'", "项目位置信息"),
            ("address", "VARCHAR(500)", "项目地址"),
            ("coordinates", "JSONB", "地理坐标"),
            ("client_info", "JSONB DEFAULT '{}'", "客户信息"),
            ("contract_info", "JSONB DEFAULT '{}'", "合同信息"),
            ("contract_number", "VARCHAR(100)", "合同编号"),
            ("contract_value", "DECIMAL(15,2)", "合同金额 - 关键字段！"),
            ("payment_terms", "JSONB", "付款条件"),
            ("technical_specs", "JSONB", "技术规格"),
            ("requirements", "JSONB", "项目需求"),
            ("deliverables", "JSONB", "交付物"),
            ("quality_standards", "JSONB", "质量标准"),
            ("risk_level", "VARCHAR(20) DEFAULT 'low'", "风险等级"),
            ("risk_factors", "JSONB", "风险因素"),
            ("mitigation_plans", "JSONB", "风险缓解计划"),
            ("budget_change_reason", "VARCHAR(200)", "预算变更原因"),
            ("contract_change_reason", "VARCHAR(200)", "合同变更原因"),
            ("change_description", "TEXT", "变更详细说明"),
            ("documents", "JSONB DEFAULT '[]'", "文档和附件"),
            ("attachments", "JSONB DEFAULT '[]'", "附件列表"),
            ("approval_status", "VARCHAR(20) DEFAULT 'pending'", "审批状态"),
            ("approval_history", "JSONB", "审批历史"),
            ("workflow_stage", "VARCHAR(50)", "工作流阶段"),
            ("last_review_date", "DATE", "最后审查日期"),
            ("next_review_date", "DATE", "下次审查日期"),
            ("review_cycle", "VARCHAR(20)", "审查周期"),
            ("reporting_frequency", "VARCHAR(20)", "报告频率"),
            ("is_active", "BOOLEAN DEFAULT TRUE", "是否激活"),
            ("is_template", "BOOLEAN DEFAULT FALSE", "是否模板"),
            ("created_by", "UUID REFERENCES users(id)", "创建人"),
            ("updated_by", "UUID REFERENCES users(id)", "更新人")
        ]
        
        for field_name, field_def, comment in project_fields:
            try:
                await conn.execute(f"ALTER TABLE projects ADD COLUMN IF NOT EXISTS {field_name} {field_def};")
                print(f"  ✅ 添加字段: {field_name} - {comment}")
                
                # 特别验证关键字段
                if field_name == "contract_value":
                    print(f"    🔍 验证关键字段 {field_name} 是否成功添加...")
                    result = await conn.fetchval("SELECT column_name FROM information_schema.columns WHERE table_name = 'projects' AND column_name = $1;", field_name)
                    if result:
                        print(f"    ✅ 关键字段 {field_name} 验证成功")
                    else:
                        print(f"    ❌ 关键字段 {field_name} 验证失败，尝试重新添加...")
                        await conn.execute(f"ALTER TABLE projects ADD COLUMN {field_name} {field_def};")
                        print(f"    ✅ 关键字段 {field_name} 重新添加成功")
                        
            except Exception as e:
                print(f"  ⚠️ 字段 {field_name} 已存在或添加失败: {e}")
                # 对于关键字段，尝试强制添加
                if field_name == "contract_value":
                    print(f"    🔧 尝试强制添加关键字段 {field_name}...")
                    try:
                        await conn.execute(f"ALTER TABLE projects ADD COLUMN {field_name} {field_def};")
                        print(f"    ✅ 关键字段 {field_name} 强制添加成功")
                    except Exception as e2:
                        print(f"    ❌ 关键字段 {field_name} 强制添加失败: {e2}")
        
        # 4. 修复categories表 - 基于Category模型
        print("🏷️ 修复categories表...")
        category_fields = [
            ("tenant_id", "UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL", "租户ID"),
            ("name", "VARCHAR(100) NOT NULL", "分类名称"),
            ("parent_id", "UUID REFERENCES categories(id)", "父分类ID"),
            ("icon", "VARCHAR(50)", "图标"),
            ("color", "VARCHAR(7)", "颜色"),
            ("is_system", "VARCHAR(1) DEFAULT '0'", "是否系统预设分类"),
            ("is_active", "VARCHAR(1) DEFAULT '1'", "是否激活"),
            ("sort_order", "VARCHAR(10) DEFAULT '0'", "排序")
        ]
        
        for field_name, field_def, comment in category_fields:
            try:
                await conn.execute(f"ALTER TABLE categories ADD COLUMN IF NOT EXISTS {field_name} {field_def};")
                print(f"  ✅ 添加字段: {field_name} - {comment}")
            except Exception as e:
                print(f"  ⚠️ 字段 {field_name} 已存在或添加失败: {e}")
        
        # 5. 修复transactions表 - 基于Transaction模型
        print("💰 修复transactions表...")
        transaction_fields = [
            ("tenant_id", "UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL", "租户ID"),
            ("project_id", "UUID REFERENCES projects(id)", "关联项目ID"),
            ("supplier_id", "UUID REFERENCES suppliers(id)", "关联供应商ID"),
            ("category_id", "UUID REFERENCES categories(id)", "分类ID"),
            ("transaction_date", "DATE NOT NULL", "交易日期"),
            ("type", "VARCHAR(10) NOT NULL", "交易类型"),
            ("amount", "DECIMAL(15,2) NOT NULL", "交易金额"),
            ("currency", "VARCHAR(10) DEFAULT 'CNY'", "货币类型"),
            ("exchange_rate", "DECIMAL(10,6) DEFAULT 1.000000", "汇率"),
            ("description", "TEXT", "交易描述"),
            ("notes", "TEXT", "备注"),
            ("tags", "JSONB", "标签"),
            ("payment_method", "VARCHAR(50)", "支付方式"),
            ("status", "VARCHAR(20) DEFAULT 'pending'", "交易状态"),
            ("attachment_url", "VARCHAR(500)", "附件链接"),
            ("reference_number", "VARCHAR(100)", "参考编号"),
            ("approved_by", "VARCHAR(100)", "审批人"),
            ("approved_at", "TIMESTAMP", "审批时间"),
            ("created_by", "UUID REFERENCES users(id)", "创建人")
        ]
        
        for field_name, field_def, comment in transaction_fields:
            try:
                await conn.execute(f"ALTER TABLE transactions ADD COLUMN IF NOT EXISTS {field_name} {field_def};")
                print(f"  ✅ 添加字段: {field_name} - {comment}")
            except Exception as e:
                print(f"  ⚠️ 字段 {field_name} 已存在或添加失败: {e}")
        
        # 6. 创建suppliers表 - 基于Supplier模型
        print("🏢 创建suppliers表...")
        try:
            await conn.execute("""
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
                )
            """)
            print("  ✅ suppliers表创建/修复完成")
        except Exception as e:
            print(f"  ⚠️ suppliers表创建警告: {e}")
        
        # 7. 创建project_change_logs表
        print("📝 创建project_change_logs表...")
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS project_change_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
                    project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
                    change_type VARCHAR(50) NOT NULL,
                    field_name VARCHAR(100),
                    old_value TEXT,
                    new_value TEXT,
                    change_description TEXT,
                    change_reason TEXT,
                    changed_by UUID REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("  ✅ project_change_logs表创建/修复完成")
        except Exception as e:
            print(f"  ⚠️ project_change_logs表创建警告: {e}")
        
        # 8. 添加必要的外键约束
        print("🔗 添加外键约束...")
        constraints = [
            ("transactions_category_id_fkey", "transactions", "category_id", "categories", "id"),
            ("transactions_project_id_fkey", "transactions", "project_id", "projects", "id"),
            ("transactions_supplier_id_fkey", "transactions", "supplier_id", "suppliers", "id"),
            ("projects_tenant_id_fkey", "projects", "tenant_id", "tenants", "id"),
            ("users_tenant_id_fkey", "users", "tenant_id", "tenants", "id"),
            ("categories_tenant_id_fkey", "categories", "tenant_id", "tenants", "id")
        ]
        
        for constraint_name, table_name, column_name, ref_table, ref_column in constraints:
            try:
                # 检查约束是否已存在
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_name = $1 AND table_name = $2;",
                    constraint_name, table_name
                )
                if result == 0:
                    await conn.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref_column});")
                    print(f"  ✅ 添加外键约束: {constraint_name}")
                else:
                    print(f"  ✅ 外键约束已存在: {constraint_name}")
            except Exception as e:
                print(f"  ⚠️ 外键约束添加警告: {e}")
        
        # 9. 创建必要的索引
        print("📊 创建索引...")
        indexes = [
            ("idx_users_tenant_email", "users", "tenant_id, email"),
            ("idx_projects_tenant_code", "projects", "tenant_id, project_code"),
            ("idx_transactions_tenant_date", "transactions", "tenant_id, transaction_date"),
            ("idx_categories_tenant_name", "categories", "tenant_id, name")
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                # 检查索引是否已存在
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM pg_indexes WHERE indexname = $1;",
                    index_name
                )
                if result == 0:
                    await conn.execute(f"CREATE INDEX {index_name} ON {table_name} ({columns});")
                    print(f"  ✅ 创建索引: {index_name}")
                else:
                    print(f"  ✅ 索引已存在: {index_name}")
            except Exception as e:
                print(f"  ⚠️ 索引创建警告: {e}")
        
        print("🎉 数据库表结构智能修复完成！")
        
        # 验证关键表是否存在
        tables_to_check = ["tenants", "users", "projects", "categories", "transactions", "suppliers"]
        for table in tables_to_check:
            try:
                result = await conn.fetchval(f"SELECT COUNT(*) FROM {table};")
                print(f"✅ {table}表验证通过，记录数: {result}")
            except Exception as e:
                print(f"❌ {table}表验证失败: {e}")
        
        # 特别验证projects表的关键字段
        print("🔍 验证projects表关键字段...")
        critical_fields = ["contract_value", "budget", "project_code", "tenant_id"]
        for field in critical_fields:
            try:
                result = await conn.fetchval("SELECT column_name FROM information_schema.columns WHERE table_name = 'projects' AND column_name = $1;", field)
                if result:
                    print(f"  ✅ 关键字段 {field} 存在")
                else:
                    print(f"  ❌ 关键字段 {field} 缺失！")
            except Exception as e:
                print(f"  ❌ 验证字段 {field} 时出错: {e}")
        
        # 验证projects表结构完整性
        try:
            column_count = await conn.fetchval("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'projects';")
            print(f"📊 projects表总字段数: {column_count}")
            if column_count < 50:
                print("  ⚠️ projects表字段数较少，可能缺少重要字段")
            else:
                print("  ✅ projects表字段数量正常")
        except Exception as e:
            print(f"  ❌ 无法统计projects表字段数: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")
        print("💡 常见解决方案:")
        print("   1. 检查数据库连接参数是否正确")
        print("   2. 确保PostgreSQL服务正在运行")
        print("   3. 检查数据库用户权限")
        print("   4. 手动运行: python3 fix_projects_schema.py")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(smart_fix_database())
