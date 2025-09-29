"""
动态集合模型 - SavedViews表
存储用户保存的查询和视图
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class SavedView(Base):
    __tablename__ = "saved_views"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 视图名称
    name = Column(String(255), nullable=False, comment="视图名称")
    
    # 查询AST（JSON格式）
    query_ast_json = Column(Text, nullable=False, comment="查询AST JSON")
    
    # 布局配置（JSON格式）
    layout_json = Column(Text, nullable=True, comment="布局配置JSON")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index('idx_saved_views_name', 'name'),
        Index('idx_saved_views_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SavedView(id={self.id}, name={self.name})>"
