"""
文件管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blobs import Blob
from app.models.assets import Asset
from app.services.scanner import FileScanner
from app.services.job_service import JobService
from typing import List, Optional
import json

router = APIRouter()
scanner = FileScanner()
job_service = JobService()

@router.get("/")
async def list_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取文件列表"""
    files = db.query(Asset).filter(Asset.is_available == True).offset(skip).limit(limit).all()
    return {"files": files, "total": len(files)}

@router.get("/{content_hash}")
async def get_file_info(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """获取文件详细信息"""
    blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
    if not blob:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    assets = db.query(Asset).filter(Asset.content_hash == content_hash).all()
    
    return {
        "blob": blob,
        "assets": assets
    }

@router.post("/scan")
async def start_scan(
    path: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """开始扫描指定路径"""
    try:
        # 创建扫描任务
        job = job_service.create_job(
            kind="scan",
            payload={"path": path}
        )
        
        # 在后台执行扫描
        background_tasks.add_task(execute_scan_job, job.id, path)
        
        return {
            "message": f"扫描任务已创建",
            "job_id": job.id,
            "path": path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_scan_job(job_id: int, path: str):
    """执行扫描任务"""
    try:
        job_service.start_job(job_id)
        
        # 执行扫描
        result = scanner.scan_path(path)
        
        # 完成任务
        job_service.complete_job(job_id, result)
        
    except Exception as e:
        job_service.fail_job(job_id, str(e))

@router.get("/scan/status")
async def get_scan_status():
    """获取扫描状态"""
    return scanner.get_scan_status()

@router.post("/scan/stop")
async def stop_scan():
    """停止扫描"""
    scanner.stop_scan()
    return {"message": "扫描已停止"}
