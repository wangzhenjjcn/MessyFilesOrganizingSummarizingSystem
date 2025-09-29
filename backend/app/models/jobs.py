"""
任务队列模型 - Jobs表
存储后台任务和队列管理
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 任务类型（scan, hash, extract, preview等）
    kind = Column(String(50), nullable=False, index=True, comment="任务类型")
    
    # 任务载荷（JSON格式）
    payload_json = Column(Text, nullable=False, comment="任务载荷JSON")
    
    # 任务状态（pending, running, completed, failed）
    status = Column(String(20), nullable=False, default="pending", index=True, comment="任务状态")
    
    # 重试次数
    attempts = Column(Integer, nullable=False, default=0, comment="重试次数")
    
    # 最后错误信息
    last_error = Column(Text, nullable=True, comment="最后错误信息")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index('idx_jobs_kind', 'kind'),
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Job(id={self.id}, kind={self.kind}, status={self.status})>"
