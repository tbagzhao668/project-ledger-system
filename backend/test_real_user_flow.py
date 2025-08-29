#!/usr/bin/env python3
"""
使用真实账号密码测试前端完整流程脚本
"""
import asyncio
import sys
import os
import json
import requests

async def test_real_user_flow():
    """使用真实账号测试前端完整流程"""
    try:
        print("=== 使用真实账号测试前端完整流程 ===")
        
        # 真实账号信息
        base_url = "http://localhost:8000"
        login_credentials = {
            'email': '123@123.com',
            'password': '123123'
        }
        
        # 测试数据
        test_user_data = {
            'name': '真实用户测试',
            'phone': '13900139000',
            'position': '测试工程师',
            'department': '测试部',
            'bio': '这是真实用户的测试简介'
        }
        
        print(f"真实账号: {login_credentials['email']}")
        print(f"测试数据: {test_user_data}")
        print(f"API地址: {base_url}")
        
        # 1. 登录获取token
        print("\n1. 登录获取token")
        try:
            response = requests.post(
                f"{base_url}/api/v1/auth/login",
                json=login_credentials,
                headers={'Content-Type': 'application/json'}
            )
            print(f"登录状态码: {response.status_code}")
            
            if response.status_code == 200:
                login_result = response.json()
                access_token = login_result.get('access_token')
                print(f"登录成功，获取到token: {access_token[:20]}...")
                
                # 设置认证头
                auth_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                }
                
            else:
                print(f"登录失败: {response.text}")
                return
                
        except Exception as e:
            print(f"登录异常: {e}")
            return
        
        # 2. 获取当前用户信息
        print("\n2. 获取当前用户信息")
        try:
            response = requests.get(f"{base_url}/api/v1/auth/me", headers=auth_headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"当前用户信息:")
                print(f"  - 用户ID: {user_data.get('id')}")
                print(f"  - 用户名: {user_data.get('username')}")
                print(f"  - 邮箱: {user_data.get('email')}")
                print(f"  - 角色: {user_data.get('role')}")
                
                profile = user_data.get('profile', {})
                print(f"  - 姓名: {profile.get('name', '未设置')}")
                print(f"  - 手机号: {profile.get('phone', '未设置')}")
                print(f"  - 职位: {profile.get('position', '未设置')}")
                print(f"  - 部门: {profile.get('department', '未设置')}")
                print(f"  - 个人简介: {profile.get('bio', '未设置')}")
            else:
                print(f"获取用户信息失败: {response.text}")
                return
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            return
        
        # 3. 更新用户信息
        print("\n3. 更新用户信息")
        try:
            response = requests.put(
                f"{base_url}/api/v1/auth/me",
                json=test_user_data,
                headers=auth_headers
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"更新结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                print("✅ 用户信息更新成功！")
            else:
                print(f"更新用户信息失败: {response.text}")
                return
        except Exception as e:
            print(f"更新用户信息异常: {e}")
            return
        
        # 4. 验证更新结果
        print("\n4. 验证更新结果")
        try:
            response = requests.get(f"{base_url}/api/v1/auth/me", headers=auth_headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"更新后用户信息:")
                
                profile = user_data.get('profile', {})
                print(f"  - 姓名: {profile.get('name', '未设置')}")
                print(f"  - 手机号: {profile.get('phone', '未设置')}")
                print(f"  - 职位: {profile.get('position', '未设置')}")
                print(f"  - 部门: {profile.get('department', '未设置')}")
                print(f"  - 个人简介: {profile.get('bio', '未设置')}")
                
                # 验证更新是否成功
                if (profile.get('name') == test_user_data['name'] and
                    profile.get('phone') == test_user_data['phone'] and
                    profile.get('position') == test_user_data['position']):
                    print("\n✅ 用户信息更新验证成功！")
                else:
                    print("\n❌ 用户信息更新验证失败！数据未正确更新")
            else:
                print(f"验证更新结果失败: {response.text}")
        except Exception as e:
            print(f"验证更新结果异常: {e}")
        
        # 5. 获取租户信息
        print("\n5. 获取租户信息")
        try:
            response = requests.get(f"{base_url}/api/v1/auth/tenant", headers=auth_headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                tenant_data = response.json()
                print(f"租户信息:")
                print(f"  - 租户ID: {tenant_data.get('data', {}).get('id')}")
                print(f"  - 租户名称: {tenant_data.get('data', {}).get('name')}")
                print(f"  - 行业类型: {tenant_data.get('data', {}).get('settings', {}).get('industry_type')}")
                print(f"  - 企业规模: {tenant_data.get('data', {}).get('settings', {}).get('company_size')}")
            else:
                print(f"获取租户信息失败: {response.text}")
        except Exception as e:
            print(f"获取租户信息异常: {e}")
        
        # 6. 测试租户信息更新
        print("\n6. 测试租户信息更新")
        try:
            tenant_update_data = {
                'name': '测试租户名称',
                'industry_type': 'construction',
                'company_size': 'medium'
            }
            
            response = requests.put(
                f"{base_url}/api/v1/auth/tenant",
                json=tenant_update_data,
                headers=auth_headers
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"租户更新结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                print("✅ 租户信息更新成功！")
            else:
                print(f"租户信息更新失败: {response.text}")
        except Exception as e:
            print(f"租户信息更新异常: {e}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_user_flow())
