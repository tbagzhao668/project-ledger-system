#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库结构检查脚本
用于检查数据库表结构、字段数量和数据类型
"""

import psycopg2
import sys
from typing import Dict, List, Tuple

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'fince_project_prod',
    'user': 'fince_app_project',
    'password': 'postgres',
    'port': 5432
}

# 期望的表结构定义
EXPECTED_TABLES = {
    'tenants': {
        'field_count': 13,
        'required_fields': ['id', 'name', 'domain', 'plan_type', 'status', 'created_at', 'updated_at']
    },
    'users': {
        'field_count': 16,
        'required_fields': ['id', 'tenant_id', 'username', 'email', 'password_hash', 'role', 'is_active', 'created_at', 'updated_at']
    },
    'projects': {
        'field_count': 60,
        'required_fields': ['id', 'tenant_id', 'name', 'project_code', 'status', 'manager_id', 'contract_value', 'created_at', 'updated_at']
    },
    'categories': {
        'field_count': 14,
        'required_fields': ['id', 'tenant_id', 'name', 'is_system', 'is_active', 'sort_order', 'created_at', 'updated_at']
    },
    'suppliers': {
        'field_count': 20,
        'required_fields': ['id', 'tenant_id', 'name', 'code', 'business_scope', 'qualification', 'credit_rating', 'created_at', 'updated_at']
    },
    'transactions': {
        'field_count': 24,
        'required_fields': ['id', 'tenant_id', 'project_id', 'amount', 'type', 'payment_method', 'created_at', 'updated_at']
    }
}

def connect_database() -> psycopg2.extensions.connection:
    """连接数据库"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        sys.exit(1)

def check_table_exists(conn: psycopg2.extensions.connection, table_name: str) -> bool:
    """检查表是否存在"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists

def get_table_structure(conn: psycopg2.extensions.connection, table_name: str) -> List[Tuple]:
    """获取表结构信息"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    columns = cursor.fetchall()
    cursor.close()
    return columns

def check_table_fields(conn: psycopg2.extensions.connection, table_name: str, expected: Dict) -> Dict:
    """检查表字段数量和必需字段"""
    columns = get_table_structure(conn, table_name)
    field_names = [col[0] for col in columns]
    
    result = {
        'table_name': table_name,
        'actual_field_count': len(columns),
        'expected_field_count': expected['field_count'],
        'field_count_match': len(columns) == expected['field_count'],
        'missing_fields': [],
        'extra_fields': [],
        'field_details': columns
    }
    
    # 检查缺失的必需字段
    for required_field in expected['required_fields']:
        if required_field not in field_names:
            result['missing_fields'].append(required_field)
    
    # 检查多余的字段
    for field in field_names:
        if field not in expected['required_fields']:
            result['extra_fields'].append(field)
    
    return result

def print_table_check_result(result: Dict):
    """打印表检查结果"""
    print(f"\n📋 表: {result['table_name']}")
    print(f"   字段数量: {result['actual_field_count']}/{result['expected_field_count']}")
    
    if result['field_count_match']:
        print("   ✅ 字段数量匹配")
    else:
        print("   ❌ 字段数量不匹配")
    
    if result['missing_fields']:
        print(f"   ❌ 缺失字段: {', '.join(result['missing_fields'])}")
    
    if result['extra_fields']:
        print(f"   ⚠️  多余字段: {', '.join(result['extra_fields'])}")
    
    print("   字段详情:")
    for col in result['field_details']:
        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
        default = f" DEFAULT {col[3]}" if col[3] else ""
        print(f"     - {col[0]}: {col[1]} {nullable}{default}")

def check_database_integrity(conn: psycopg2.extensions.connection):
    """检查数据库完整性"""
    print("\n🔍 开始检查数据库完整性...")
    
    all_tables_exist = True
    all_checks_passed = True
    
    for table_name, expected in EXPECTED_TABLES.items():
        print(f"\n检查表: {table_name}")
        
        # 检查表是否存在
        if check_table_exists(conn, table_name):
            print(f"   ✅ 表 {table_name} 存在")
            
            # 检查表结构
            result = check_table_fields(conn, table_name, expected)
            print_table_check_result(result)
            
            # 检查是否有问题
            if not result['field_count_match'] or result['missing_fields']:
                all_checks_passed = False
        else:
            print(f"   ❌ 表 {table_name} 不存在")
            all_tables_exist = False
            all_checks_passed = False
    
    return all_tables_exist, all_checks_passed

def check_data_integrity(conn: psycopg2.extensions.connection):
    """检查数据完整性"""
    print("\n📊 检查数据完整性...")
    
    cursor = conn.cursor()
    
    # 检查各表的记录数量
    for table_name in EXPECTED_TABLES.keys():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} 条记录")
        except Exception as e:
            print(f"   ❌ {table_name}: 查询失败 - {e}")
    
    cursor.close()

def main():
    """主函数"""
    print("=== 数据库结构检查脚本 ===")
    print(f"目标数据库: {DB_CONFIG['database']}")
    print(f"目标用户: {DB_CONFIG['user']}")
    
    # 连接数据库
    conn = connect_database()
    
    try:
        # 检查数据库完整性
        tables_exist, checks_passed = check_database_integrity(conn)
        
        # 检查数据完整性
        check_data_integrity(conn)
        
        # 输出检查结果
        print("\n" + "="*50)
        print("📋 检查结果总结:")
        
        if tables_exist:
            print("✅ 所有必需的表都存在")
        else:
            print("❌ 部分必需的表缺失")
        
        if checks_passed:
            print("✅ 所有表结构检查通过")
        else:
            print("❌ 部分表结构存在问题")
        
        if tables_exist and checks_passed:
            print("\n🎉 数据库结构完全正常！")
        else:
            print("\n⚠️  数据库结构存在问题，请检查上述详细信息")
            print("💡 建议运行: ./deploy.sh fix-schema")
        
    finally:
        conn.close()
        print("\n🔌 数据库连接已关闭")

if __name__ == "__main__":
    main()
