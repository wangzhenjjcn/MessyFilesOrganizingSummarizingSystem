"""
SavedView引擎服务
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Blob, Asset, SavedView
import logging

logger = logging.getLogger(__name__)

class SavedViewService:
    """SavedView引擎服务"""
    
    def __init__(self):
        self.db = SessionLocal()
        
        # 支持的查询操作符
        self.operators = {
            'eq': '=',
            'ne': '!=',
            'gt': '>',
            'gte': '>=',
            'lt': '<',
            'lte': '<=',
            'like': 'LIKE',
            'in': 'IN',
            'not_in': 'NOT IN',
            'is_null': 'IS NULL',
            'is_not_null': 'IS NOT NULL'
        }
        
        # 支持的字段映射
        self.field_mapping = {
            'name': 'a.full_path',
            'size': 'b.size',
            'type': 'b.primary_type',
            'mime': 'b.mime',
            'created': 'b.created_at',
            'modified': 'a.last_seen',
            'path': 'a.full_path',
            'extension': 'a.full_path',
            'tag': 'ft.tag_id'
        }
    
    def parse_query_ast(self, query_ast: Dict[str, Any]) -> str:
        """解析查询AST为SQL"""
        try:
            if 'all' in query_ast:
                # AND条件
                conditions = []
                for condition in query_ast['all']:
                    sql_condition = self.parse_condition(condition)
                    if sql_condition:
                        conditions.append(sql_condition)
                return ' AND '.join(conditions)
            
            elif 'any' in query_ast:
                # OR条件
                conditions = []
                for condition in query_ast['any']:
                    sql_condition = self.parse_condition(condition)
                    if sql_condition:
                        conditions.append(sql_condition)
                return ' OR '.join(conditions)
            
            elif 'not' in query_ast:
                # NOT条件
                condition = self.parse_condition(query_ast['not'])
                return f"NOT ({condition})" if condition else ""
            
            else:
                # 单个条件
                return self.parse_condition(query_ast)
                
        except Exception as e:
            logger.error(f"解析查询AST失败: {e}")
            return ""
    
    def parse_condition(self, condition: Dict[str, Any]) -> str:
        """解析单个条件"""
        try:
            field = condition.get('field', '')
            operator = condition.get('op', 'eq')
            value = condition.get('value')
            
            # 获取SQL字段名
            sql_field = self.field_mapping.get(field, field)
            
            # 获取SQL操作符
            sql_operator = self.operators.get(operator, '=')
            
            # 处理特殊字段
            if field == 'extension':
                sql_field = f"LOWER(SUBSTR({sql_field}, INSTR({sql_field}, '.') + 1))"
                if isinstance(value, str):
                    value = value.lower()
            
            # 构建SQL条件
            if operator == 'in':
                if isinstance(value, list):
                    value_list = ', '.join([f"'{v}'" for v in value])
                    return f"{sql_field} IN ({value_list})"
                else:
                    return f"{sql_field} = '{value}'"
            
            elif operator == 'not_in':
                if isinstance(value, list):
                    value_list = ', '.join([f"'{v}'" for v in value])
                    return f"{sql_field} NOT IN ({value_list})"
                else:
                    return f"{sql_field} != '{value}'"
            
            elif operator == 'like':
                return f"{sql_field} LIKE '%{value}%'"
            
            elif operator == 'is_null':
                return f"{sql_field} IS NULL"
            
            elif operator == 'is_not_null':
                return f"{sql_field} IS NOT NULL"
            
            else:
                # 处理值类型
                if isinstance(value, str):
                    value = f"'{value}'"
                elif isinstance(value, (int, float)):
                    value = str(value)
                else:
                    value = f"'{value}'"
                
                return f"{sql_field} {sql_operator} {value}"
                
        except Exception as e:
            logger.error(f"解析条件失败: {condition}, 错误: {e}")
            return ""
    
    def execute_savedview(self, savedview_id: int, limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        """执行SavedView查询"""
        try:
            # 获取SavedView
            savedview = self.db.query(SavedView).filter(SavedView.id == savedview_id).first()
            if not savedview:
                return {'error': 'SavedView不存在'}
            
            # 解析查询AST
            query_ast = json.loads(savedview.query_ast_json)
            where_clause = self.parse_query_ast(query_ast)
            
            # 构建基础查询
            base_query = """
            SELECT DISTINCT a.content_hash, a.full_path, a.volume_id, a.is_available,
                   b.size, b.mime, b.primary_type, b.created_at, a.last_seen
            FROM assets a
            JOIN blobs b ON a.content_hash = b.content_hash
            LEFT JOIN file_tags ft ON a.content_hash = ft.content_hash
            WHERE a.is_available = 1
            """
            
            # 添加WHERE条件
            if where_clause:
                base_query += f" AND ({where_clause})"
            
            # 添加排序
            sort_config = query_ast.get('sort', [])
            if sort_config:
                sort_clauses = []
                for sort_item in sort_config:
                    field = sort_item.get('field', 'created_at')
                    direction = sort_item.get('dir', 'desc')
                    sql_field = self.field_mapping.get(field, field)
                    sort_clauses.append(f"{sql_field} {direction.upper()}")
                
                if sort_clauses:
                    base_query += f" ORDER BY {', '.join(sort_clauses)}"
            else:
                base_query += " ORDER BY b.created_at DESC"
            
            # 添加分页
            base_query += f" LIMIT {limit} OFFSET {offset}"
            
            # 执行查询
            result = self.db.execute(text(base_query))
            files = []
            
            for row in result:
                files.append({
                    'content_hash': row.content_hash,
                    'full_path': row.full_path,
                    'volume_id': row.volume_id,
                    'is_available': row.is_available,
                    'size': row.size,
                    'mime': row.mime,
                    'primary_type': row.primary_type,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'last_seen': row.last_seen.isoformat() if row.last_seen else None
                })
            
            # 获取总数
            count_query = base_query.replace(f"LIMIT {limit} OFFSET {offset}", "")
            count_query = f"SELECT COUNT(*) FROM ({count_query})"
            count_result = self.db.execute(text(count_query))
            total = count_result.scalar()
            
            return {
                'files': files,
                'total': total,
                'savedview_id': savedview_id,
                'savedview_name': savedview.name,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"执行SavedView失败: {savedview_id}, 错误: {e}")
            return {'error': str(e)}
    
    def create_savedview(self, name: str, query_ast: Dict[str, Any], layout_json: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建SavedView"""
        try:
            # 验证查询AST
            test_query = self.parse_query_ast(query_ast)
            if not test_query:
                return {'error': '无效的查询AST'}
            
            # 创建SavedView
            savedview = SavedView(
                name=name,
                query_ast_json=json.dumps(query_ast),
                layout_json=json.dumps(layout_json) if layout_json else None
            )
            
            self.db.add(savedview)
            self.db.commit()
            
            return {
                'success': True,
                'savedview_id': savedview.id,
                'name': savedview.name
            }
            
        except Exception as e:
            logger.error(f"创建SavedView失败: {e}")
            self.db.rollback()
            return {'error': str(e)}
    
    def update_savedview(self, savedview_id: int, name: str = None, query_ast: Dict[str, Any] = None, layout_json: Dict[str, Any] = None) -> Dict[str, Any]:
        """更新SavedView"""
        try:
            savedview = self.db.query(SavedView).filter(SavedView.id == savedview_id).first()
            if not savedview:
                return {'error': 'SavedView不存在'}
            
            # 更新字段
            if name:
                savedview.name = name
            
            if query_ast:
                # 验证查询AST
                test_query = self.parse_query_ast(query_ast)
                if not test_query:
                    return {'error': '无效的查询AST'}
                savedview.query_ast_json = json.dumps(query_ast)
            
            if layout_json:
                savedview.layout_json = json.dumps(layout_json)
            
            self.db.commit()
            
            return {
                'success': True,
                'savedview_id': savedview_id,
                'name': savedview.name
            }
            
        except Exception as e:
            logger.error(f"更新SavedView失败: {e}")
            self.db.rollback()
            return {'error': str(e)}
    
    def delete_savedview(self, savedview_id: int) -> Dict[str, Any]:
        """删除SavedView"""
        try:
            savedview = self.db.query(SavedView).filter(SavedView.id == savedview_id).first()
            if not savedview:
                return {'error': 'SavedView不存在'}
            
            self.db.delete(savedview)
            self.db.commit()
            
            return {
                'success': True,
                'savedview_id': savedview_id
            }
            
        except Exception as e:
            logger.error(f"删除SavedView失败: {e}")
            self.db.rollback()
            return {'error': str(e)}
    
    def list_savedviews(self) -> List[Dict[str, Any]]:
        """列出所有SavedView"""
        try:
            savedviews = self.db.query(SavedView).all()
            
            result = []
            for savedview in savedviews:
                result.append({
                    'id': savedview.id,
                    'name': savedview.name,
                    'created_at': savedview.created_at.isoformat() if savedview.created_at else None,
                    'updated_at': savedview.updated_at.isoformat() if savedview.updated_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"列出SavedView失败: {e}")
            return []
    
    def export_symlinks(self, savedview_id: int, export_path: str) -> Dict[str, Any]:
        """导出软链接"""
        try:
            # 执行查询获取文件列表
            result = self.execute_savedview(savedview_id, limit=10000)
            if 'error' in result:
                return result
            
            files = result['files']
            if not files:
                return {'error': '没有找到文件'}
            
            # 创建导出目录
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建软链接
            created_links = []
            failed_links = []
            
            for file_info in files:
                source_path = Path(file_info['full_path'])
                if not source_path.exists():
                    failed_links.append({
                        'source': str(source_path),
                        'error': '源文件不存在'
                    })
                    continue
                
                # 创建目标路径
                target_path = export_dir / source_path.name
                
                # 处理重名文件
                counter = 1
                while target_path.exists():
                    stem = source_path.stem
                    suffix = source_path.suffix
                    target_path = export_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                try:
                    # 创建软链接
                    target_path.symlink_to(source_path)
                    created_links.append({
                        'source': str(source_path),
                        'target': str(target_path)
                    })
                except Exception as e:
                    failed_links.append({
                        'source': str(source_path),
                        'error': str(e)
                    })
            
            # 创建manifest文件
            manifest = {
                'savedview_id': savedview_id,
                'export_path': str(export_dir),
                'total_files': len(files),
                'created_links': len(created_links),
                'failed_links': len(failed_links),
                'created_at': result.get('created_at'),
                'files': created_links,
                'errors': failed_links
            }
            
            manifest_path = export_dir / 'manifest.json'
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'export_path': str(export_dir),
                'total_files': len(files),
                'created_links': len(created_links),
                'failed_links': len(failed_links),
                'manifest_path': str(manifest_path)
            }
            
        except Exception as e:
            logger.error(f"导出软链接失败: {e}")
            return {'error': str(e)}
    
    def refresh_savedview(self, savedview_id: int) -> Dict[str, Any]:
        """刷新SavedView"""
        try:
            # 执行查询获取最新结果
            result = self.execute_savedview(savedview_id, limit=10000)
            
            if 'error' in result:
                return result
            
            # 更新SavedView的更新时间
            savedview = self.db.query(SavedView).filter(SavedView.id == savedview_id).first()
            if savedview:
                from datetime import datetime
                savedview.updated_at = datetime.now()
                self.db.commit()
            
            return {
                'success': True,
                'savedview_id': savedview_id,
                'total_files': result['total'],
                'refreshed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"刷新SavedView失败: {e}")
            return {'error': str(e)}
    
    def get_savedview_stats(self, savedview_id: int) -> Dict[str, Any]:
        """获取SavedView统计信息"""
        try:
            # 执行查询获取统计信息
            result = self.execute_savedview(savedview_id, limit=1)
            
            if 'error' in result:
                return result
            
            # 获取SavedView信息
            savedview = self.db.query(SavedView).filter(SavedView.id == savedview_id).first()
            if not savedview:
                return {'error': 'SavedView不存在'}
            
            # 按文件类型统计
            type_stats = {}
            for file_info in result['files']:
                file_type = file_info.get('primary_type', 'unknown')
                type_stats[file_type] = type_stats.get(file_type, 0) + 1
            
            return {
                'savedview_id': savedview_id,
                'name': savedview.name,
                'total_files': result['total'],
                'type_stats': type_stats,
                'created_at': savedview.created_at.isoformat() if savedview.created_at else None,
                'updated_at': savedview.updated_at.isoformat() if savedview.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"获取SavedView统计失败: {e}")
            return {'error': str(e)}
