"""
搜索服务
"""
import sqlite3
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Blob, Asset
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """搜索服务"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def setup_fts5_index(self):
        """设置FTS5全文搜索索引"""
        try:
            # 创建FTS5虚拟表
            fts5_sql = """
            CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
                content_hash,
                file_path,
                file_name,
                file_extension,
                mime_type,
                primary_type,
                size,
                content='',
                content_rowid='rowid'
            );
            """
            
            # 创建触发器以保持FTS5索引同步
            trigger_sql = """
            CREATE TRIGGER IF NOT EXISTS files_fts_insert AFTER INSERT ON assets BEGIN
                INSERT INTO files_fts(
                    content_hash, file_path, file_name, file_extension,
                    mime_type, primary_type, size
                ) VALUES (
                    NEW.content_hash,
                    NEW.full_path,
                    (SELECT name FROM files WHERE path = NEW.full_path),
                    (SELECT extension FROM files WHERE path = NEW.full_path),
                    (SELECT mime FROM blobs WHERE content_hash = NEW.content_hash),
                    (SELECT primary_type FROM blobs WHERE content_hash = NEW.content_hash),
                    (SELECT size FROM blobs WHERE content_hash = NEW.content_hash)
                );
            END;
            """
            
            # 执行SQL
            self.db.execute(text(fts5_sql))
            self.db.execute(text(trigger_sql))
            self.db.commit()
            
            logger.info("FTS5索引设置完成")
            return True
            
        except Exception as e:
            logger.error(f"设置FTS5索引失败: {e}")
            self.db.rollback()
            return False
    
    def search_files(self, query: str, filters: Dict = None, limit: int = 100, offset: int = 0) -> Dict:
        """搜索文件"""
        try:
            # 构建基础查询
            base_query = """
            SELECT DISTINCT a.content_hash, a.full_path, a.volume_id, a.is_available,
                   b.size, b.mime, b.primary_type, b.created_at
            FROM assets a
            JOIN blobs b ON a.content_hash = b.content_hash
            WHERE a.is_available = 1
            """
            
            # 添加全文搜索
            if query:
                fts_query = f"""
                AND a.content_hash IN (
                    SELECT content_hash FROM files_fts 
                    WHERE files_fts MATCH :query
                )
                """
                base_query += fts_query
            
            # 添加过滤器
            if filters:
                if 'file_type' in filters:
                    base_query += " AND b.primary_type = :file_type"
                
                if 'min_size' in filters:
                    base_query += " AND b.size >= :min_size"
                
                if 'max_size' in filters:
                    base_query += " AND b.size <= :max_size"
                
                if 'extension' in filters:
                    base_query += " AND a.full_path LIKE :extension"
            
            # 添加排序和分页
            base_query += " ORDER BY b.created_at DESC LIMIT :limit OFFSET :offset"
            
            # 准备参数
            params = {'query': query, 'limit': limit, 'offset': offset}
            if filters:
                params.update(filters)
            
            # 执行查询
            result = self.db.execute(text(base_query), params)
            files = result.fetchall()
            
            # 获取总数
            count_query = base_query.replace("ORDER BY b.created_at DESC LIMIT :limit OFFSET :offset", "")
            count_query = f"SELECT COUNT(*) FROM ({count_query})"
            count_result = self.db.execute(text(count_query), params)
            total = count_result.scalar()
            
            return {
                'files': [dict(row._mapping) for row in files],
                'total': total,
                'query': query,
                'filters': filters
            }
            
        except Exception as e:
            logger.error(f"搜索文件失败: {e}")
            return {'files': [], 'total': 0, 'error': str(e)}
    
    def search_by_content_hash(self, content_hash: str) -> Optional[Dict]:
        """根据内容哈希搜索文件"""
        try:
            query = """
            SELECT a.content_hash, a.full_path, a.volume_id, a.is_available,
                   b.size, b.mime, b.primary_type, b.created_at
            FROM assets a
            JOIN blobs b ON a.content_hash = b.content_hash
            WHERE a.content_hash = :content_hash
            """
            
            result = self.db.execute(text(query), {'content_hash': content_hash})
            row = result.fetchone()
            
            if row:
                return dict(row._mapping)
            return None
            
        except Exception as e:
            logger.error(f"根据内容哈希搜索失败: {e}")
            return None
    
    def search_similar_files(self, content_hash: str, similarity_threshold: float = 0.8) -> List[Dict]:
        """搜索相似文件"""
        try:
            # 获取源文件的感知哈希
            source_query = """
            SELECT phash, audio_fingerprint, doc_fingerprint
            FROM blobs WHERE content_hash = :content_hash
            """
            
            source_result = self.db.execute(text(source_query), {'content_hash': content_hash})
            source_row = source_result.fetchone()
            
            if not source_row:
                return []
            
            similar_files = []
            
            # 搜索图片相似文件（基于感知哈希）
            if source_row.phash:
                phash_query = """
                SELECT a.content_hash, a.full_path, b.size, b.mime
                FROM assets a
                JOIN blobs b ON a.content_hash = b.content_hash
                WHERE b.phash IS NOT NULL 
                AND b.content_hash != :content_hash
                AND a.is_available = 1
                """
                
                phash_result = self.db.execute(text(phash_query), {'content_hash': content_hash})
                for row in phash_result:
                    # TODO: 实现感知哈希相似度计算
                    similar_files.append(dict(row._mapping))
            
            # 搜索音频相似文件（基于音频指纹）
            if source_row.audio_fingerprint:
                audio_query = """
                SELECT a.content_hash, a.full_path, b.size, b.mime
                FROM assets a
                JOIN blobs b ON a.content_hash = b.content_hash
                WHERE b.audio_fingerprint IS NOT NULL 
                AND b.content_hash != :content_hash
                AND a.is_available = 1
                """
                
                audio_result = self.db.execute(text(audio_query), {'content_hash': content_hash})
                for row in audio_result:
                    # TODO: 实现音频指纹相似度计算
                    similar_files.append(dict(row._mapping))
            
            return similar_files
            
        except Exception as e:
            logger.error(f"搜索相似文件失败: {e}")
            return []
    
    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """获取搜索建议"""
        try:
            if len(query) < 2:
                return []
            
            # 搜索文件名建议
            suggestions_query = """
            SELECT DISTINCT file_name
            FROM files_fts
            WHERE file_name MATCH :query
            LIMIT :limit
            """
            
            result = self.db.execute(text(suggestions_query), {
                'query': f"{query}*",
                'limit': limit
            })
            
            suggestions = [row[0] for row in result.fetchall()]
            return suggestions
            
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    def rebuild_fts_index(self):
        """重建FTS5索引"""
        try:
            # 清空现有索引
            self.db.execute(text("DELETE FROM files_fts"))
            
            # 重新填充索引
            populate_sql = """
            INSERT INTO files_fts(
                content_hash, file_path, file_name, file_extension,
                mime_type, primary_type, size
            )
            SELECT 
                a.content_hash,
                a.full_path,
                substr(a.full_path, instr(a.full_path, '/') + 1) as file_name,
                CASE 
                    WHEN instr(a.full_path, '.') > 0 
                    THEN substr(a.full_path, instr(a.full_path, '.'))
                    ELSE ''
                END as file_extension,
                b.mime,
                b.primary_type,
                b.size
            FROM assets a
            JOIN blobs b ON a.content_hash = b.content_hash
            WHERE a.is_available = 1
            """
            
            self.db.execute(text(populate_sql))
            self.db.commit()
            
            logger.info("FTS5索引重建完成")
            return True
            
        except Exception as e:
            logger.error(f"重建FTS5索引失败: {e}")
            self.db.rollback()
            return False
