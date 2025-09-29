"""
预览API路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Blob, Asset
from app.services.preview_service import PreviewService
from typing import Optional
import os

router = APIRouter()
preview_service = PreviewService()

@router.get("/{content_hash}")
async def get_preview(
    content_hash: str,
    size: str = "medium",
    db: Session = Depends(get_db)
):
    """获取文件预览"""
    try:
        # 检查文件是否存在
        blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
        if not blob:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 获取文件路径
        asset = db.query(Asset).filter(
            Asset.content_hash == content_hash,
            Asset.is_available == True
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="文件路径不存在")
        
        file_path = asset.full_path
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在于磁盘")
        
        # 检查预览是否已缓存
        if preview_service.is_preview_cached(content_hash, size):
            preview_path = preview_service.get_preview_path(content_hash, size)
            return FileResponse(
                str(preview_path),
                media_type="image/jpeg",
                filename=f"preview_{content_hash}_{size}.jpg"
            )
        
        # 生成预览
        result = await preview_service.generate_preview(content_hash, file_path, size)
        
        if result['success']:
            preview_path = preview_service.get_preview_path(content_hash, size)
            return FileResponse(
                str(preview_path),
                media_type="image/jpeg",
                filename=f"preview_{content_hash}_{size}.jpg"
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', '预览生成失败'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/{content_hash}")
async def generate_preview(
    content_hash: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """生成文件预览"""
    try:
        # 检查文件是否存在
        blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
        if not blob:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 获取文件路径
        asset = db.query(Asset).filter(
            Asset.content_hash == content_hash,
            Asset.is_available == True
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="文件路径不存在")
        
        file_path = asset.full_path
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在于磁盘")
        
        # 在后台生成预览
        background_tasks.add_task(
            generate_preview_task,
            content_hash,
            file_path
        )
        
        return {
            "message": f"预览生成任务已启动: {content_hash}",
            "content_hash": content_hash,
            "status": "generating"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_preview_task(content_hash: str, file_path: str):
    """生成预览任务"""
    try:
        # 生成不同尺寸的预览
        for size in ['small', 'medium', 'large', 'thumbnail']:
            await preview_service.generate_preview(content_hash, file_path, size)
    except Exception as e:
        print(f"生成预览任务失败: {content_hash}, 错误: {e}")

@router.get("/info/{content_hash}")
async def get_preview_info(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """获取预览信息"""
    try:
        # 检查文件是否存在
        blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
        if not blob:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 获取预览信息
        result = await preview_service.get_preview_info(content_hash)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('error', '获取预览信息失败'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{content_hash}")
async def delete_preview(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """删除预览"""
    try:
        # 检查文件是否存在
        blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
        if not blob:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 删除预览文件
        preview_dir = preview_service.cache_dir / content_hash
        if preview_dir.exists():
            import shutil
            shutil.rmtree(preview_dir)
        
        return {
            "message": f"预览已删除: {content_hash}",
            "content_hash": content_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_preview_cache():
    """清理预览缓存"""
    try:
        result = await preview_service.cleanup_cache()
        
        if result['success']:
            return {
                "message": "缓存清理完成",
                "cleaned_directories": result['cleaned_directories'],
                "total_size": result['total_size']
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', '缓存清理失败'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
