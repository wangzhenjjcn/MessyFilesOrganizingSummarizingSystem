"""
业务实体模型 - Entities表
存储项目、客户、剧集、专辑等业务实体
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Entity(Base):
    __tablename__ = "entities"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 实体类型（project, client, series, album等）
    type = Column(String(50), nullable=False, index=True, comment="实体类型")
    
    # 实体名称
    name = Column(String(255), nullable=False, comment="实体名称")
    
    # 元数据JSON
    meta_json = Column(Text, nullable=True, comment="实体元数据JSON")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index('idx_entities_type', 'type'),
        Index('idx_entities_name', 'name'),
    )
    
    def __repr__(self):
        return f"<Entity(id={self.id}, type={self.type}, name={self.name})>"
