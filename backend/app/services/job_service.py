"""
任务服务
"""
import json
import time
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Job
import logging

logger = logging.getLogger(__name__)

class JobService:
    """任务管理服务"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_job(self, kind: str, payload: Dict, priority: int = 0) -> Job:
        """创建新任务"""
        try:
            job = Job(
                kind=kind,
                payload_json=json.dumps(payload),
                status="pending"
            )
            self.db.add(job)
            self.db.commit()
            
            logger.info(f"创建任务: {job.id}, 类型: {kind}")
            return job
            
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            self.db.rollback()
            raise
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """获取任务"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def get_pending_jobs(self, kind: str = None, limit: int = 10) -> List[Job]:
        """获取待处理任务"""
        query = self.db.query(Job).filter(Job.status == "pending")
        
        if kind:
            query = query.filter(Job.kind == kind)
        
        return query.limit(limit).all()
    
    def start_job(self, job_id: int) -> bool:
        """开始执行任务"""
        try:
            job = self.get_job(job_id)
            if not job or job.status != "pending":
                return False
            
            job.status = "running"
            job.updated_at = time.time()
            self.db.commit()
            
            logger.info(f"开始执行任务: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"开始任务失败: {job_id}, 错误: {e}")
            self.db.rollback()
            return False
    
    def complete_job(self, job_id: int, result: Dict = None) -> bool:
        """完成任务"""
        try:
            job = self.get_job(job_id)
            if not job or job.status != "running":
                return False
            
            job.status = "completed"
            job.updated_at = time.time()
            
            if result:
                # 将结果添加到载荷中
                payload = json.loads(job.payload_json)
                payload['result'] = result
                job.payload_json = json.dumps(payload)
            
            self.db.commit()
            
            logger.info(f"完成任务: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"完成任务失败: {job_id}, 错误: {e}")
            self.db.rollback()
            return False
    
    def fail_job(self, job_id: int, error: str, max_attempts: int = 3) -> bool:
        """任务失败"""
        try:
            job = self.get_job(job_id)
            if not job:
                return False
            
            job.attempts += 1
            job.last_error = error
            job.updated_at = time.time()
            
            if job.attempts >= max_attempts:
                job.status = "failed"
                logger.error(f"任务失败，达到最大重试次数: {job_id}")
            else:
                job.status = "pending"  # 重新排队
                logger.warning(f"任务失败，将重试: {job_id}, 尝试次数: {job.attempts}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"处理任务失败: {job_id}, 错误: {e}")
            self.db.rollback()
            return False
    
    def get_job_stats(self) -> Dict:
        """获取任务统计信息"""
        try:
            total = self.db.query(Job).count()
            pending = self.db.query(Job).filter(Job.status == "pending").count()
            running = self.db.query(Job).filter(Job.status == "running").count()
            completed = self.db.query(Job).filter(Job.status == "completed").count()
            failed = self.db.query(Job).filter(Job.status == "failed").count()
            
            return {
                'total': total,
                'pending': pending,
                'running': running,
                'completed': completed,
                'failed': failed
            }
            
        except Exception as e:
            logger.error(f"获取任务统计失败: {e}")
            return {}
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """清理旧任务"""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            old_jobs = self.db.query(Job).filter(
                Job.status.in_(["completed", "failed"]),
                Job.updated_at < cutoff_time
            ).all()
            
            count = len(old_jobs)
            for job in old_jobs:
                self.db.delete(job)
            
            self.db.commit()
            
            logger.info(f"清理了 {count} 个旧任务")
            return count
            
        except Exception as e:
            logger.error(f"清理旧任务失败: {e}")
            self.db.rollback()
            return 0
