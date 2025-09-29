"""
审计模型 - Audits表
记录所有操作和变更
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Audit(Base):
    __tablename__ = "audits"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 操作者
    actor = Column(String(100), nullable=False, comment="操作者")
    
    # 操作类型（create, update, delete, move, rename等）
    action = Column(String(50), nullable=False, index=True, comment="操作类型")
    
    # 操作目标
    target = Column(String(255), nullable=False, comment="操作目标")
    
    # 操作前状态（JSON）
    before_json = Column(Text, nullable=True, comment="操作前状态JSON")
    
    # 操作后状态（JSON）
    after_json = Column(Text, nullable=True, comment="操作后状态JSON")
    
    # 撤销令牌
    undo_token = Column(String(64), nullable=True, unique=True, comment="撤销令牌")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 索引
    __table_args__ = (
        Index('idx_audits_actor', 'actor'),
        Index('idx_audits_action', 'action'),
        Index('idx_audits_created', 'created_at'),
        Index('idx_audits_undo_token', 'undo_token'),
    )
    
    def __repr__(self):
        return f"<Audit(id={self.id}, action={self.action}, actor={self.actor})>"
