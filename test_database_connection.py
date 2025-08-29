#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
用于测试数据库连接、权限和基本功能
"""

import psycopg2
import sys
import time
from typing import Dict, List

# 数据库连接配置
DB_CONFIGS = {
    'postgres_user': {
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'postgres',
        'port': 5432
    },
    'fince_app_project': {
        'host': 'localhost',
        'database': 'fince_project_prod',
        'user': 'fince_app_project',
        'password': 'postgres',
        'port': 5432
    }
}

def test_connection(config: Dict, user_name: str) -> bool:
    """测试数据库连接"""
    print(f"\n🔌 测试 {user_name} 用户连接...")
    
    try:
        start_time = time.time()
        conn = psycopg2.connect(**config)
        end_time = time.time()
        
        print(f"   ✅ 连接成功 (耗时: {(end_time - start_time)*1000:.2f}ms)")
        
        # 测试基本查询
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   📊 PostgreSQL版本: {version.split(',')[0]}")
        
        # 测试当前用户
        cursor.execute("SELECT current_user, current_database();")
        current_user, current_db = cursor.fetchone()
        print(f"   👤 当前用户: {current_user}")
        print(f"   🗄️  当前数据库: {current_db}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

def test_database_permissions(config: Dict, user_name: str) -> bool:
    """测试数据库权限"""
    print(f"\n🔐 测试 {user_name} 用户权限...")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # 测试创建临时表
        cursor.execute("CREATE TEMP TABLE test_permissions (id SERIAL, name TEXT);")
        print("   ✅ 可以创建临时表")
        
        # 测试插入数据
        cursor.execute("INSERT INTO test_permissions (name) VALUES ('test');")
        print("   ✅ 可以插入数据")
        
        # 测试查询数据
        cursor.execute("SELECT * FROM test_permissions;")
        result = cursor.fetchone()
        print(f"   ✅ 可以查询数据: {result}")
        
        # 测试更新数据
        cursor.execute("UPDATE test_permissions SET name = 'updated' WHERE id = 1;")
        print("   ✅ 可以更新数据")
        
        # 测试删除数据
        cursor.execute("DELETE FROM test_permissions WHERE id = 1;")
        print("   ✅ 可以删除数据")
        
        # 清理临时表
        cursor.execute("DROP TABLE test_permissions;")
        print("   ✅ 可以删除表")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 权限测试失败: {e}")
        return False

def test_specific_permissions(config: Dict, user_name: str) -> bool:
    """测试特定权限"""
    print(f"\n🔍 测试 {user_name} 特定权限...")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # 测试查看表结构
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            LIMIT 5;
        """)
        tables = cursor.fetchall()
        print(f"   ✅ 可以查看表结构 (示例: {len(tables)} 个字段)")
        
        # 测试查看用户权限
        cursor.execute("""
            SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcanlogin
            FROM pg_roles 
            WHERE rolname = current_user;
        """)
        role_info = cursor.fetchone()
        if role_info:
            print(f"   👤 用户角色信息:")
            print(f"      - 超级用户: {'是' if role_info[1] else '否'}")
            print(f"      - 可创建角色: {'是' if role_info[3] else '否'}")
            print(f"      - 可创建数据库: {'是' if role_info[4] else '否'}")
            print(f"      - 可登录: {'是' if role_info[5] else '否'}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 特定权限测试失败: {e}")
        return False

def test_database_operations(config: Dict, user_name: str) -> bool:
    """测试数据库操作"""
    print(f"\n⚙️  测试 {user_name} 数据库操作...")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # 测试事务
        cursor.execute("BEGIN;")
        print("   ✅ 可以开始事务")
        
        # 测试回滚
        cursor.execute("ROLLBACK;")
        print("   ✅ 可以回滚事务")
        
        # 测试提交
        cursor.execute("BEGIN;")
        cursor.execute("COMMIT;")
        print("   ✅ 可以提交事务")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库操作测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 数据库连接测试脚本 ===")
    print("测试数据库连接、权限和基本功能")
    
    all_tests_passed = True
    
    # 测试postgres用户连接
    if test_connection(DB_CONFIGS['postgres_user'], 'postgres'):
        if test_database_permissions(DB_CONFIGS['postgres_user'], 'postgres'):
            if test_specific_permissions(DB_CONFIGS['postgres_user'], 'postgres'):
                if test_database_operations(DB_CONFIGS['postgres_user'], 'postgres'):
                    print("\n✅ postgres用户所有测试通过")
                else:
                    all_tests_passed = False
            else:
                all_tests_passed = False
        else:
            all_tests_passed = False
    else:
        all_tests_passed = False
    
    # 测试fince_app_project用户连接
    if test_connection(DB_CONFIGS['fince_app_project'], 'fince_app_project'):
        if test_database_permissions(DB_CONFIGS['fince_app_project'], 'fince_app_project'):
            if test_specific_permissions(DB_CONFIGS['fince_app_project'], 'fince_app_project'):
                if test_database_operations(DB_CONFIGS['fince_app_project'], 'fince_app_project'):
                    print("\n✅ fince_app_project用户所有测试通过")
                else:
                    all_tests_passed = False
            else:
                all_tests_passed = False
        else:
            all_tests_passed = False
    else:
        all_tests_passed = False
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📋 测试结果总结:")
    
    if all_tests_passed:
        print("🎉 所有数据库测试通过！")
        print("✅ 数据库连接正常")
        print("✅ 用户权限配置正确")
        print("✅ 基本功能正常")
    else:
        print("❌ 部分测试失败")
        print("💡 建议检查:")
        print("   1. PostgreSQL服务状态")
        print("   2. 数据库用户权限")
        print("   3. 数据库配置")
        print("   4. 网络连接")

if __name__ == "__main__":
    main()
