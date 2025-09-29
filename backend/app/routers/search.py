"""
搜索API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Blob, Asset
from app.services.search_service import SearchService
from typing import List, Optional, Dict, Any

router = APIRouter()
search_service = SearchService()

@router.get("/")
async def search_files(
    q: str = Query("", description="搜索关键词"),
    file_type: Optional[str] = Query(None, description="文件类型过滤"),
    min_size: Optional[int] = Query(None, description="最小文件大小"),
    max_size: Optional[int] = Query(None, description="最大文件大小"),
    extension: Optional[str] = Query(None, description="文件扩展名"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    db: Session = Depends(get_db)
):
    """搜索文件"""
    try:
        # 构建过滤器
        filters = {}
        if file_type:
            filters['file_type'] = file_type
        if min_size:
            filters['min_size'] = min_size
        if max_size:
            filters['max_size'] = max_size
        if extension:
            filters['extension'] = f"%.{extension}"
        
        # 执行搜索
        result = search_service.search_files(
            query=q,
            filters=filters,
            limit=limit,
            offset=skip
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{content_hash}")
async def find_similar_files(
    content_hash: str,
    threshold: float = Query(0.8, ge=0.0, le=1.0, description="相似度阈值"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db)
):
    """查找相似文件"""
    try:
        similar_files = search_service.search_similar_files(
            content_hash=content_hash,
            similarity_threshold=threshold
        )
        
        # 限制返回数量
        similar_files = similar_files[:limit]
        
        return {
            "similar_files": similar_files,
            "content_hash": content_hash,
            "threshold": threshold,
            "count": len(similar_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="建议数量")
):
    """获取搜索建议"""
    try:
        suggestions = search_service.get_search_suggestions(q, limit)
        return {
            "suggestions": suggestions,
            "query": q,
            "count": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_hash}")
async def get_file_by_hash(
    content_hash: str,
    db: Session = Depends(get_db)
):
    """根据内容哈希获取文件信息"""
    try:
        file_info = search_service.search_by_content_hash(content_hash)
        if not file_info:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-index")
async def rebuild_search_index():
    """重建搜索索引"""
    try:
        success = search_service.rebuild_fts_index()
        if success:
            return {"message": "搜索索引重建成功"}
        else:
            raise HTTPException(status_code=500, detail="搜索索引重建失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
