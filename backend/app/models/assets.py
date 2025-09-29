"""
位置实体模型 - Assets表
存储文件的物理位置信息
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Asset(Base):
    __tablename__ = "assets"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键：内容哈希
    content_hash = Column(String(64), ForeignKey("blobs.content_hash"), nullable=False, index=True)
    
    # 完整路径
    full_path = Column(String(4096), nullable=False, comment="完整文件路径")
    
    # 卷ID（用于跨卷管理）
    volume_id = Column(String(100), nullable=True, index=True, comment="卷标识符")
    
    # 跨平台字段：inode/device_id
    inode = Column(String(50), nullable=True, comment="inode号")
    device_id = Column(String(50), nullable=True, comment="设备ID")
    
    # 首次发现时间
    first_seen = Column(DateTime(timezone=True), server_default=func.now(), comment="首次发现时间")
    
    # 最后发现时间
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), comment="最后发现时间")
    
    # 是否可用
    is_available = Column(Boolean, default=True, index=True, comment="文件是否可用")
    
    # 关系
    blob = relationship("Blob", back_populates="assets")
    
    # 索引
    __table_args__ = (
        Index('idx_assets_path', 'full_path'),
        Index('idx_assets_volume', 'volume_id'),
        Index('idx_assets_available', 'is_available'),
        Index('idx_assets_last_seen', 'last_seen'),
    )
    
    def __repr__(self):
        return f"<Asset(id={self.id}, path={self.full_path}, available={self.is_available})>"
