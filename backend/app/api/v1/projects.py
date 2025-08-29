"""项目管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text, case
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from ...core.auth import get_current_user, require_permissions
from ...core.database import get_db
from ...models.user import User
from ...models.project import Project, ProjectChangeLog
from ...models.transaction import Transaction
from ...schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectStatistics, ProjectQueryParams, ProjectStatusEnum, ProjectTypeEnum,
    ProjectPriorityEnum, ChangeLogResponse
)

router = APIRouter(prefix="/projects")

# 根路径路由必须在参数化路由之前定义，避免路由冲突
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
        # 构建查询条件 - 添加租户隔离
        query = select(Project).options(selectinload(Project.manager))
        
        # 添加租户隔离条件
        query = query.where(Project.tenant_id == current_user.tenant_id)
        
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
                Project.project_code.contains(search)
            )
            query = query.where(search_filter)
        
        # 添加分页和排序
        query = query.offset(skip).limit(limit).order_by(desc(Project.created_at))
        
        result = await db.execute(query)
        projects = result.scalars().unique().all()
        
        # 转换为前端期望的格式
        formatted_projects = []
        for project in projects:
            try:
                # 获取项目经理姓名
                manager_name = "未分配"
                if project.manager:
                    manager_name = project.manager.name if hasattr(project.manager, 'name') else "未知"
                elif project.manager_name:
                    manager_name = project.manager_name
                
                # 获取创建人姓名
                created_by_name = "系统用户"
                
                # 格式化日期
                start_date = project.start_date.isoformat() if project.start_date else None
                end_date = project.end_date.isoformat() if project.end_date else None
                actual_end_date = project.actual_end_date.isoformat() if project.actual_end_date else None
                created_at = project.created_at.isoformat() if project.created_at else None
                updated_at = project.updated_at.isoformat() if project.updated_at else None
                
                # 转换金额类型
                budget = float(project.budget) if project.budget else None
                contract_amount = float(project.contract_value) if project.contract_value else None
                actual_expenses = float(project.actual_cost) if project.actual_cost else None
                
                # 计算利润
                profit = None
                if contract_amount and actual_expenses:
                    profit = contract_amount - actual_expenses
                elif contract_amount and budget:
                    profit = contract_amount - budget
                
                formatted_project = {
                    "id": str(project.id),
                    "project_code": project.project_code,
                    "name": project.name,
                    "description": project.description,
                    "project_type": project.project_type if project.project_type else None,
                    "priority": project.priority if project.priority else None,
                    "status": project.status if project.status else "planning",
                    "start_date": start_date,
                    "planned_end_date": end_date,
                    "end_date": end_date,
                    "actual_end_date": actual_end_date,
                    "budget": budget,
                    "contract_amount": contract_amount,
                    "actual_expenses": actual_expenses,
                    "profit": profit,
                    "currency": "CNY",
                    "location": str(project.location) if project.location else None,
                    "client_name": project.client_info.get('name') if hasattr(project, 'client_info') and project.client_info else None,
                    "client_contact": project.client_info.get('contact') if hasattr(project, 'client_info') and project.client_info else None,
                    "client_phone": project.client_info.get('phone') if hasattr(project, 'client_info') and project.client_info else None,
                    "tags": project.tags,
                    "notes": project.description,
                    "manager_id": str(project.manager_id) if project.manager_id else None,
                    "manager_name": manager_name,
                    "created_by": str(project.created_by),
                    "created_by_name": created_by_name,
                    "created_at": created_at,
                    "updated_at": updated_at
                }
                
                formatted_projects.append(formatted_project)
                
            except Exception as e:
                print(f"DEBUG: 处理项目时出错: {str(e)}")
                continue
        
        return formatted_projects
        
    except Exception as e:
        print(f"DEBUG: get_projects 函数出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目列表失败: {str(e)}"
        )



# 统计API必须在项目详情API之前定义，避免路由冲突
@router.get("/statistics", summary="获取项目统计概览")
async def get_project_statistics(
    current_user: User = Depends(require_permissions(["project_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目统计概览数据
    
    需要权限: project_read
    """
    try:
        print(f"开始获取项目统计，用户ID: {current_user.id}, 租户ID: {current_user.tenant_id}")
        
        # 构建基础查询条件
        base_conditions = [Project.tenant_id == current_user.tenant_id]
        
        # 1. 项目总数
        total_query = await db.execute(
            select(func.count(Project.id)).where(and_(*base_conditions))
        )
        total_projects = total_query.scalar() or 0
        print(f"项目总数: {total_projects}")
        
        # 2. 各状态项目数量
        status_query = await db.execute(
            select(
                Project.status,
                func.count(Project.id).label('count')
            ).where(and_(*base_conditions))
            .group_by(Project.status)
        )
        
        status_counts = {}
        for row in status_query.all():
            status_counts[row.status] = row.count
            print(f"状态 {row.status}: {row.count} 个项目")
        
        # 3. 总预算和合同金额
        financial_query = await db.execute(
            select(
                func.sum(Project.budget).label('total_budget'),
                func.sum(Project.contract_value).label('total_contract_amount')
            ).where(and_(*base_conditions))
        )
        financial_data = financial_query.first()
        
        total_budget = float(financial_data.total_budget or 0)
        total_contract_amount = float(financial_data.total_contract_amount or 0)
        
        print(f"总预算: {total_budget}, 总合同金额: {total_contract_amount}")
        
        result = {
            "total_projects": total_projects,
            "completed_projects": status_counts.get('completed', 0),
            "ongoing_projects": status_counts.get('in_progress', 0),
            "delayed_projects": status_counts.get('delayed', 0),
            "planning_projects": status_counts.get('planning', 0),
            "total_budget": total_budget,
            "total_contract_amount": total_contract_amount
        }
        
        print(f"返回统计结果: {result}")
        return result
        
    except Exception as e:
        print(f"项目统计查询异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目统计失败: {str(e)}"
        )

