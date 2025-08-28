#!/usr/bin/env python3
"""
创建项目相关表的数据库迁移脚本
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db_manager
from app.models.project import ProjectMilestone, ProjectTeamMember, ProjectChangeLog
from app.models.base import Base

async def create_project_tables():
    """创建项目相关的数据库表"""
    try:
        print("开始创建项目相关表...")
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 创建表
        async with db_manager.get_session() as session:
            # 创建项目里程碑表
            print("创建项目里程碑表...")
            await session.execute(
                """
                CREATE TABLE IF NOT EXISTS project_milestones (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    target_date DATE,
                    actual_date DATE,
                    status VARCHAR(20) DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    dependencies JSONB DEFAULT '[]',
                    deliverables JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                """
            )
            
            # 创建项目团队成员表
            print("创建项目团队成员表...")
            await session.execute(
                """
                CREATE TABLE IF NOT EXISTS project_team_members (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(100),
                    role_name VARCHAR(100),
                    join_date DATE,
                    leave_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    permissions JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                """
            )
            
            # 创建项目变更记录表
            print("创建项目变更记录表...")
            await session.execute(
                """
                CREATE TABLE IF NOT EXISTS project_change_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    change_type VARCHAR(50) NOT NULL,
                    field_name VARCHAR(100),
                    old_value TEXT,
                    new_value TEXT,
                    change_description TEXT,
                    change_reason TEXT,
                    changed_by UUID REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                """
            )
            
            # 创建索引
            print("创建索引...")
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_milestones_project_id ON project_milestones(project_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_milestones_tenant_id ON project_milestones(tenant_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_team_members_project_id ON project_team_members(project_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_team_members_user_id ON project_team_members(user_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_team_members_tenant_id ON project_team_members(tenant_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_change_logs_project_id ON project_change_logs(project_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_change_logs_tenant_id ON project_change_logs(tenant_id)"
            )
            await session.execute(
                "CREATE INDEX IF NOT EXISTS idx_project_change_logs_created_at ON project_change_logs(created_at)"
            )
            
            await session.commit()
            print("✅ 项目相关表创建成功！")
            
    except Exception as e:
        print(f"❌ 创建表失败: {str(e)}")
        raise

async def main():
    """主函数"""
    try:
        await create_project_tables()
        print("数据库迁移完成！")
    except Exception as e:
        print(f"数据库迁移失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
