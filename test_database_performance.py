#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库性能测试脚本
用于测试数据库查询性能、连接池和并发处理能力
"""

import psycopg2
import time
import threading
import statistics
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'fince_project_prod',
    'user': 'fince_app_project',
    'password': 'postgres',
    'port': 5432
}

def connect_database() -> psycopg2.extensions.connection:
    """连接数据库"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def test_simple_query_performance(conn: psycopg2.extensions.connection, iterations: int = 100) -> Dict:
    """测试简单查询性能"""
    print(f"\n🔍 测试简单查询性能 ({iterations} 次迭代)...")
    
    cursor = conn.cursor()
    times = []
    
    for i in range(iterations):
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables;")
        cursor.fetchone()
        end_time = time.time()
        times.append((end_time - start_time) * 1000)  # 转换为毫秒
    
    cursor.close()
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"   📊 平均查询时间: {avg_time:.2f}ms")
    print(f"   📊 最快查询时间: {min_time:.2f}ms")
    print(f"   📊 最慢查询时间: {max_time:.2f}ms")
    print(f"   📊 标准差: {std_dev:.2f}ms")
    
    return {
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'std_dev': std_dev,
        'times': times
    }

def test_complex_query_performance(conn: psycopg2.extensions.connection, iterations: int = 50) -> Dict:
    """测试复杂查询性能"""
    print(f"\n🔍 测试复杂查询性能 ({iterations} 次迭代)...")
    
    cursor = conn.cursor()
    times = []
    
    # 复杂的JOIN查询
    complex_query = """
    SELECT 
        p.name as project_name,
        p.status,
        COUNT(t.id) as transaction_count,
        SUM(t.amount) as total_amount
    FROM projects p
    LEFT JOIN transactions t ON p.id = t.project_id
    GROUP BY p.id, p.name, p.status
    ORDER BY total_amount DESC
    LIMIT 10;
    """
    
    for i in range(iterations):
        start_time = time.time()
        cursor.execute(complex_query)
        cursor.fetchall()
        end_time = time.time()
        times.append((end_time - start_time) * 1000)
    
    cursor.close()
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"   📊 平均查询时间: {avg_time:.2f}ms")
    print(f"   📊 最快查询时间: {min_time:.2f}ms")
    print(f"   📊 最慢查询时间: {max_time:.2f}ms")
    print(f"   📊 标准差: {std_dev:.2f}ms")
    
    return {
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'std_dev': std_dev,
        'times': times
    }

