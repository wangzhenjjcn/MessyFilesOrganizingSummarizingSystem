"""
容器文件API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blobs import Blob
from app.models.assets import Asset
from app.services.container_service import ContainerService
from typing import List, Optional, Dict, Any

router = APIRouter()
container_service = ContainerService()

@router.get("/")
async def list_containers():
    """获取所有容器列表"""
    try:
        containers = container_service.list_containers()
        return {
            "containers": containers,
            "count": len(containers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_hash}")
async def get_container_info(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """获取容器信息"""
    try:
        result = container_service.get_container_info(content_hash)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{content_hash}/extract")
async def extract_container(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """提取容器文件"""
    try:
        # 获取文件路径
        asset = db.query(Asset).filter(
            Asset.content_hash == content_hash,
            Asset.is_available == True
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 提取容器
        result = container_service.extract_container(content_hash, asset.full_path)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{content_hash}/extract-file")
async def extract_container_file(
    content_hash: str,
    file_path: str = Body(..., description="容器内文件路径"),
    target_path: str = Body(..., description="目标路径"),
    db: Session = Depends(get_db)
):
    """提取容器中的特定文件"""
    try:
        result = container_service.extract_container_file(content_hash, file_path, target_path)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{content_hash}")
async def delete_container(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """删除容器信息"""
    try:
        result = container_service.delete_container(content_hash)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_hash}/files")
async def list_container_files(
    content_hash: str,
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    offset: int = Query(0, ge=0, description="跳过数量"),
    db: Session = Depends(get_db)
):
    """获取容器文件列表"""
    try:
        result = container_service.get_container_info(content_hash)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        files = result['files']
        total = len(files)
        
        # 分页
        files = files[offset:offset + limit]
        
        return {
            "files": files,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_hash}/search")
async def search_container_files(
    content_hash: str,
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    db: Session = Depends(get_db)
):
    """搜索容器文件"""
    try:
        result = container_service.get_container_info(content_hash)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        files = result['files']
        
        # 搜索过滤
        if query:
            filtered_files = []
            for file_info in files:
                if query.lower() in file_info['path'].lower():
                    filtered_files.append(file_info)
            files = filtered_files
        
        total = len(files)
        
        # 分页
        files = files[:limit]
        
        return {
            "files": files,
            "total": total,
            "query": query,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{content_hash}/refresh")
async def refresh_container(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """刷新容器信息"""
    try:
        # 获取文件路径
        asset = db.query(Asset).filter(
            Asset.content_hash == content_hash,
            Asset.is_available == True
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 重新提取容器
        result = container_service.extract_container(content_hash, asset.full_path)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "message": f"容器信息已刷新: {content_hash}",
            "total_files": result['total_files']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
