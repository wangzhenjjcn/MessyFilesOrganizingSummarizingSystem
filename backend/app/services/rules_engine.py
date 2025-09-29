"""
规则引擎服务
"""
import json
import re
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
import logging
from app.database import SessionLocal
from app.models.blobs import Blob
from app.models.assets import Asset
from app.models.tags import Tag, FileTag

logger = logging.getLogger(__name__)

class RulesEngine:
    """规则引擎"""
    
    def __init__(self):
        self.db = SessionLocal()
        
        # 支持的条件操作符
        self.condition_operators = {
            'eq': self._eq,
            'ne': self._ne,
            'gt': self._gt,
            'gte': self._gte,
            'lt': self._lt,
            'lte': self._lte,
            'contains': self._contains,
            'starts_with': self._starts_with,
            'ends_with': self._ends_with,
            'regex': self._regex,
            'in': self._in,
            'not_in': self._not_in,
            'is_null': self._is_null,
            'is_not_null': self._is_not_null
        }
        
        # 支持的动作类型
        self.action_handlers = {
            'add_tag': self._add_tag,
            'remove_tag': self._remove_tag,
            'set_primary_type': self._set_primary_type,
            'move_file': self._move_file,
            'copy_file': self._copy_file,
            'delete_file': self._delete_file,
            'generate_preview': self._generate_preview,
            'extract_metadata': self._extract_metadata,
            'send_notification': self._send_notification
        }
        
        # 支持的字段类型
        self.field_types = {
            'name': 'string',
            'size': 'number',
            'type': 'string',
            'mime': 'string',
            'created': 'datetime',
            'modified': 'datetime',
            'path': 'string',
            'extension': 'string',
            'tag': 'string'
        }
    
    def evaluate_condition(self, condition: Dict[str, Any], file_info: Dict[str, Any]) -> bool:
        """评估条件"""
        try:
            field = condition.get('field')
            operator = condition.get('op', 'eq')
            value = condition.get('value')
            
            if not field or operator not in self.condition_operators:
                return False
            
            # 获取字段值
            field_value = self._get_field_value(file_info, field)
            
            # 执行条件检查
            handler = self.condition_operators[operator]
            return handler(field_value, value)
            
        except Exception as e:
            logger.error(f"评估条件失败: {condition}, 错误: {e}")
            return False
    
    def evaluate_rule(self, rule: Dict[str, Any], file_info: Dict[str, Any]) -> bool:
        """评估规则"""
        try:
            conditions = rule.get('when', {})
            
            if 'all' in conditions:
                # AND条件
                for condition in conditions['all']:
                    if not self.evaluate_condition(condition, file_info):
                        return False
                return True
            
            elif 'any' in conditions:
                # OR条件
                for condition in conditions['any']:
                    if self.evaluate_condition(condition, file_info):
                        return True
                return False
            
            elif 'not' in conditions:
                # NOT条件
                return not self.evaluate_condition(conditions['not'], file_info)
            
            else:
                # 单个条件
                return self.evaluate_condition(conditions, file_info)
                
        except Exception as e:
            logger.error(f"评估规则失败: {rule}, 错误: {e}")
            return False
    
    def execute_actions(self, actions: List[Dict[str, Any]], file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行动作"""
        results = []
        
        for action in actions:
            try:
                action_type = action.get('action')
                args = action.get('args', {})
                
                if action_type not in self.action_handlers:
                    results.append({
                        'action': action_type,
                        'success': False,
                        'error': f'不支持的动作类型: {action_type}'
                    })
                    continue
                
                # 执行动作
                handler = self.action_handlers[action_type]
                result = handler(file_info, args)
                
                results.append({
                    'action': action_type,
                    'success': result.get('success', False),
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"执行动作失败: {action}, 错误: {e}")
                results.append({
                    'action': action.get('action', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def process_file(self, file_info: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理文件"""
        try:
            matched_rules = []
            executed_actions = []
            
            for rule in rules:
                # 评估规则
                if self.evaluate_rule(rule, file_info):
                    matched_rules.append(rule)
                    
                    # 执行动作
                    actions = rule.get('then', [])
                    if actions:
                        action_results = self.execute_actions(actions, file_info)
                        executed_actions.extend(action_results)
            
            return {
                'success': True,
                'matched_rules': len(matched_rules),
                'executed_actions': len(executed_actions),
                'results': executed_actions
            }
            
        except Exception as e:
            logger.error(f"处理文件失败: {file_info}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_field_value(self, file_info: Dict[str, Any], field: str) -> Any:
        """获取字段值"""
        try:
            if field == 'name':
                return Path(file_info.get('full_path', '')).name
            
            elif field == 'size':
                return file_info.get('size', 0)
            
            elif field == 'type':
                return file_info.get('primary_type', '')
            
            elif field == 'mime':
                return file_info.get('mime', '')
            
            elif field == 'created':
                return file_info.get('created_at')
            
            elif field == 'modified':
                return file_info.get('last_seen')
            
            elif field == 'path':
                return file_info.get('full_path', '')
            
            elif field == 'extension':
                return Path(file_info.get('full_path', '')).suffix.lower()
            
            elif field == 'tag':
                return file_info.get('tags', [])
            
            else:
                return file_info.get(field)
                
        except Exception as e:
            logger.error(f"获取字段值失败: {field}, 错误: {e}")
            return None
    
    # 条件操作符实现
    def _eq(self, field_value: Any, value: Any) -> bool:
        return field_value == value
    
    def _ne(self, field_value: Any, value: Any) -> bool:
        return field_value != value
    
    def _gt(self, field_value: Any, value: Any) -> bool:
        return field_value > value
    
    def _gte(self, field_value: Any, value: Any) -> bool:
        return field_value >= value
    
    def _lt(self, field_value: Any, value: Any) -> bool:
        return field_value < value
    
    def _lte(self, field_value: Any, value: Any) -> bool:
        return field_value <= value
    
    def _contains(self, field_value: Any, value: Any) -> bool:
        if isinstance(field_value, str) and isinstance(value, str):
            return value.lower() in field_value.lower()
        return False
    
    def _starts_with(self, field_value: Any, value: Any) -> bool:
        if isinstance(field_value, str) and isinstance(value, str):
            return field_value.lower().startswith(value.lower())
        return False
    
    def _ends_with(self, field_value: Any, value: Any) -> bool:
        if isinstance(field_value, str) and isinstance(value, str):
            return field_value.lower().endswith(value.lower())
        return False
    
    def _regex(self, field_value: Any, value: Any) -> bool:
        if isinstance(field_value, str) and isinstance(value, str):
            try:
                return bool(re.search(value, field_value))
            except re.error:
                return False
        return False
    
    def _in(self, field_value: Any, value: Any) -> bool:
        if isinstance(value, list):
            return field_value in value
        return False
    
    def _not_in(self, field_value: Any, value: Any) -> bool:
        if isinstance(value, list):
            return field_value not in value
        return False
    
    def _is_null(self, field_value: Any, value: Any) -> bool:
        return field_value is None
    
    def _is_not_null(self, field_value: Any, value: Any) -> bool:
        return field_value is not None
    
    # 动作处理器实现
    def _add_tag(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """添加标签"""
        try:
            tag_name = args.get('name')
            if not tag_name:
                return {'success': False, 'error': '标签名称不能为空'}
            
            content_hash = file_info.get('content_hash')
            if not content_hash:
                return {'success': False, 'error': '文件哈希不存在'}
            
            # 获取或创建标签
            tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, kind='rule', color=args.get('color', '#2196F3'))
                self.db.add(tag)
                self.db.flush()
            
            # 检查是否已存在
            existing = self.db.query(FileTag).filter(
                FileTag.content_hash == content_hash,
                FileTag.tag_id == tag.id
            ).first()
            
            if not existing:
                file_tag = FileTag(
                    content_hash=content_hash,
                    tag_id=tag.id,
                    source='rule',
                    confidence=args.get('confidence', 1.0)
                )
                self.db.add(file_tag)
                self.db.commit()
            
            return {'success': True, 'tag_name': tag_name}
            
        except Exception as e:
            logger.error(f"添加标签失败: {e}")
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def _remove_tag(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """移除标签"""
        try:
            tag_name = args.get('name')
            if not tag_name:
                return {'success': False, 'error': '标签名称不能为空'}
            
            content_hash = file_info.get('content_hash')
            if not content_hash:
                return {'success': False, 'error': '文件哈希不存在'}
            
            # 查找标签
            tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                return {'success': True, 'message': '标签不存在'}
            
            # 删除文件标签
            self.db.query(FileTag).filter(
                FileTag.content_hash == content_hash,
                FileTag.tag_id == tag.id
            ).delete()
            
            self.db.commit()
            return {'success': True, 'tag_name': tag_name}
            
        except Exception as e:
            logger.error(f"移除标签失败: {e}")
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def _set_primary_type(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """设置主要类型"""
        try:
            primary_type = args.get('type')
            if not primary_type:
                return {'success': False, 'error': '类型不能为空'}
            
            content_hash = file_info.get('content_hash')
            if not content_hash:
                return {'success': False, 'error': '文件哈希不存在'}
            
            # 更新Blob
            blob = self.db.query(Blob).filter(Blob.content_hash == content_hash).first()
            if blob:
                blob.primary_type = primary_type
                self.db.commit()
            
            return {'success': True, 'primary_type': primary_type}
            
        except Exception as e:
            logger.error(f"设置主要类型失败: {e}")
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def _move_file(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """移动文件"""
        try:
            target_path = args.get('path')
            if not target_path:
                return {'success': False, 'error': '目标路径不能为空'}
            
            source_path = file_info.get('full_path')
            if not source_path:
                return {'success': False, 'error': '源文件路径不存在'}
            
            # 执行移动
            import shutil
            shutil.move(source_path, target_path)
            
            # 更新数据库
            asset = self.db.query(Asset).filter(Asset.full_path == source_path).first()
            if asset:
                asset.full_path = target_path
                self.db.commit()
            
            return {'success': True, 'target_path': target_path}
            
        except Exception as e:
            logger.error(f"移动文件失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _copy_file(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """复制文件"""
        try:
            target_path = args.get('path')
            if not target_path:
                return {'success': False, 'error': '目标路径不能为空'}
            
            source_path = file_info.get('full_path')
            if not source_path:
                return {'success': False, 'error': '源文件路径不存在'}
            
            # 执行复制
            import shutil
            shutil.copy2(source_path, target_path)
            
            return {'success': True, 'target_path': target_path}
            
        except Exception as e:
            logger.error(f"复制文件失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _delete_file(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """删除文件"""
        try:
            source_path = file_info.get('full_path')
            if not source_path:
                return {'success': False, 'error': '源文件路径不存在'}
            
            # 执行删除
            import os
            os.remove(source_path)
            
            # 更新数据库
            asset = self.db.query(Asset).filter(Asset.full_path == source_path).first()
            if asset:
                asset.is_available = False
                self.db.commit()
            
            return {'success': True, 'deleted_path': source_path}
            
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_preview(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """生成预览"""
        try:
            content_hash = file_info.get('content_hash')
            if not content_hash:
                return {'success': False, 'error': '文件哈希不存在'}
            
            # 这里可以调用预览服务
            # 暂时返回成功
            return {'success': True, 'content_hash': content_hash}
            
        except Exception as e:
            logger.error(f"生成预览失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_metadata(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """提取元数据"""
        try:
            content_hash = file_info.get('content_hash')
            if not content_hash:
                return {'success': False, 'error': '文件哈希不存在'}
            
            # 这里可以调用元数据提取服务
            # 暂时返回成功
            return {'success': True, 'content_hash': content_hash}
            
        except Exception as e:
            logger.error(f"提取元数据失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_notification(self, file_info: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """发送通知"""
        try:
            message = args.get('message', '规则执行完成')
            # 这里可以实现通知逻辑
            logger.info(f"通知: {message}, 文件: {file_info.get('full_path')}")
            
            return {'success': True, 'message': message}
            
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """验证规则"""
        try:
            # 检查必需字段
            if 'name' not in rule:
                return {'valid': False, 'error': '规则名称不能为空'}
            
            if 'when' not in rule:
                return {'valid': False, 'error': '规则条件不能为空'}
            
            if 'then' not in rule:
                return {'valid': False, 'error': '规则动作不能为空'}
            
            # 验证条件
            conditions = rule['when']
            if not self._validate_conditions(conditions):
                return {'valid': False, 'error': '无效的条件配置'}
            
            # 验证动作
            actions = rule['then']
            if not self._validate_actions(actions):
                return {'valid': False, 'error': '无效的动作配置'}
            
            return {'valid': True, 'message': '规则验证通过'}
            
        except Exception as e:
            logger.error(f"验证规则失败: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _validate_conditions(self, conditions: Dict[str, Any]) -> bool:
        """验证条件"""
        try:
            if 'all' in conditions:
                for condition in conditions['all']:
                    if not self._validate_condition(condition):
                        return False
            elif 'any' in conditions:
                for condition in conditions['any']:
                    if not self._validate_condition(condition):
                        return False
            elif 'not' in conditions:
                return self._validate_condition(conditions['not'])
            else:
                return self._validate_condition(conditions)
            
            return True
            
        except Exception as e:
            logger.error(f"验证条件失败: {e}")
            return False
    
    def _validate_condition(self, condition: Dict[str, Any]) -> bool:
        """验证单个条件"""
        try:
            field = condition.get('field')
            operator = condition.get('op')
            
            if not field or not operator:
                return False
            
            if field not in self.field_types:
                return False
            
            if operator not in self.condition_operators:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证单个条件失败: {e}")
            return False
    
    def _validate_actions(self, actions: List[Dict[str, Any]]) -> bool:
        """验证动作"""
        try:
            for action in actions:
                action_type = action.get('action')
                if not action_type or action_type not in self.action_handlers:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证动作失败: {e}")
            return False
