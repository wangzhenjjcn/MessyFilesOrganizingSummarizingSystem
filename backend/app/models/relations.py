"""
关系模型 - Relations表
存储文件间和文件-实体间的关系
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Relation(Base):
    __tablename__ = "relations"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 源内容哈希
    src_content_hash = Column(String(64), nullable=False, index=True, comment="源内容哈希")
    
    # 目标内容哈希或实体ID
    dst_content_hash = Column(String(64), nullable=True, index=True, comment="目标内容哈希")
    dst_entity_id = Column(Integer, nullable=True, index=True, comment="目标实体ID")
    
    # 关系类型
    rel_type = Column(String(50), nullable=False, index=True, comment="关系类型")
    
    # 关系得分/权重
    score = Column(Float, nullable=False, default=1.0, comment="关系得分")
    
    # 关系来源（inferred, manual, rule等）
    source = Column(String(50), nullable=False, default="inferred", comment="关系来源")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 索引
    __table_args__ = (
        Index('idx_relations_src', 'src_content_hash'),
        Index('idx_relations_dst', 'dst_content_hash'),
        Index('idx_relations_type', 'rel_type'),
        Index('idx_relations_source', 'source'),
    )
    
    def __repr__(self):
        return f"<Relation(id={self.id}, type={self.rel_type}, src={self.src_content_hash[:8]}...)>"
