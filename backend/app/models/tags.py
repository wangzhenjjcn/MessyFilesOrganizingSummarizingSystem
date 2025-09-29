"""
标签系统模型 - Tags和FileTags表
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Tag(Base):
    __tablename__ = "tags"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 标签名称
    name = Column(String(100), nullable=False, unique=True, comment="标签名称")
    
    # 标签类型（category, keyword, custom等）
    kind = Column(String(50), nullable=False, default="custom", comment="标签类型")
    
    # 标签颜色（用于UI显示）
    color = Column(String(7), nullable=True, comment="标签颜色（十六进制）")
    
    # 关系
    file_tags = relationship("FileTag", back_populates="tag")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, kind={self.kind})>"

class FileTag(Base):
    __tablename__ = "file_tags"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键：内容哈希
    content_hash = Column(String(64), ForeignKey("blobs.content_hash"), nullable=False, index=True)
    
    # 外键：标签ID
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False, index=True)
    
    # 标签来源（rule, manual, parser等）
    source = Column(String(50), nullable=False, default="manual", comment="标签来源")
    
    # 置信度（0.0-1.0）
    confidence = Column(Float, nullable=False, default=1.0, comment="置信度")
    
    # 关系
    blob = relationship("Blob", back_populates="file_tags")
    tag = relationship("Tag", back_populates="file_tags")
    
    # 索引
    __table_args__ = (
        Index('idx_file_tags_content', 'content_hash'),
        Index('idx_file_tags_tag', 'tag_id'),
        Index('idx_file_tags_source', 'source'),
    )
    
    def __repr__(self):
        return f"<FileTag(content_hash={self.content_hash[:8]}..., tag_id={self.tag_id})>"
