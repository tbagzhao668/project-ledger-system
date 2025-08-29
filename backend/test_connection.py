#!/usr/bin/env python3
"""
测试数据库连接的脚本
"""
import asyncio
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_database_connection():
    """测试数据库连接"""
    try:
        print("开始测试数据库连接...")
        
        # 导入配置
        from app.config import settings
        print(f"数据库URL: {settings.DATABASE_URL}")
        
        # 导入数据库管理器
        from app.core.database import db_manager
        print("数据库管理器导入成功")
        
        # 初始化数据库连接
        print("初始化数据库连接...")
        await db_manager.initialize()
        print("✅ 数据库连接初始化成功")
        
        # 测试获取会话
        print("测试获取数据库会话...")
        async for session in db_manager.get_session():
            print("✅ 数据库会话获取成功")
            break
        
        # 关闭连接
        await db_manager.close()
        print("✅ 数据库连接关闭成功")
        
        print("🎉 所有数据库测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