@router.get("/statistics/status", summary="获取项目状态分布")
async def get_project_status_distribution(
    current_user: User = Depends(require_permissions(["project_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目状态分布数据
    
    需要权限: project_read
    """
    try:
        # 构建查询条件
        query_conditions = [Project.tenant_id == current_user.tenant_id]
        
        # 查询各状态项目数量
        status_query = await db.execute(
            select(
                Project.status,
                func.count(Project.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(Project.status)
        )
        
        # 状态颜色映射
        status_colors = {
            'planning': '#909399',
            'in_progress': '#409eff',
            'on_hold': '#e6a23c',
            'completed': '#67c23a',
            'cancelled': '#f56c6c',
            'delayed': '#f56c6c'
        }
        
        # 状态名称映射
        status_names = {
            'planning': '规划中',
            'in_progress': '进行中',
            'on_hold': '暂停',
            'completed': '已完成',
            'cancelled': '已取消',
            'delayed': '延期'
        }
        
        status_distribution = []
        for row in status_query.all():
            status = row.status or 'unknown'
            status_distribution.append({
                'name': status_names.get(status, status),
                'value': row.count,
                'itemStyle': { 'color': status_colors.get(status, '#909399') }
            })
        
        return {
            "status_distribution": status_distribution
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目状态分布失败: {str(e)}"
        )

@router.get("/statistics/trend", summary="获取项目月度趋势")
async def get_project_monthly_trend(
    months: int = Query(6, ge=1, le=24, description="统计月数"),
    current_user: User = Depends(require_permissions(["project_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目月度趋势数据
    
    需要权限: project_read
    """
    try:
        # 构建查询条件
        query_conditions = [Project.tenant_id == current_user.tenant_id]
        
        # 查询月度项目数量和预算
        trend_query = await db.execute(
            select(
                func.extract('year', Project.created_at).label('year'),
                func.extract('month', Project.created_at).label('month'),
                func.count(Project.id).label('projects'),
                func.sum(Project.budget).label('budget')
            ).where(and_(*query_conditions))
            .group_by(
                func.extract('year', Project.created_at),
                func.extract('month', Project.created_at)
            )
            .order_by(
                func.extract('year', Project.created_at).desc(),
                func.extract('month', Project.created_at).desc()
            )
            .limit(months)
        )
        
        monthly_trend = []
        month_names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        
        for row in trend_query.all():
            month_label = f"{int(row.year)}年{month_names[int(row.month)-1]}"
            monthly_trend.append({
                'month': month_label,
                'projects': row.projects,
                'budget': float(row.budget or 0)
            })
        
        # 按时间正序排列
        monthly_trend.reverse()
        
        return {
            "monthly_trend": monthly_trend
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目月度趋势失败: {str(e)}"
        )

@router.get("/statistics/types", summary="获取项目类型分布")
async def get_project_type_distribution(
    current_user: User = Depends(require_permissions(["project_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目类型分布数据
    
    需要权限: project_read
    """
    try:
        # 构建查询条件
        query_conditions = [Project.tenant_id == current_user.tenant_id]
        
        # 查询各类型项目数量
        type_query = await db.execute(
            select(
                Project.project_type,
                func.count(Project.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(Project.project_type)
            .order_by(func.count(Project.id).desc())
        )
        
        # 类型名称映射
        type_names = {
            'construction': '建筑工程',
            'decoration': '装饰工程',
            'municipal': '市政工程',
            'electrical': '电气工程',
            'mechanical': '机械工程',
            'industrial': '工业工程',
            'residential': '住宅工程',
            'commercial': '商业工程',
            'infrastructure': '基础设施工程',
            'renovation': '改造工程',
            'maintenance': '维护工程',
            'other': '其他工程'
        }
        
        type_distribution = []
        for row in type_query.all():
            project_type = row.project_type or 'other'
            type_distribution.append({
                'name': type_names.get(project_type, project_type),
                'value': row.count,
                'itemStyle': { 'color': f'#{hash(project_type) % 0xFFFFFF:06x}' }
            })
        
        return {
            "type_distribution": type_distribution
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目类型分布失败: {str(e)}"
        )

@router.get("/statistics/progress", summary="获取项目进度分布")
async def get_project_progress_distribution(
    current_user: User = Depends(require_permissions(["project_read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目进度分布数据
    
    需要权限: project_read
    """
    try:
        # 构建查询条件
        query_conditions = [Project.tenant_id == current_user.tenant_id]
        
        # 查询各进度范围项目数量
        progress_query = await db.execute(
            select(
                case(
                    (Project.progress < 20, '0-20%'),
                    (Project.progress < 50, '20-50%'),
                    (Project.progress < 80, '50-80%'),
                    (Project.progress < 100, '80-100%'),
                    else_='100%'
                ).label('progress_range'),
                func.count(Project.id).label('count')
            ).where(and_(*query_conditions))
            .group_by(text('progress_range'))
            .order_by(text('progress_range'))
        )
        
        progress_distribution = []
        for row in progress_query.all():
            progress_distribution.append({
                'range': row.progress_range,
                'count': row.count
            })
        
        return {
            "progress_distribution": progress_distribution
        }
        
    except Exception as e:
        print(f"项目进度分布查询异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目进度分布失败: {str(e)}"
        )



@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新项目"""
    try:
        print(f"DEBUG: 接收到的项目数据: {project_data.dict()}")
        
        # 检查项目代码是否已存在（在同一租户内）
        existing_project = await db.execute(
            select(Project).where(
                and_(
                    Project.project_code == project_data.project_code,
                    Project.tenant_id == current_user.tenant_id  # 添加租户隔离
                )
            )
        )
        if existing_project.scalar_one_or_none():
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="项目代码已存在"
            )
        
        # 准备项目数据，处理字段映射
        project_dict = project_data.dict()
        print(f"DEBUG: 处理后的项目数据: {project_dict}")
        
        # 字段映射：将schema字段映射到模型字段
        mapped_data = {
            'name': project_dict['name'],
            'project_code': project_dict['project_code'],  # project_code -> project_code
            'description': project_dict.get('description'),
            'project_type': project_dict['project_type'],
            'priority': project_dict['priority'],
            'status': project_dict['status'],
            'start_date': project_dict.get('start_date'),
            'end_date': project_dict.get('end_date'),  # end_date -> end_date
            'budget': project_dict.get('budget'),
            'contract_value': project_dict.get('contract_amount'),  # contract_amount -> contract_value
            'address': project_dict.get('address'),  # address -> address
            'manager_name': project_dict.get('manager_name'),  # 项目经理姓名
            'client_info': {
                'name': project_dict.get('client_name'),
                'contact': project_dict.get('client_contact'),
                'phone': project_dict.get('client_phone')
            },
            'tags': project_dict.get('tags', []),
            'tenant_id': current_user.tenant_id,  # 添加租户ID
            'created_by': current_user.id,
            'created_at': datetime.utcnow()
        }
        
        # 验证合同金额
        if not mapped_data['contract_value']:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="合同金额不能为空，请输入合同金额"
            )
        
        print(f"DEBUG: 映射后的数据: {mapped_data}")
        
        # 创建新项目
        new_project = Project(**mapped_data)
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        print(f"DEBUG: 项目创建成功，ID: {new_project.id}")
        
        # 手动格式化响应数据以匹配ProjectResponse schema
        response_data = {
            "id": str(new_project.id),
            "project_code": new_project.project_code,
            "name": new_project.name,
            "description": new_project.description,
            "project_type": new_project.project_type,
            "priority": new_project.priority,
            "status": new_project.status,
            "start_date": new_project.start_date.isoformat() if new_project.start_date else None,
            "planned_end_date": new_project.end_date.isoformat() if new_project.end_date else None,
            "end_date": new_project.end_date.isoformat() if new_project.end_date else None,
            "actual_end_date": new_project.actual_end_date.isoformat() if new_project.actual_end_date else None,
            "budget": float(new_project.budget) if new_project.budget else None,
            "contract_amount": float(new_project.contract_value) if new_project.contract_value else None,
            "actual_expenses": float(new_project.actual_cost) if new_project.actual_cost else None,
            "currency": "CNY",
            "location": str(new_project.location) if new_project.location else None,
            "client_name": new_project.client_info.get('name') if new_project.client_info else None,
            "client_contact": new_project.client_info.get('contact') if new_project.client_info else None,
            "client_phone": new_project.client_info.get('phone') if new_project.client_info else None,
            "tags": new_project.tags or [],
            "notes": new_project.description,
            "manager_id": str(new_project.manager_id) if new_project.manager_id else None,
            "manager_name": new_project.manager_name,
            "created_by": str(new_project.created_by),
            "created_by_name": "系统用户",  # 这里可以根据需要查询用户表
            "created_at": new_project.created_at.isoformat() if new_project.created_at else None,
            "updated_at": new_project.updated_at.isoformat() if new_project.updated_at else None
        }
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"ERROR: 创建项目失败: {str(e)}")
        print(f"ERROR: 错误类型: {type(e)}")
        import traceback
        print(f"ERROR: 错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建项目失败: {str(e)}"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目详情"""
    try:
        print(f"DEBUG: 获取项目详情，ID: {project_id}")
        
        # 将字符串ID转换为UUID
        try:
            project_uuid = UUID(project_id)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="无效的项目ID格式"
            )
        
        project = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_uuid,
                    Project.tenant_id == current_user.tenant_id  # 添加租户隔离
                )
            )
        )
        project = project.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 项目信息获取成功
        
        # 手动格式化响应数据以匹配ProjectResponse schema
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
            "client_name": project.client_info.get('name') if project.client_info else None,
            "client_contact": project.client_info.get('contact') if project.client_info else None,
            "client_phone": project.client_info.get('phone') if project.client_info else None,
            "tags": project.tags or [],
            "notes": project.description,
            "manager_id": str(project.manager_id) if project.manager_id else None,
            "manager_name": project.manager_name,
            "created_by": str(project.created_by),
            "created_by_name": "系统用户",  # 这里可以根据需要查询用户表
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        }
        
        # 项目详情格式化完成
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: 获取项目详情失败: {str(e)}")
        print(f"ERROR: 错误类型: {type(e)}")
        import traceback
        print(f"ERROR: 错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目详情失败: {str(e)}"
        )

@router.get("/{project_id}/change-logs")
async def get_project_change_logs(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目变更日志"""
    try:
        print(f"DEBUG: 获取项目变更日志，项目ID: {project_id}")
        
        # 将字符串ID转换为UUID
        try:
            project_uuid = UUID(project_id)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="无效的项目ID格式"
            )
        
        # 检查项目是否存在
        project = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_uuid,
                    Project.tenant_id == current_user.tenant_id  # 添加租户隔离
                )
            )
        )
        if not project.scalar_one_or_none():
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 获取项目变更日志
        change_logs = await db.execute(
            select(ProjectChangeLog)
            .where(ProjectChangeLog.project_id == project_uuid)
            .order_by(desc(ProjectChangeLog.created_at))
        )
        change_logs = change_logs.scalars().all()
        
        # 变更日志获取成功
        
        # 格式化变更记录数据
        formatted_logs = []
        for log in change_logs:
            # 处理合并后的变更记录
            if log.field_name and ',' in log.field_name:
                # 多个字段合并的变更
                field_names = log.field_name.split(',')
                field_display_names = [get_field_display_name(field) for field in field_names]
                field_display_name = '、'.join(field_display_names)
            else:
                # 单个字段变更
                field_display_name = get_field_display_name(log.field_name) if log.field_name else '项目信息'
            
            # 构建完整的变更记录
            if log.change_description:
                # 使用后端已经格式化好的变更记录
                change_record = log.change_description
            else:
                # 如果没有变更记录，构建一个
                change_record = f"{field_display_name}已更新"
            
            formatted_log = {
                "id": str(log.id),
                "change_type": log.change_type,
                "field_name": log.field_name,
                "field_display_name": field_display_name,
                "change_description": log.change_description,
                "change_reason": log.change_reason,
                "change_record": change_record,  # 改名为change_record
                "changed_by": str(log.changed_by) if log.changed_by else None,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            formatted_logs.append(formatted_log)
        
        return formatted_logs
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: 获取项目变更日志失败: {str(e)}")
        print(f"ERROR: 错误类型: {type(e)}")
        import traceback
        print(f"ERROR: 错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目变更日志失败: {str(e)}"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目信息"""
    try:
        print(f"DEBUG: 更新项目，ID: {project_id}")
        
        # 将字符串ID转换为UUID
        try:
            project_uuid = UUID(project_id)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="无效的项目ID格式"
            )
        
        project = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_uuid,
                    Project.tenant_id == current_user.tenant_id  # 添加租户隔离
                )
            )
        )
        project = project.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 记录原始值用于变更日志
        original_values = {}
        update_data = project_data.dict(exclude_unset=True)
        
        # 记录变更记录 - 按您要求的格式
        change_logs = []
        changed_fields = []
        field_changes = []
        
        # 排除技术字段，只处理实际的项目字段
        excluded_fields = {'budget_change_reason', 'contract_change_reason', 'change_description'}
        
        for field, new_value in update_data.items():
            # 跳过技术字段
            if field in excluded_fields:
                continue
            
            # 字段映射：将前端字段名映射到数据库字段名
            db_field = field
            if field == 'contract_amount':
                db_field = 'contract_value'
            
            if hasattr(project, db_field):
                old_value = getattr(project, db_field)
                if old_value != new_value:
                    original_values[field] = old_value
                    changed_fields.append(field)
                    
                    # 格式化字段变更信息
                    field_display_name = get_field_display_name(field)
                    old_value_display = format_field_value(field, old_value)
                    new_value_display = format_field_value(field, new_value)
                    
                    # 构建单个字段的变更记录
                    if field in ['budget', 'contract_amount']:
                        # 金额字段需要显示变更原因
                        if field == 'budget' and hasattr(project_data, 'budget_change_reason') and project_data.budget_change_reason:
                            field_change = f"{field_display_name}[{old_value_display}]变更成[{new_value_display}]，变更原因[{project_data.budget_change_reason}]"
                        elif field == 'contract_amount' and hasattr(project_data, 'contract_change_reason') and project_data.contract_change_reason:
                            field_change = f"{field_display_name}[{old_value_display}]变更成[{new_value_display}]，变更原因[{project_data.contract_change_reason}]"
                        else:
                            field_change = f"{field_display_name}[{old_value_display}]变更成[{new_value_display}]"
                    else:
                        # 非金额字段
                        field_change = f"{field_display_name}[{old_value_display}]变更成[{new_value_display}]"
                    
                    field_changes.append(field_change)
        
        # 如果有变更，创建变更记录
        if changed_fields:
            # 获取变更原因和详细说明
            change_reason = None
            change_description = None
            
            # 检查是否有金额变更
            has_budget_change = 'budget' in changed_fields
            has_contract_change = 'contract_amount' in changed_fields
            
            if has_budget_change and hasattr(project_data, 'budget_change_reason') and project_data.budget_change_reason:
                change_reason = project_data.budget_change_reason
            elif has_contract_change and hasattr(project_data, 'contract_change_reason') and project_data.contract_change_reason:
                change_reason = project_data.contract_change_reason
            
            if hasattr(project_data, 'change_description') and project_data.change_description:
                change_description = project_data.change_description
            
            # 构建完整的变更记录
            complete_change_record = "\n".join(field_changes)
            
            # 创建变更记录
            change_log = ProjectChangeLog(
                tenant_id=current_user.tenant_id,
                project_id=project_uuid,
                change_type='update',
                field_name=','.join(changed_fields),  # 合并所有变更字段
                old_value=None,  # 不再单独存储每个字段的原值
                new_value=None,  # 不再单独存储每个字段的新值
                change_description=complete_change_record,  # 完整的变更记录
                change_reason=change_reason,
                changed_by=current_user.id,
                created_at=datetime.utcnow()
            )
            change_logs.append(change_log)
        
        # 更新项目信息
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)
        
        # 特殊字段映射
        if 'contract_amount' in update_data:
            project.contract_value = update_data['contract_amount']
        
        project.updated_at = datetime.utcnow()
        project.updated_by = current_user.id
        
        # 保存变更日志
        for change_log in change_logs:
            db.add(change_log)
        
        await db.commit()
        await db.refresh(project)
        
        # 项目更新成功
        
        # 手动格式化响应数据以匹配ProjectResponse schema
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
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"ERROR: 更新项目失败: {str(e)}")
        print(f"ERROR: 错误类型: {type(e)}")
        import traceback
        print(f"ERROR: 错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新项目失败: {str(e)}"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目"""
    try:
        # 删除项目请求处理
        try:
            project_uuid = UUID(project_id)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="无效的项目ID格式"
            )
        
        project = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_uuid,
                    Project.tenant_id == current_user.tenant_id  # 添加租户隔离
                )
            )
        )
        project = project.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 删除项目
        await db.delete(project)
        await db.commit()
        
        return {"message": "项目删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除项目失败: {str(e)}"
        )

@router.put("/{project_id}/status")
async def update_project_status(
    project_id: str,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目状态"""
    try:
        # 查找项目
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.tenant_id == current_user.tenant_id  # 添加租户隔离
                )
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 验证状态值
        new_status = status_data.get("status")
        if not new_status:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="状态值不能为空"
            )
        
        # 更新项目状态
        project.status = new_status
        project.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"success": True, "message": "项目状态更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新项目状态失败: {str(e)}"
        )


