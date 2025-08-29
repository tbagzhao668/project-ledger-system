#!/usr/bin/env python3
"""
测试项目详情API响应
"""
import asyncio
import json
from app.core.database import get_db
from app.models.project import Project
from sqlalchemy import select

async def test_project_detail():
    async for db in get_db():
        # 获取第一个项目
        result = await db.execute(select(Project).limit(1))
        project = result.scalar_one_or_none()
        
        if project:
            print(f"项目名称: {project.name}")
            print(f"项目ID: {project.id}")
            print(f"开始时间: {project.start_date} (类型: {type(project.start_date)})")
            print(f"结束时间: {project.end_date} (类型: {type(project.end_date)})")
            
            # 模拟API响应格式
            response_data = {
                "id": str(project.id),
                "project_code": project.project_code,
                "name": project.name,
                "description": project.description,
                "project_type": project.project_type,
                "priority": project.priority,
                "status": project.status,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "planned_end_date": project.end_date.isoformat() if project.end_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "actual_end_date": project.actual_end_date.isoformat() if project.actual_end_date else None,
                "budget": float(project.budget) if project.budget else None,
                "contract_amount": float(project.contract_value) if project.contract_value else None,
                "actual_expenses": float(project.actual_cost) if project.actual_cost else None,
                "currency": "CNY",
                "location": str(project.location) if project.location else None,
                "client_name": project.client_info.get('name') if hasattr(project, 'client_info') and project.client_info else None,
                "client_contact": project.client_info.get('contact') if hasattr(project, 'client_info') and project.client_info else None,
                "client_phone": project.client_info.get('phone') if hasattr(project, 'client_info') and project.client_info else None,
                "tags": project.tags or [],
                "notes": project.description,
                "manager_id": str(project.manager_id) if project.manager_id else None,
                "manager_name": project.manager_name,
                "created_by": str(project.created_by),
                "created_by_name": "系统用户",
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None
            }
            
            print("\nAPI响应数据:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # 特别检查时间字段
            print(f"\n时间字段检查:")
            print(f"start_date: {response_data['start_date']} (类型: {type(response_data['start_date'])})")
            print(f"end_date: {response_data['end_date']} (类型: {type(response_data['end_date'])})")
            print(f"planned_end_date: {response_data['planned_end_date']} (类型: {type(response_data['planned_end_date'])})")
            
        break

if __name__ == "__main__":
    asyncio.run(test_project_detail())
