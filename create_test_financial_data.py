#!/usr/bin/env python3
"""
创建测试财务数据的脚本
"""
import asyncio
import sys
import os
from datetime import date, datetime
from decimal import Decimal

# 添加项目路径
sys.path.append('.')

async def create_test_financial_data():
    try:
        from app.core.database import db_manager
        from app.models.transaction import Transaction, Category
        from app.models.project import Project
        from app.models.user import User
        from sqlalchemy import select
        
        # 初始化数据库连接
        db_manager.initialize()
        
        async for session in db_manager.get_session():
            print("开始创建测试财务数据...")
            
            # 获取租户ID和用户ID - 使用有项目的租户
            projects_result = await session.execute(
                select(Project.tenant_id).where(Project.tenant_id.isnot(None)).limit(1)
            )
            tenant_id = projects_result.scalar()
            
            if not tenant_id:
                print("❌ 未找到有项目的租户")
                return
            
            user_result = await session.execute(
                select(User.id).where(User.tenant_id == tenant_id).limit(1)
            )
            user_id = user_result.scalar()
            
            if not tenant_id or not user_id:
                print("❌ 未找到租户或用户数据")
                return
            
            print(f"使用租户ID: {tenant_id}")
            print(f"使用用户ID: {user_id}")
            
            # 获取项目列表
            projects_result = await session.execute(
                select(Project.id, Project.name).where(Project.tenant_id == tenant_id).limit(5)
            )
            projects = projects_result.fetchall()
            
            if not projects:
                print("❌ 未找到项目数据")
                return
            
            print(f"找到 {len(projects)} 个项目")
            
            # 创建测试财务记录
            test_transactions = []
            
            for i, (project_id, project_name) in enumerate(projects):
                print(f"为项目 '{project_name}' 创建财务记录...")
                
                # 收入记录（合同款）
                income_transaction = Transaction(
                    tenant_id=tenant_id,
                    project_id=project_id,
                    type='income',
                    amount=Decimal('1000000.00'),  # 100万收入
                    amount_base=Decimal('1000000.00'),
                    description=f'项目{project_name}合同款',
                    transaction_date=date.today(),
                    status='confirmed',
                    approval_status='approved',
                    created_by=user_id,
                    approved_by=user_id,
                    approved_at=date.today()
                )
                test_transactions.append(income_transaction)
                
                # 支出记录（材料费）
                expense_material = Transaction(
                    tenant_id=tenant_id,
                    project_id=project_id,
                    type='expense',
                    amount=Decimal('300000.00'),  # 30万材料费
                    amount_base=Decimal('300000.00'),
                    description=f'项目{project_name}材料费',
                    transaction_date=date.today(),
                    status='confirmed',
                    approval_status='approved',
                    created_by=user_id,
                    approved_by=user_id,
                    approved_at=date.today()
                )
                test_transactions.append(expense_material)
                
                # 支出记录（人工费）
                expense_labor = Transaction(
                    tenant_id=tenant_id,
                    project_id=project_id,
                    type='expense',
                    amount=Decimal('200000.00'),  # 20万人工费
                    amount_base=Decimal('200000.00'),
                    description=f'项目{project_name}人工费',
                    transaction_date=date.today(),
                    status='confirmed',
                    approval_status='approved',
                    created_by=user_id,
                    approved_by=user_id,
                    approved_at=date.today()
                )
                test_transactions.append(expense_labor)
                
                # 支出记录（设备费）
                expense_equipment = Transaction(
                    tenant_id=tenant_id,
                    project_id=project_id,
                    type='expense',
                    amount=Decimal('150000.00'),  # 15万设备费
                    amount_base=Decimal('150000.00'),
                    description=f'项目{project_name}设备费',
                    transaction_date=date.today(),
                    status='confirmed',
                    approval_status='approved',
                    created_by=user_id,
                    approved_by=user_id,
                    approved_at=date.today()
                )
                test_transactions.append(expense_equipment)
            
            # 批量插入财务记录
            for transaction in test_transactions:
                session.add(transaction)
            
            await session.commit()
            
            print(f"✅ 成功创建 {len(test_transactions)} 条财务记录")
            
            # 验证数据
            total_income = sum(t.amount for t in test_transactions if t.type == 'income')
            total_expense = sum(t.amount for t in test_transactions if t.type == 'expense')
            
            print(f"总收入: ¥{total_income:,.2f}")
            print(f"总支出: ¥{total_expense:,.2f}")
            print(f"净收入: ¥{total_income - total_expense:,.2f}")
            
            print("✅ 测试财务数据创建完成！")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_financial_data())
