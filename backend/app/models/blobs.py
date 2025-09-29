"""
内容实体模型 - Blobs表
存储文件的唯一内容标识
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base

class Blob(Base):
    __tablename__ = "blobs"
    
    # 主键：内容哈希（SHA-256）
    content_hash = Column(String(64), primary_key=True, comment="内容哈希SHA-256")
    
    # 快速哈希（BLAKE3）
    fast_hash = Column(String(64), nullable=False, index=True, comment="快速哈希BLAKE3")
    
    # 文件大小（字节）
    size = Column(Integer, nullable=False, comment="文件大小（字节）")
    
    # MIME类型
    mime = Column(String(255), nullable=True, comment="MIME类型")
    
    # 主要类型（image, video, audio, document, archive, executable等）
    primary_type = Column(String(50), nullable=True, index=True, comment="主要文件类型")
    
    # 感知哈希（图片相似度）
    phash = Column(String(16), nullable=True, index=True, comment="感知哈希")
    
    # 音频指纹
    audio_fingerprint = Column(String(64), nullable=True, index=True, comment="音频指纹")
    
    # 文档指纹
    doc_fingerprint = Column(String(64), nullable=True, index=True, comment="文档指纹")
    
    # 元数据JSON
    meta_json = Column(Text, nullable=True, comment="解析的元数据JSON")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    assets = relationship("Asset", back_populates="blob")
    containers = relationship("Container", back_populates="blob")
    file_tags = relationship("FileTag", back_populates="blob")
    
    # 索引
    __table_args__ = (
        Index('idx_blobs_primary_type_size', 'primary_type', 'size'),
        Index('idx_blobs_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Blob(content_hash={self.content_hash[:8]}..., size={self.size})>"
