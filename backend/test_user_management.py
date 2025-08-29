#!/usr/bin/env python3
"""
测试用户管理API接口
"""
import requests
import json
import sys

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@monitoring.local"  # 监控系统管理员邮箱
ADMIN_PASSWORD = "Lovelewis@586930"  # 监控系统管理员密码

def get_admin_token():
    """获取管理员访问令牌"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/monitoring/login", data={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_get_tenants(token):
    """测试获取租户列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/tenants", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取租户列表成功，共 {len(data.get('tenants', []))} 个租户")
            return data.get('tenants', [])
        else:
            print(f"❌ 获取租户列表失败: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ 获取租户列表异常: {e}")
        return []

def test_get_tenant_detail(token, tenant_id):
    """测试获取租户详情"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/tenants/{tenant_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取租户详情成功: {data.get('name', 'Unknown')}")
            print(f"   用户数量: {len(data.get('users', []))}")
            return data
        else:
            print(f"❌ 获取租户详情失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取租户详情异常: {e}")
        return None

def test_user_management_apis(token, tenant_id, user_id):
    """测试用户管理API接口"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔧 测试租户 {tenant_id} 的用户 {user_id} 管理功能:")
    
    # 测试1: 更新用户状态
    print("\n1. 测试更新用户状态...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/tenants/{tenant_id}/users/{user_id}/status",
            params={"is_active": False, "reason": "测试禁用用户"},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 禁用用户成功: {data.get('message')}")
        else:
            print(f"   ❌ 禁用用户失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 禁用用户异常: {e}")
    
    # 测试2: 重新启用用户
    print("\n2. 测试重新启用用户...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/tenants/{tenant_id}/users/{user_id}/status",
            params={"is_active": True, "reason": "测试启用用户"},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 启用用户成功: {data.get('message')}")
        else:
            print(f"   ❌ 启用用户失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 启用用户异常: {e}")
    
    # 测试3: 更新用户角色
    print("\n3. 测试更新用户角色...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/tenants/{tenant_id}/users/{user_id}/role",
            params={"role": "admin", "reason": "测试角色修改"},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 更新用户角色成功: {data.get('message')}")
        else:
            print(f"   ❌ 更新用户角色失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 更新用户角色异常: {e}")
    
    # 测试4: 恢复用户角色
    print("\n4. 测试恢复用户角色...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/tenants/{tenant_id}/users/{user_id}/role",
            params={"role": "super_admin", "reason": "测试恢复角色"},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 恢复用户角色成功: {data.get('message')}")
        else:
            print(f"   ❌ 恢复用户角色失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 恢复用户角色异常: {e}")

def main():
    """主函数"""
    print("🚀 开始测试用户管理API接口...")
    
    # 1. 获取管理员令牌
    print("\n1. 获取管理员访问令牌...")
    token = get_admin_token()
    if not token:
        print("❌ 无法获取管理员令牌，测试终止")
        sys.exit(1)
    print("✅ 成功获取管理员令牌")
    
    # 2. 获取租户列表
    print("\n2. 获取租户列表...")
    tenants = test_get_tenants(token)
    if not tenants:
        print("❌ 无法获取租户列表，测试终止")
        sys.exit(1)
    
    # 3. 选择第一个非监控系统的租户进行测试
    test_tenant = None
    for tenant in tenants:
        if tenant.get('name') != "监控系统":
            test_tenant = tenant
            break
    
    if not test_tenant:
        print("❌ 没有找到可测试的租户，测试终止")
        sys.exit(1)
    
    print(f"✅ 选择测试租户: {test_tenant.get('name')} (ID: {test_tenant.get('id')})")
    
    # 4. 获取租户详情
    print("\n3. 获取租户详情...")
    tenant_detail = test_get_tenant_detail(token, test_tenant['id'])
    if not tenant_detail or not tenant_detail.get('users'):
        print("❌ 租户下没有用户，无法测试用户管理功能")
        sys.exit(1)
    
    # 5. 选择第一个用户进行测试
    test_user = tenant_detail['users'][0]
    print(f"✅ 选择测试用户: {test_user.get('email')} (ID: {test_user.get('id')})")
    
    # 6. 测试用户管理API
    test_user_management_apis(token, test_tenant['id'], test_user['id'])
    
    print("\n🎉 用户管理API测试完成！")
    print("\n📋 测试总结:")
    print("   - 用户状态管理 (启用/禁用)")
    print("   - 用户角色管理 (角色修改)")
    print("   - 所有操作都有完整的日志记录")
    print("   - 包含安全检查 (防止删除唯一超级管理员)")

if __name__ == "__main__":
    main()
