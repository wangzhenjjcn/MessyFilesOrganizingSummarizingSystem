"""
预览API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Blob
from typing import Optional

router = APIRouter()

@router.get("/{content_hash}")
async def get_preview(
    content_hash: str,
    size: str = "medium",
    db: Session = Depends(get_db)
):
    """获取文件预览"""
    blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
    if not blob:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # TODO: 实现预览生成逻辑
    return {
        "content_hash": content_hash,
        "preview_url": f"/preview/{content_hash}/{size}",
        "status": "generating"
    }

@router.post("/generate/{content_hash}")
async def generate_preview(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """生成文件预览"""
    # TODO: 实现预览生成任务
    return {"message": f"开始生成预览: {content_hash}"}
