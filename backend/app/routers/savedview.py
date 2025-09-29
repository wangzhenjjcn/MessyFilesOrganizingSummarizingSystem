"""
SavedView API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.saved_views import SavedView
from app.services.savedview_service import SavedViewService
from typing import List, Optional, Dict, Any

router = APIRouter()
savedview_service = SavedViewService()

@router.get("/")
async def list_savedviews():
    """获取所有SavedView列表"""
    try:
        savedviews = savedview_service.list_savedviews()
        return {
            "savedviews": savedviews,
            "count": len(savedviews)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{savedview_id}")
async def get_savedview(
    savedview_id: int,
    db: Session = Depends(get_db)
):
    """获取SavedView详情"""
    try:
        savedview = db.query(SavedView).filter(SavedView.id == savedview_id).first()
        if not savedview:
            raise HTTPException(status_code=404, detail="SavedView不存在")
        
        return {
            "id": savedview.id,
            "name": savedview.name,
            "query_ast": savedview.query_ast_json,
            "layout": savedview.layout_json,
            "created_at": savedview.created_at.isoformat() if savedview.created_at else None,
            "updated_at": savedview.updated_at.isoformat() if savedview.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_savedview(
    name: str = Body(..., description="SavedView名称"),
    query_ast: Dict[str, Any] = Body(..., description="查询AST"),
    layout: Optional[Dict[str, Any]] = Body(None, description="布局配置"),
    db: Session = Depends(get_db)
):
    """创建SavedView"""
    try:
        result = savedview_service.create_savedview(name, query_ast, layout)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{savedview_id}")
async def update_savedview(
    savedview_id: int,
    name: Optional[str] = Body(None, description="SavedView名称"),
    query_ast: Optional[Dict[str, Any]] = Body(None, description="查询AST"),
    layout: Optional[Dict[str, Any]] = Body(None, description="布局配置"),
    db: Session = Depends(get_db)
):
    """更新SavedView"""
    try:
        result = savedview_service.update_savedview(savedview_id, name, query_ast, layout)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{savedview_id}")
async def delete_savedview(
    savedview_id: int,
    db: Session = Depends(get_db)
):
    """删除SavedView"""
    try:
        result = savedview_service.delete_savedview(savedview_id)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{savedview_id}/execute")
async def execute_savedview(
    savedview_id: int,
    limit: int = Query(1000, ge=1, le=10000, description="返回数量"),
    offset: int = Query(0, ge=0, description="跳过数量"),
    db: Session = Depends(get_db)
):
    """执行SavedView查询"""
    try:
        result = savedview_service.execute_savedview(savedview_id, limit, offset)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{savedview_id}/export")
async def export_savedview(
    savedview_id: int,
    export_path: str = Body(..., description="导出路径"),
    db: Session = Depends(get_db)
):
    """导出SavedView为软链接"""
    try:
        result = savedview_service.export_symlinks(savedview_id, export_path)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{savedview_id}/refresh")
async def refresh_savedview(
    savedview_id: int,
    db: Session = Depends(get_db)
):
    """刷新SavedView"""
    try:
        result = savedview_service.refresh_savedview(savedview_id)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{savedview_id}/stats")
async def get_savedview_stats(
    savedview_id: int,
    db: Session = Depends(get_db)
):
    """获取SavedView统计信息"""
    try:
        result = savedview_service.get_savedview_stats(savedview_id)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_query_ast(
    query_ast: Dict[str, Any] = Body(..., description="查询AST")
):
    """验证查询AST"""
    try:
        # 测试解析查询AST
        test_query = savedview_service.parse_query_ast(query_ast)
        
        if not test_query:
            raise HTTPException(status_code=400, detail="无效的查询AST")
        
        return {
            "valid": True,
            "sql_query": test_query,
            "message": "查询AST有效"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
