"""
容器文件模型 - Containers和Containment表
处理压缩包、镜像等容器文件
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Container(Base):
    __tablename__ = "containers"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 容器类型（zip, 7z, tar, iso等）
    type = Column(String(50), nullable=False, index=True, comment="容器类型")
    
    # 外键：容器文件的内容哈希
    content_hash = Column(String(64), ForeignKey("blobs.content_hash"), nullable=True, index=True)
    
    # 元数据JSON
    meta_json = Column(Text, nullable=True, comment="容器元数据JSON")
    
    # 关系
    blob = relationship("Blob", back_populates="containers")
    containments = relationship("Containment", back_populates="container")
    
    def __repr__(self):
        return f"<Container(id={self.id}, type={self.type})>"

class Containment(Base):
    __tablename__ = "containment"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键：容器ID
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=False, index=True)
    
    # 子文件内容哈希
    child_content_hash = Column(String(64), ForeignKey("blobs.content_hash"), nullable=False, index=True)
    
    # 容器内路径
    path_in_container = Column(String(1024), nullable=False, comment="容器内路径")
    
    # 元数据
    meta = Column(Text, nullable=True, comment="子文件元数据")
    
    # 关系
    container = relationship("Container", back_populates="containments")
    child_blob = relationship("Blob", foreign_keys=[child_content_hash])
    
    # 索引
    __table_args__ = (
        Index('idx_containment_container', 'container_id'),
        Index('idx_containment_child', 'child_content_hash'),
        Index('idx_containment_path', 'path_in_container'),
    )
    
    def __repr__(self):
        return f"<Containment(container_id={self.container_id}, path={self.path_in_container})>"