def test_insert_performance(conn: psycopg2.extensions.connection, iterations: int = 100) -> Dict:
    """测试插入性能"""
    print(f"\n🔍 测试插入性能 ({iterations} 次迭代)...")
    
    cursor = conn.cursor()
    times = []
    
    # 创建临时表进行测试
    cursor.execute("""
        CREATE TEMP TABLE performance_test (
            id SERIAL PRIMARY KEY,
            name TEXT,
            value INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    for i in range(iterations):
        start_time = time.time()
        cursor.execute("""
            INSERT INTO performance_test (name, value) 
            VALUES (%s, %s);
        """, (f"test_{i}", i))
        end_time = time.time()
        times.append((end_time - start_time) * 1000)
    
    # 清理临时表
    cursor.execute("DROP TABLE performance_test;")
    conn.commit()
    cursor.close()
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"   📊 平均插入时间: {avg_time:.2f}ms")
    print(f"   📊 最快插入时间: {min_time:.2f}ms")
    print(f"   📊 最慢插入时间: {max_time:.2f}ms")
    print(f"   📊 标准差: {std_dev:.2f}ms")
    
    return {
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'std_dev': std_dev,
        'times': times
    }

def test_concurrent_connections(max_connections: int = 10) -> Dict:
    """测试并发连接性能"""
    print(f"\n🔍 测试并发连接性能 (最大 {max_connections} 个连接)...")
    
    def test_single_connection(conn_id: int) -> Tuple[int, float, bool]:
        """测试单个连接"""
        start_time = time.time()
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.fetchone()
            cursor.close()
            conn.close()
            end_time = time.time()
            return conn_id, (end_time - start_time) * 1000, True
        except Exception as e:
            end_time = time.time()
            return conn_id, (end_time - start_time) * 1000, False
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_connections) as executor:
        futures = [executor.submit(test_single_connection, i) for i in range(max_connections)]
        results = []
        
        for future in as_completed(futures):
            conn_id, duration, success = future.result()
            results.append((conn_id, duration, success))
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    
    successful_connections = sum(1 for _, _, success in results if success)
    failed_connections = max_connections - successful_connections
    
    if successful_connections > 0:
        successful_times = [duration for _, duration, success in results if success]
        avg_time = statistics.mean(successful_times)
        min_time = min(successful_times)
        max_time = max(successful_times)
    else:
        avg_time = min_time = max_time = 0
    
    print(f"   📊 总耗时: {total_time:.2f}ms")
    print(f"   📊 成功连接: {successful_connections}/{max_connections}")
    print(f"   📊 失败连接: {failed_connections}/{max_connections}")
    if successful_connections > 0:
        print(f"   📊 平均连接时间: {avg_time:.2f}ms")
        print(f"   📊 最快连接时间: {min_time:.2f}ms")
        print(f"   📊 最慢连接时间: {max_time:.2f}ms")
    
    return {
        'total_time': total_time,
        'successful_connections': successful_connections,
        'failed_connections': failed_connections,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time
    }

def test_database_size(conn: psycopg2.extensions.connection) -> Dict:
    """测试数据库大小和统计信息"""
    print(f"\n🔍 测试数据库大小和统计信息...")
    
    cursor = conn.cursor()
    
    # 获取数据库大小
    cursor.execute("""
        SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;
    """)
    db_size = cursor.fetchone()[0]
    
    # 获取表数量
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    table_count = cursor.fetchone()[0]
    
    # 获取各表的大小
    cursor.execute("""
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    """)
    table_sizes = cursor.fetchall()
    
    cursor.close()
    
    print(f"   📊 数据库大小: {db_size}")
    print(f"   📊 表数量: {table_count}")
    print(f"   📊 各表大小:")
    for schema, table, size in table_sizes:
        print(f"      - {table}: {size}")
    
    return {
        'db_size': db_size,
        'table_count': table_count,
        'table_sizes': table_sizes
    }

def main():
    """主函数"""
    print("=== 数据库性能测试脚本 ===")
    print("测试数据库查询性能、连接池和并发处理能力")
    
    # 连接数据库
    conn = connect_database()
    if not conn:
        return
    
    try:
        # 测试简单查询性能
        simple_query_result = test_simple_query_performance(conn)
        
        # 测试复杂查询性能
        complex_query_result = test_complex_query_performance(conn)
        
        # 测试插入性能
        insert_result = test_insert_performance(conn)
        
        # 测试并发连接
        concurrent_result = test_concurrent_connections()
        
        # 测试数据库大小
        size_result = test_database_size(conn)
        
        # 输出性能评估
        print("\n" + "="*50)
        print("📋 性能评估结果:")
        
        # 简单查询性能评估
        if simple_query_result['avg_time'] < 1:
            print("✅ 简单查询性能: 优秀 (< 1ms)")
        elif simple_query_result['avg_time'] < 5:
            print("✅ 简单查询性能: 良好 (1-5ms)")
        elif simple_query_result['avg_time'] < 10:
            print("⚠️  简单查询性能: 一般 (5-10ms)")
        else:
            print("❌ 简单查询性能: 较差 (> 10ms)")
        
        # 复杂查询性能评估
        if complex_query_result['avg_time'] < 10:
            print("✅ 复杂查询性能: 优秀 (< 10ms)")
        elif complex_query_result['avg_time'] < 50:
            print("✅ 复杂查询性能: 良好 (10-50ms)")
        elif complex_query_result['avg_time'] < 100:
            print("⚠️  复杂查询性能: 一般 (50-100ms)")
        else:
            print("❌ 复杂查询性能: 较差 (> 100ms)")
        
        # 插入性能评估
        if insert_result['avg_time'] < 5:
            print("✅ 插入性能: 优秀 (< 5ms)")
        elif insert_result['avg_time'] < 20:
            print("✅ 插入性能: 良好 (5-20ms)")
        elif insert_result['avg_time'] < 50:
            print("⚠️  插入性能: 一般 (20-50ms)")
        else:
            print("❌ 插入性能: 较差 (> 50ms)")
        
        # 并发性能评估
        if concurrent_result['successful_connections'] == concurrent_result['successful_connections'] + concurrent_result['failed_connections']:
            print("✅ 并发连接性能: 优秀 (100% 成功)")
        elif concurrent_result['successful_connections'] / (concurrent_result['successful_connections'] + concurrent_result['failed_connections']) > 0.8:
            print("✅ 并发连接性能: 良好 (> 80% 成功)")
        elif concurrent_result['successful_connections'] / (concurrent_result['successful_connections'] + concurrent_result['failed_connections']) > 0.5:
            print("⚠️  并发连接性能: 一般 (50-80% 成功)")
        else:
            print("❌ 并发连接性能: 较差 (< 50% 成功)")
        
        print(f"\n💡 性能优化建议:")
        if simple_query_result['avg_time'] > 5:
            print("   - 考虑添加数据库索引")
        if complex_query_result['avg_time'] > 50:
            print("   - 优化复杂查询SQL")
        if insert_result['avg_time'] > 20:
            print("   - 考虑批量插入操作")
        if concurrent_result['failed_connections'] > 0:
            print("   - 检查数据库连接池配置")
        
    finally:
        conn.close()
        print("\n🔌 数据库连接已关闭")

if __name__ == "__main__":
    main()
