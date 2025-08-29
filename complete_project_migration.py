#!/usr/bin/env python3
"""
完整的项目数据库迁移脚本 - 添加所有新字段
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append('.')

async def complete_project_migration():
    try:
        from app.core.database import db_manager
        from sqlalchemy import text
        
        # 初始化数据库连接
        db_manager.initialize()
        
        async with db_manager.engine.begin() as conn:
            print("开始完整的项目数据库迁移...")
            
            # 需要添加的字段列表
            new_fields = [
                ("priority", "VARCHAR(20) DEFAULT 'medium'", "项目优先级"),
                ("category", "VARCHAR(100)", "项目分类"),
                ("tags", "JSONB DEFAULT '[]'", "项目标签"),
                ("health_status", "VARCHAR(20) DEFAULT 'healthy'", "项目健康状态"),
                ("actual_start_date", "DATE", "实际开始日期"),
                ("estimated_duration", "INTEGER", "预计工期(天)"),
                ("actual_duration", "INTEGER", "实际工期(天)"),
                ("estimated_cost", "DECIMAL(15,2)", "预估成本"),
                ("cost_variance", "DECIMAL(15,2)", "成本偏差"),
                ("budget_utilization", "DECIMAL(5,2)", "预算使用率(%)"),
                ("manager_id", "UUID", "项目经理ID"),
                ("team_size", "INTEGER DEFAULT 1", "团队规模"),
                ("assigned_users", "JSONB DEFAULT '[]'", "分配的用户ID列表"),
                ("address", "VARCHAR(500)", "项目地址"),
                ("coordinates", "JSONB", "地理坐标"),
                ("contract_number", "VARCHAR(100)", "合同编号"),
                ("contract_value", "DECIMAL(15,2)", "合同金额"),
                ("payment_terms", "JSONB", "付款条件"),
                ("technical_specs", "JSONB", "技术规格"),
                ("requirements", "JSONB", "项目需求"),
                ("deliverables", "JSONB", "交付物"),
                ("quality_standards", "JSONB", "质量标准"),
                ("risk_level", "VARCHAR(20) DEFAULT 'low'", "风险等级"),
                ("risk_factors", "JSONB", "风险因素"),
                ("mitigation_plans", "JSONB", "风险缓解计划"),
                ("documents", "JSONB DEFAULT '[]'", "相关文档"),
                ("attachments", "JSONB DEFAULT '[]'", "附件信息"),
                ("approval_status", "VARCHAR(20) DEFAULT 'pending'", "审批状态"),
                ("approval_history", "JSONB", "审批历史"),
                ("workflow_stage", "VARCHAR(50)", "工作流阶段"),
                ("last_review_date", "DATE", "最后评审日期"),
                ("next_review_date", "DATE", "下次评审日期"),
                ("review_cycle", "VARCHAR(20)", "评审周期"),
                ("reporting_frequency", "VARCHAR(20)", "报告频率"),
                ("updated_by", "UUID", "最后更新人"),
                ("is_active", "BOOLEAN DEFAULT true", "是否激活"),
                ("is_template", "BOOLEAN DEFAULT false", "是否为模板项目")
            ]
            
            # 检查并添加每个字段
            for field_name, field_type, field_comment in new_fields:
                print(f"检查字段: {field_name}")
                
                # 检查字段是否存在
                result = await conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'projects' AND column_name = '{field_name}'
                """))
                
                if not result.fetchone():
                    print(f"添加字段: {field_name} ({field_type})")
                    try:
                        await conn.execute(text(f"""
                            ALTER TABLE projects 
                            ADD COLUMN {field_name} {field_type}
                        """))
                        
                        # 添加注释
                        if field_comment:
                            await conn.execute(text(f"""
                                COMMENT ON COLUMN projects.{field_name} IS '{field_comment}'
                            """))
                        
                        print(f"✅ {field_name} 字段添加成功")
                    except Exception as e:
                        print(f"❌ {field_name} 字段添加失败: {e}")
                else:
                    print(f"✅ {field_name} 字段已存在")
            
            # 更新现有项目的默认值
            print("\n更新现有项目数据...")
            await conn.execute(text("""
                UPDATE projects 
                SET priority = 'medium' 
                WHERE priority IS NULL
            """))
            
            await conn.execute(text("""
                UPDATE projects 
                SET health_status = 'healthy' 
                WHERE health_status IS NULL
            """))
            
            await conn.execute(text("""
                UPDATE projects 
                SET risk_level = 'low' 
                WHERE risk_level IS NULL
            """))
            
            await conn.execute(text("""
                UPDATE projects 
                SET approval_status = 'pending' 
                WHERE approval_status IS NULL
            """))
            
            await conn.execute(text("""
                UPDATE projects 
                SET is_active = true 
                WHERE is_active IS NULL
            """))
            
            await conn.execute(text("""
                UPDATE projects 
                SET is_template = false 
                WHERE is_template IS NULL
            """))
            
            # 验证所有字段
            print("\n验证所有字段...")
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print(f"\n项目表总字段数: {len(columns)}")
            print("字段列表:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} (可空: {col[2]}, 默认值: {col[3]})")
            
            print("\n✅ 完整的项目数据库迁移完成！")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(complete_project_migration())
