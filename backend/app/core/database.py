"""
数据库连接和配置
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
    
    async def initialize(self):
        """初始化数据库连接"""
        if self.engine is None:
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
                poolclass=NullPool,  # 使用NullPool避免连接池问题
                future=True
            )
            
            self.session_maker = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
    
    async def get_session(self):
        """获取数据库会话"""
        if self.session_maker is None:
            await self.initialize()
        
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"数据库会话错误: {e}")
                raise
            finally:
                await session.close()
    
    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

async def get_db() -> AsyncSession:
    """FastAPI依赖函数：获取数据库会话"""
    async for session in db_manager.get_session():
        yield session
