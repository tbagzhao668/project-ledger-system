#!/usr/bin/env python3
"""
调试项目列表显示问题
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://192.168.1.215:8000"
API_BASE = f"{BASE_URL}/api/v1"

def debug_project_list():
    """调试项目列表问题"""
    print("🔍 调试项目列表显示问题...")
    print("=" * 50)
    
    # 1. 检查健康状态
    print("1. 检查API健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   - 健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API服务正常")
        else:
            print("   ❌ API服务异常")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
    
    print()
    
    # 2. 检查项目统计（不需要认证）
    print("2. 检查项目统计...")
    try:
        response = requests.get(f"{API_BASE}/projects/statistics/overview")
        print(f"   - 统计API状态码: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 总项目数: {stats.get('total_projects', 0)}")
            print(f"   ✅ 活跃项目数: {stats.get('active_projects', 0)}")
            print(f"   ✅ 已完成项目数: {stats.get('completed_projects', 0)}")
            print(f"   ✅ 项目状态分布: {stats.get('projects_by_status', {})}")
            print(f"   ✅ 项目类型分布: {stats.get('projects_by_type', {})}")
        else:
            print(f"   ❌ 统计API失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 统计API请求失败: {e}")
    
    print()
    
    # 3. 检查项目列表（不需要认证）
    print("3. 检查项目列表...")
    try:
        # 测试不同的查询参数
        test_params = [
            {},  # 无参数
            {"page": 1, "per_page": 20},  # 基础分页
            {"status": "active"},  # 活跃状态
            {"project_type": "industrial"},  # 工业类型
            {"search": "测试"},  # 搜索关键词
        ]
        
        for i, params in enumerate(test_params, 1):
            print(f"   - 测试参数 {i}: {params}")
            response = requests.get(f"{API_BASE}/projects/", params=params)
            print(f"     - 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"     - 总数: {data.get('total', 0)}")
                print(f"     - 当前页: {data.get('page', 0)}")
                print(f"     - 每页数量: {data.get('per_page', 0)}")
                print(f"     - 总页数: {data.get('pages', 0)}")
                print(f"     - 项目数量: {len(data.get('projects', []))}")
                
                if data.get('projects'):
                    print(f"     - 第一个项目: {data['projects'][0].get('name', 'N/A')}")
            else:
                print(f"     - 错误: {response.text[:200]}")
            
            print()
            
    except Exception as e:
        print(f"   ❌ 项目列表请求失败: {e}")
    
    print()
    
    # 4. 检查OpenAPI文档
    print("4. 检查API文档...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            
            # 检查项目列表端点
            projects_path = "/api/v1/projects/"
            if projects_path in openapi_data.get("paths", {}):
                print(f"   ✅ 项目列表端点已注册: {projects_path}")
                
                # 检查参数
                get_method = openapi_data["paths"][projects_path].get("get", {})
                parameters = get_method.get("parameters", [])
                print(f"   ✅ 支持 {len(parameters)} 个查询参数:")
                for param in parameters:
                    print(f"     - {param.get('name')}: {param.get('description', 'N/A')}")
            else:
                print(f"   ❌ 项目列表端点未找到: {projects_path}")
        else:
            print(f"   ❌ 无法获取OpenAPI文档: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 检查API文档失败: {e}")
    
    print()
    
    # 5. 分析问题
    print("5. 问题分析...")
    print("   📋 可能的原因:")
    print("   - 租户ID不匹配")
    print("   - 查询参数格式错误")
    print("   - 数据库权限问题")
    print("   - 前端传递的参数有问题")
    print("   - 后端查询逻辑有bug")
    
    print()
    print("🎯 建议解决方案:")
    print("1. 检查前端传递的查询参数")
    print("2. 检查用户认证和租户ID")
    print("3. 检查数据库中的项目数据")
    print("4. 检查后端查询逻辑")

def main():
    """主函数"""
    print("🚀 开始调试项目列表问题")
    print("=" * 60)
    
    debug_project_list()
    
    print("🎉 调试完成!")
    print("\n📝 请根据上述信息分析问题原因")

if __name__ == "__main__":
    main()
