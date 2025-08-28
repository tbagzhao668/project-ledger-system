#!/usr/bin/env python3
"""
检查数据库中的用户数据
"""
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor

def check_users():
    """检查用户数据"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='project_ledger'
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 检查用户表
            cur.execute("SELECT id, username, email, role, created_at FROM users LIMIT 5;")
            users = cur.fetchall()
            
            print(f"找到 {len(users)} 个用户:")
            for user in users:
                print(f"  - ID: {user['id']}")
                print(f"    用户名: {user['username']}")
                print(f"    邮箱: {user['email']}")
                print(f"    角色: {user['role']}")
                print(f"    创建时间: {user['created_at']}")
                print()
            
            # 检查租户表
            cur.execute("SELECT id, name, domain, status FROM tenants LIMIT 5;")
            tenants = cur.fetchall()
            
            print(f"找到 {len(tenants)} 个租户:")
            for tenant in tenants:
                print(f"  - ID: {tenant['id']}")
                print(f"    名称: {tenant['name']}")
                print(f"    域名: {tenant['domain']}")
                print(f"    状态: {tenant['status']}")
                print()
                
    except Exception as e:
        print(f"错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_users()
