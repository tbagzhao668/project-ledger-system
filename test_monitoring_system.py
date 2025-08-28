#!/usr/bin/env python3
"""
测试监控系统功能的脚本
"""

import asyncio
import asyncpg
import requests
import json

async def test_monitoring_system():
    """测试监控系统功能"""
    print("🔍 测试监控系统功能...")
    
    try:
        # 1. 测试监控系统登录
        print("\n1. 🔐 测试监控系统登录...")
        login_data = {
            'email': 'admin@monitoring.local',
            'password': 'Lovelewis@586930'
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/monitoring/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            login_result = response.json()
            print(f"   ✅ 登录成功")
            print(f"      用户ID: {login_result['user']['id']}")
            print(f"      角色: {login_result['user']['role']}")
            print(f"      Token: {login_result['access_token'][:50]}...")
            
            # 保存token用于后续测试
            access_token = login_result['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
            print(f"      响应: {response.text}")
            return
        
        # 2. 测试监控系统健康检查
        print("\n2. 🏥 测试监控系统健康检查...")
        health_response = requests.get(
            'http://localhost:8000/api/v1/admin/health',
            headers=headers
        )
        
        if health_response.status_code == 200:
            print("   ✅ 健康检查API正常")
        else:
            print(f"   ❌ 健康检查API失败: {health_response.status_code}")
        
        # 3. 测试租户管理API
        print("\n3. 🏢 测试租户管理API...")
        tenants_response = requests.get(
            'http://localhost:8000/api/v1/admin/tenants',
            headers=headers
        )
        
        if tenants_response.status_code == 200:
            tenants_data = tenants_response.json()
            print(f"   ✅ 租户管理API正常，找到 {len(tenants_data)} 个租户")
        else:
            print(f"   ❌ 租户管理API失败: {tenants_response.status_code}")
        
        # 4. 测试系统统计API
        print("\n4. 📊 测试系统统计API...")
        stats_response = requests.get(
            'http://localhost:8000/api/v1/admin/statistics',
            headers=headers
        )
        
        if stats_response.status_code == 200:
            print("   ✅ 系统统计API正常")
        else:
            print(f"   ❌ 系统统计API失败: {stats_response.status_code}")
        
        # 5. 测试数据库中的监控数据
        print("\n5. 🗄️ 检查数据库中的监控数据...")
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='project_ledger'
        )
        
        # 检查监控系统用户
        monitoring_user = await conn.fetchrow("""
            SELECT id, username, email, role, is_active 
            FROM users 
            WHERE email = 'admin@monitoring.local'
        """)
        
        if monitoring_user:
            print(f"   ✅ 监控系统用户存在: {monitoring_user['username']}")
            print(f"      角色: {monitoring_user['role']}")
            print(f"      状态: {'激活' if monitoring_user['is_active'] else '未激活'}")
        else:
            print("   ❌ 监控系统用户不存在")
        
        # 检查监控系统租户
        monitoring_tenant = await conn.fetchrow("""
            SELECT id, name, domain, status 
            FROM tenants 
            WHERE name = '监控系统'
        """)
        
        if monitoring_tenant:
            print(f"   ✅ 监控系统租户存在: {monitoring_tenant['name']}")
            print(f"      域名: {monitoring_tenant['domain']}")
            print(f"      状态: {monitoring_tenant['status']}")
        else:
            print("   ❌ 监控系统租户不存在")
        
        await conn.close()
        
        print("\n🎉 监控系统功能测试完成！")
        print("\n🌐 访问地址:")
        print("   - 监控系统登录: http://localhost:3000/monitoring/login")
        print("   - 监控仪表盘: http://localhost:3000/monitoring/dashboard")
        print("   - 租户管理: http://localhost:3000/monitoring/tenants")
        print("   - 系统日志: http://localhost:3000/monitoring/logs")
        print("   - 健康检查: http://localhost:3000/monitoring/health")
        
    except Exception as e:
        print(f"❌ 测试监控系统失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_monitoring_system())