def get_change_reason(field: str, project_data: ProjectUpdate) -> str:
    """获取字段变更的原因"""
    if field == 'budget' and hasattr(project_data, 'budget_change_reason'):
        return project_data.budget_change_reason or '预算调整'
    elif field == 'contract_amount' and hasattr(project_data, 'contract_change_reason'):
        return project_data.contract_change_reason or '合同变更'
    else:
        return '字段更新'


def get_field_display_name(field_name: str) -> str:
    """将字段名转换为用户友好的显示名称"""
    field_mapping = {
        'name': '项目名称',
        'description': '项目描述',
        'project_type': '项目类型',
        'priority': '项目优先级',
        'status': '项目状态',
        'start_date': '开始日期',
        'end_date': '结束日期',
        'budget': '项目预算',
        'contract_amount': '合同金额',
        'address': '项目地址',
        'manager_name': '项目经理',
        'client_name': '客户名称',
        'client_contact': '客户联系人',
        'client_phone': '客户电话',
        'tags': '项目标签'
    }
    return field_mapping.get(field_name, field_name)


def format_field_value(field_name: str, value) -> str:
    """格式化字段值的显示"""
    if value is None or value == "":
        if field_name == 'address':
            return '未填写'
        return '未设置'
    
    if field_name == 'budget' or field_name == 'contract_amount':
        if value:
            return f"{float(value):,.0f} 元"
        return '未设置'
    elif field_name == 'start_date' or field_name == 'end_date':
        if value:
            return str(value)
        return '未设置'
    elif field_name == 'project_type':
        type_mapping = {
            'municipal': '市政工程',
            'decoration': '装饰工程',
            'construction': '建筑工程',
            'water_conservancy': '水利水电工程',
            'installation': '安装工程',
            'highway': '公路工程',
            'bridge': '桥梁工程',
            'tunnel': '隧道工程',
            'mechanical_electrical': '机电工程',
            'other': '其他'
        }
        return type_mapping.get(value, value)
    elif field_name == 'priority':
        priority_mapping = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '紧急'
        }
        return priority_mapping.get(value, value)
    elif field_name == 'status':
        status_mapping = {
            'planning': '规划中',
            'in_progress': '进行中',
            'on_hold': '暂停',
            'completed': '已完成',
            'cancelled': '已取消'
        }
        return status_mapping.get(value, value)
    elif field_name == 'tags':
        if isinstance(value, list):
            return ', '.join(value) if value else '无'
        return str(value)
    else:
        return str(value) if value else '未设置'


def build_change_summary(field_display_name: str, old_value: str, new_value: str, change_reason: str, change_description: str) -> str:
    """构建用户友好的变更描述"""
    # 基础变更描述
    summary = f"{field_display_name}由「{old_value}」变更为「{new_value}」"
    
    # 如果有变更原因，添加到描述中
    if change_reason and change_reason not in ['字段更新', '预算调整', '合同变更']:
        summary += f"，变更原因：{change_reason}"
    
    # 如果有详细说明，添加到描述中
    if change_description:
        summary += f"，详细说明：{change_description}"
    
    return summary
