#!/usr/bin/env python3
"""
修复projects表结构的脚本
"""
import asyncio
import asyncpg
import os

async def fix_projects_schema():
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host="localhost",
            database=os.getenv("DB_NAME", "fince_project_prod"),
            user=os.getenv("DB_USER", "fince_app_project"),
            password=os.getenv("DB_PASSWORD", "Fince_project_5%8*6^9(3#0)")
        )
        
        print("开始修复projects表结构...")
        
        # 添加基础信息字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS project_code VARCHAR(50);")
            print("✅ 添加 project_code 字段")
        except Exception as e:
            print(f"⚠️ project_code 字段添加警告: {e}")
        
        # 添加项目分类字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS project_type VARCHAR(50) DEFAULT 'other';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS category VARCHAR(100);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]';")
            print("✅ 添加项目分类字段")
        except Exception as e:
            print(f"⚠️ 项目分类字段添加警告: {e}")
        
        # 添加项目状态字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS health_status VARCHAR(20) DEFAULT 'healthy';")
            print("✅ 添加项目状态字段")
        except Exception as e:
            print(f"⚠️ 项目状态字段添加警告: {e}")
        
        # 添加时间管理字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS actual_start_date DATE;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS actual_end_date DATE;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS estimated_duration INTEGER;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS actual_duration INTEGER;")
            print("✅ 添加时间管理字段")
        except Exception as e:
            print(f"⚠️ 时间管理字段添加警告: {e}")
        
        # 添加财务信息字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS actual_cost DECIMAL(15,2) DEFAULT 0;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS estimated_cost DECIMAL(15,2);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_variance DECIMAL(15,2);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS budget_utilization DECIMAL(5,2);")
            print("✅ 添加财务信息字段")
        except Exception as e:
            print(f"⚠️ 财务信息字段添加警告: {e}")
        
        # 添加人员管理字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS team_size INTEGER DEFAULT 1;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS assigned_users JSONB DEFAULT '[]';")
            print("✅ 添加人员管理字段")
        except Exception as e:
            print(f"⚠️ 人员管理字段添加警告: {e}")
        
        # 添加位置和联系信息字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS location JSONB DEFAULT '{}';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS address VARCHAR(500);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS coordinates JSONB;")
            print("✅ 添加位置和联系信息字段")
        except Exception as e:
            print(f"⚠️ 位置和联系信息字段添加警告: {e}")
        
        # 添加客户和合同信息字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS client_info JSONB DEFAULT '{}';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS contract_info JSONB DEFAULT '{}';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS contract_number VARCHAR(100);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS contract_value DECIMAL(15,2);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS payment_terms JSONB;")
            print("✅ 添加客户和合同信息字段")
        except Exception as e:
            print(f"⚠️ 客户和合同信息字段添加警告: {e}")
        
        # 添加技术规格字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS technical_specs JSONB;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS requirements JSONB;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS deliverables JSONB;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS quality_standards JSONB;")
            print("✅ 添加技术规格字段")
        except Exception as e:
            print(f"⚠️ 技术规格字段添加警告: {e}")
        
        # 添加风险管理字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20) DEFAULT 'low';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS risk_factors JSONB;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS mitigation_plans JSONB;")
            print("✅ 添加风险管理字段")
        except Exception as e:
            print(f"⚠️ 风险管理字段添加警告: {e}")
        
        # 添加变更原因相关字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS budget_change_reason VARCHAR(200);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS contract_change_reason VARCHAR(200);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS change_description TEXT;")
            print("✅ 添加变更原因相关字段")
        except Exception as e:
            print(f"⚠️ 变更原因相关字段添加警告: {e}")
        
        # 添加文档和附件字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS documents JSONB DEFAULT '[]';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS attachments JSONB DEFAULT '[]';")
            print("✅ 添加文档和附件字段")
        except Exception as e:
            print(f"⚠️ 文档和附件字段添加警告: {e}")
        
        # 添加审批和流程字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending';")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS approval_history JSONB;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS workflow_stage VARCHAR(50);")
            print("✅ 添加审批和流程字段")
        except Exception as e:
            print(f"⚠️ 审批和流程字段添加警告: {e}")
        
        # 添加监控和报告字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS last_review_date DATE;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS next_review_date DATE;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS review_cycle VARCHAR(20);")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS reporting_frequency VARCHAR(20);")
            print("✅ 添加监控和报告字段")
        except Exception as e:
            print(f"⚠️ 监控和报告字段添加警告: {e}")
        
        # 添加系统字段
        try:
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;")
            await conn.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS is_template BOOLEAN DEFAULT FALSE;")
            print("✅ 添加系统字段")
        except Exception as e:
            print(f"⚠️ 系统字段添加警告: {e}")
        
        # 添加唯一约束
        try:
            await conn.execute("ALTER TABLE projects ADD CONSTRAINT IF NOT EXISTS projects_project_code_key UNIQUE (project_code);")
            print("✅ 添加唯一约束")
        except Exception as e:
            print(f"⚠️ 唯一约束添加警告: {e}")
        
        await conn.close()
        
        print("🎉 projects表结构修复完成！")
        
    except Exception as e:
        print(f"❌ projects表结构修复失败: {e}")

if __name__ == "__main__":
    asyncio.run(fix_projects_schema())
