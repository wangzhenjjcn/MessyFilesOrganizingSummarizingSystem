"""
哈希服务
"""
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Callable
import blake3
import logging

logger = logging.getLogger(__name__)

class HashService:
    """哈希计算服务"""
    
    def __init__(self):
        self.progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def calculate_fast_hash(self, file_path: Path, chunk_size: int = 64 * 1024) -> str:
        """计算快速哈希（BLAKE3）"""
        try:
            hasher = blake3.blake3()
            file_size = file_path.stat().st_size
            
            with open(file_path, 'rb') as f:
                if file_size <= chunk_size * 2:
                    # 小文件：读取全部内容
                    hasher.update(f.read())
                else:
                    # 大文件：读取头部和尾部
                    # 读取头部
                    head = f.read(chunk_size)
                    hasher.update(head)
                    
                    # 读取尾部
                    f.seek(-chunk_size, 2)
                    tail = f.read(chunk_size)
                    hasher.update(tail)
            
            return hasher.hexdigest()
            
        except Exception as e:
            logger.error(f"计算快速哈希失败: {file_path}, 错误: {e}")
            return ""
    
    def calculate_content_hash(self, file_path: Path, chunk_size: int = 4096) -> str:
        """计算内容哈希（SHA-256）"""
        try:
            sha256_hash = hashlib.sha256()
            file_size = file_path.stat().st_size
            processed = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    sha256_hash.update(chunk)
                    processed += len(chunk)
                    
                    # 调用进度回调
                    if self.progress_callback:
                        progress = (processed / file_size) * 100
                        self.progress_callback({
                            'type': 'hash_progress',
                            'file_path': str(file_path),
                            'progress': progress,
                            'processed': processed,
                            'total': file_size
                        })
            
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"计算内容哈希失败: {file_path}, 错误: {e}")
            return ""
    
    def calculate_both_hashes(self, file_path: Path) -> Dict[str, str]:
        """同时计算快速哈希和内容哈希"""
        fast_hash = self.calculate_fast_hash(file_path)
        content_hash = self.calculate_content_hash(file_path)
        
        return {
            'fast_hash': fast_hash,
            'content_hash': content_hash
        }
    
    def verify_file_integrity(self, file_path: Path, expected_hash: str) -> bool:
        """验证文件完整性"""
        try:
            actual_hash = self.calculate_content_hash(file_path)
            return actual_hash == expected_hash
        except Exception as e:
            logger.error(f"验证文件完整性失败: {file_path}, 错误: {e}")
            return False
    
    def find_duplicate_files(self, file_paths: list[Path]) -> Dict[str, list[Path]]:
        """查找重复文件"""
        hash_groups = {}
        
        for file_path in file_paths:
            try:
                content_hash = self.calculate_content_hash(file_path)
                if content_hash:
                    if content_hash not in hash_groups:
                        hash_groups[content_hash] = []
                    hash_groups[content_hash].append(file_path)
            except Exception as e:
                logger.error(f"计算文件哈希失败: {file_path}, 错误: {e}")
        
        # 返回有重复的组
        return {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}
