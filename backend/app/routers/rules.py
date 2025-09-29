"""
规则引擎API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blobs import Blob
from app.models.assets import Asset
from app.services.rules_engine import RulesEngine
from typing import List, Optional, Dict, Any

router = APIRouter()
rules_engine = RulesEngine()

@router.post("/validate")
async def validate_rule(
    rule: Dict[str, Any] = Body(..., description="规则配置")
):
    """验证规则"""
    try:
        result = rules_engine.validate_rule(rule)
        
        if not result['valid']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_rule(
    rule: Dict[str, Any] = Body(..., description="规则配置"),
    file_info: Dict[str, Any] = Body(..., description="测试文件信息")
):
    """测试规则"""
    try:
        # 验证规则
        validation = rules_engine.validate_rule(rule)
        if not validation['valid']:
            raise HTTPException(status_code=400, detail=validation['error'])
        
        # 测试规则
        result = rules_engine.process_file(file_info, [rule])
        
        return {
            "rule_name": rule.get('name', '未命名规则'),
            "matched": result['matched_rules'] > 0,
            "executed_actions": result['executed_actions'],
            "results": result['results']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/{content_hash}")
async def process_file_with_rules(
    content_hash: str,
    rules: List[Dict[str, Any]] = Body(..., description="规则列表"),
    db: Session = Depends(get_db)
):
    """使用规则处理文件"""
    try:
        # 获取文件信息
        blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
        if not blob:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        asset = db.query(Asset).filter(
            Asset.content_hash == content_hash,
            Asset.is_available == True
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="文件路径不存在")
        
        # 构建文件信息
        file_info = {
            'content_hash': blob.content_hash,
            'full_path': asset.full_path,
            'size': blob.size,
            'primary_type': blob.primary_type,
            'mime': blob.mime,
            'created_at': blob.created_at,
            'last_seen': asset.last_seen
        }
        
        # 处理文件
        result = rules_engine.process_file(file_info, rules)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-process")
async def batch_process_files(
    content_hashes: List[str] = Body(..., description="文件哈希列表"),
    rules: List[Dict[str, Any]] = Body(..., description="规则列表"),
    db: Session = Depends(get_db)
):
    """批量处理文件"""
    try:
        results = []
        
        for content_hash in content_hashes:
            try:
                # 获取文件信息
                blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
                if not blob:
                    results.append({
                        'content_hash': content_hash,
                        'success': False,
                        'error': '文件不存在'
                    })
                    continue
                
                asset = db.query(Asset).filter(
                    Asset.content_hash == content_hash,
                    Asset.is_available == True
                ).first()
                
                if not asset:
                    results.append({
                        'content_hash': content_hash,
                        'success': False,
                        'error': '文件路径不存在'
                    })
                    continue
                
                # 构建文件信息
                file_info = {
                    'content_hash': blob.content_hash,
                    'full_path': asset.full_path,
                    'size': blob.size,
                    'primary_type': blob.primary_type,
                    'mime': blob.mime,
                    'created_at': blob.created_at,
                    'last_seen': asset.last_seen
                }
                
                # 处理文件
                result = rules_engine.process_file(file_info, rules)
                results.append({
                    'content_hash': content_hash,
                    'success': result['success'],
                    'matched_rules': result['matched_rules'],
                    'executed_actions': result['executed_actions'],
                    'results': result.get('results', [])
                })
                
            except Exception as e:
                results.append({
                    'content_hash': content_hash,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'total_files': len(content_hashes),
            'processed_files': len([r for r in results if r['success']]),
            'results': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/operators")
async def get_operators():
    """获取支持的操作符"""
    return {
        "condition_operators": list(rules_engine.condition_operators.keys()),
        "action_handlers": list(rules_engine.action_handlers.keys()),
        "field_types": rules_engine.field_types
    }

@router.get("/examples")
async def get_rule_examples():
    """获取规则示例"""
    return {
        "examples": [
            {
                "name": "图片文件自动标签",
                "description": "为所有图片文件添加'图片'标签",
                "rule": {
                    "name": "图片文件自动标签",
                    "when": {
                        "field": "type",
                        "op": "eq",
                        "value": "image"
                    },
                    "then": [
                        {
                            "action": "add_tag",
                            "args": {
                                "name": "图片",
                                "color": "#4CAF50"
                            }
                        }
                    ]
                }
            },
            {
                "name": "大文件警告",
                "description": "为大于100MB的文件添加'大文件'标签",
                "rule": {
                    "name": "大文件警告",
                    "when": {
                        "field": "size",
                        "op": "gt",
                        "value": 104857600
                    },
                    "then": [
                        {
                            "action": "add_tag",
                            "args": {
                                "name": "大文件",
                                "color": "#FF9800"
                            }
                        }
                    ]
                }
            },
            {
                "name": "临时文件清理",
                "description": "删除临时文件",
                "rule": {
                    "name": "临时文件清理",
                    "when": {
                        "all": [
                            {
                                "field": "name",
                                "op": "starts_with",
                                "value": "temp"
                            },
                            {
                                "field": "type",
                                "op": "eq",
                                "value": "document"
                            }
                        ]
                    },
                    "then": [
                        {
                            "action": "delete_file",
                            "args": {}
                        }
                    ]
                }
            }
        ]
    }
