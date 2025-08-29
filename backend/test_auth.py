#!/usr/bin/env python3
"""
测试认证API响应
"""
import requests
import json

def test_login():
    """测试登录API"""
    url = "http://localhost:8000/api/v1/auth/login"
    
    # 测试登录数据
    login_data = {
        "email": "123@123.com",
        "password": "123123",
        "remember_me": False
    }
    
    try:
        response = requests.post(url, json=login_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("登录成功!")
            print(f"访问令牌: {data['access_token'][:50]}...")
            print(f"刷新令牌: {data['refresh_token'][:50]}...")
            print(f"令牌类型: {data['token_type']}")
            print(f"过期时间: {data['expires_in']} 秒")
            
            # 检查用户数据
            if 'user' in data and data['user']:
                user = data['user']
                print(f"\n用户信息:")
                print(f"  ID: {user.get('id')}")
                print(f"  用户名: {user.get('username')}")
                print(f"  邮箱: {user.get('email')}")
                print(f"  角色: {user.get('role')}")
                print(f"  权限: {user.get('permissions')}")
            else:
                print("\n警告: 响应中没有用户数据!")
                
        else:
            print(f"登录失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_login()
