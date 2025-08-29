#!/usr/bin/env python3
"""在服务器上创建正确的projects.py文件"""

import subprocess
import sys

# 文件内容
content = '''"""项目管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
import uuid

from ...core.auth import get_current_user, require_permissions
from ...core.database import get_db
from ...models.user import User
from ...models.project import Project, ProjectChangeLog
from ...models.transaction import Transaction
from ...schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectStatistics, ProjectQueryParams, ProjectStatusEnum, ProjectTypeEnum,
    ProjectPriorityEnum, ProjectChangeLogResponse
)

router = APIRouter(prefix="/projects")

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ProjectStatusEnum] = None,
    type: Optional[ProjectTypeEnum] = None,
    priority: Optional[ProjectPriorityEnum] = None,
    search: Optional[str] = None
):
    """获取项目列表"""
    try:
        # 构建查询条件
        query = select(Project).options(selectinload(Project.manager))
        
        # 添加过滤条件
        if status:
            query = query.where(Project.status == status)
        if type:
            query = query.where(Project.type == type)
        if priority:
            query = query.where(Project.priority == priority)
        if search:
            search_filter = or_(
                Project.name.contains(search),
                Project.description.contains(search),
                Project.code.contains(search)
            )
            query = query.where(search_filter)
        
        # 添加分页和排序
        query = query.offset(skip).limit(limit).order_by(desc(Project.created_at))
        
        result = await db.execute(query)
        projects = result.scalars().unique().all()
        
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目列表失败: {str(e)}"
        )

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新项目"""
    try:
        # 检查项目代码是否已存在
        existing_project = await db.execute(
            select(Project).where(Project.code == project_data.code)
        )
        if existing_project.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目代码已存在"
            )
        
        # 创建新项目
        new_project = Project(
            **project_data.dict(),
            created_by=current_user.id,
            created_at=datetime.utcnow()
        )
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        return new_project
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建项目失败: {str(e)}"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目详情"""
    try:
        project = await db.execute(
            select(Project).options(selectinload(Project.manager)).where(Project.id == project_id)
        )
        project = project.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目详情失败: {str(e)}"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目信息"""
    try:
        project = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 更新项目信息
        for field, value in project_data.dict(exclude_unset=True).items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        project.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(project)
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新项目失败: {str(e)}"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目"""
    try:
        project = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查项目是否可以删除（例如没有关联的交易记录）
        transactions = await db.execute(
            select(Transaction).where(Transaction.project_id == project_id)
        )
        if transactions.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目存在关联的交易记录，无法删除"
            )
        
        await db.delete(project)
        await db.commit()
        
        return {"message": "项目删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除项目失败: {str(e)}"
        )

@router.get("/statistics/overview")
async def get_project_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目统计概览"""
    try:
        # 获取项目总数
        total_projects = await db.execute(select(func.count(Project.id)))
        total_count = total_projects.scalar()
        
        # 获取各状态的项目数量
        status_stats = await db.execute(
            select(Project.status, func.count(Project.id))
            .group_by(Project.status)
        )
        status_counts = dict(status_stats.fetchall())
        
        # 获取各类型的项目数量
        type_stats = await db.execute(
            select(Project.project_type, func.count(Project.id))
            .group_by(Project.project_type)
        )
        type_counts = dict(type_stats.fetchall())
        
        # 获取各优先级的项目数量
        priority_stats = await db.execute(
            select(Project.priority, func.count(Project.id))
            .group_by(Project.priority)
        )
        priority_counts = dict(priority_stats.fetchall())
        
        # 计算总预算和实际成本
        budget_stats = await db.execute(
            select(
                func.sum(Project.budget).label("total_budget"),
                func.sum(Project.actual_cost).label("total_actual_cost")
            )
        )
        budget_result = budget_stats.fetchone()
        total_budget = float(budget_result[0]) if budget_result[0] else 0
        total_actual_cost = float(budget_result[1]) if budget_result[1] else 0
        
        return {
            "total_projects": total_count,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "priority_distribution": priority_counts,
            "budget_summary": {
                "total_budget": total_budget,
                "total_actual_cost": total_actual_cost,
                "cost_variance": total_budget - total_actual_cost
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目统计失败: {str(e)}"
        )
'''

# 使用plink命令在服务器上创建文件
cmd = f'plink -batch -ssh -pw 123 dev@192.168.1.215 "cd /home/dev/project/app/api/v1 && cat > projects.py << \'EOF\'\n{content}\nEOF"'
print("正在创建projects.py文件...")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(f"命令执行结果: {result.returncode}")
if result.stdout:
    print(f"输出: {result.stdout}")
if result.stderr:
    print(f"错误: {result.stderr}")
