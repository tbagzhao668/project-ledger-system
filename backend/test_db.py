#!/usr/bin/env python3
"""
测试数据库连接的脚本
"""
import psycopg2
import os

def test_database():
    """测试数据库连接和查询"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "fince_project_prod"),
            user=os.getenv("DB_USER", "fince_app_project"),
            password=os.getenv("DB_PASSWORD", "Fince_project_5%8*6^9(3#0)")
        )
        
        cur = conn.cursor()
        
        # 测试查询用户表
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        print(f"✅ 用户表查询成功，用户数量: {user_count}")
        
        # 测试查询租户表
        cur.execute("SELECT COUNT(*) FROM tenants")
        tenant_count = cur.fetchone()[0]
        print(f"✅ 租户表查询成功，租户数量: {tenant_count}")
        
        # 测试查询项目表
        cur.execute("SELECT COUNT(*) FROM projects")
        project_count = cur.fetchone()[0]
        print(f"✅ 项目表查询成功，项目数量: {project_count}")
        
        cur.close()
        conn.close()
        
        print("🎉 所有数据库测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

if __name__ == "__main__":
    test_database()
