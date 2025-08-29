"""
基础数据模型
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, UUID
from sqlalchemy.sql import func
import uuid

# 创建基础模型类
Base = declarative_base()

class BaseModel(Base):
    """基础模型类，包含公共字段"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="主键ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def to_dict(self):
        """转换为字典格式"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
