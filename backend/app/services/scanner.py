"""
文件扫描器服务
"""
import os
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Blob, Asset, Job
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    """文件扫描器"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.scanning = False
        self.progress_callback: Optional[Callable] = None
        
        # 系统目录黑名单
        self.blacklist_dirs = {
            'System Volume Information',
            '$Recycle.Bin',
            'Windows',
            'Program Files',
            'Program Files (x86)',
            'AppData',
            'Application Data',
            'Local Settings',
            'Temporary Internet Files',
            'Temp',
            '.git',
            '.svn',
            'node_modules',
            '__pycache__',
            '.cache'
        }
        
        # 文件扩展名黑名单
        self.blacklist_extensions = {
            '.tmp', '.temp', '.log', '.cache', '.bak', '.swp',
            '.lock', '.pid', '.sock', '.fifo'
        }
    
    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _is_blacklisted(self, path: Path) -> bool:
        """检查路径是否在黑名单中"""
        # 检查目录名
        for part in path.parts:
            if part in self.blacklist_dirs:
                return True
        
        # 检查文件扩展名
        if path.suffix.lower() in self.blacklist_extensions:
            return True
        
        return False
    
    def _calculate_fast_hash(self, file_path: Path) -> str:
        """计算快速哈希（BLAKE3）"""
        try:
            import blake3
            hasher = blake3.blake3()
            
            # 对于大文件，只读取头部和尾部
            file_size = file_path.stat().st_size
            if file_size > 1024 * 1024:  # 大于1MB的文件
                with open(file_path, 'rb') as f:
                    # 读取前64KB
                    head = f.read(64 * 1024)
                    hasher.update(head)
                    
                    # 如果文件大于128KB，读取后64KB
                    if file_size > 128 * 1024:
                        f.seek(-64 * 1024, 2)  # 从文件末尾向前64KB
                        tail = f.read(64 * 1024)
                        hasher.update(tail)
            else:
                # 小文件直接读取全部内容
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"计算快速哈希失败: {file_path}, 错误: {e}")
            return ""
    
    def _calculate_content_hash(self, file_path: Path) -> str:
        """计算内容哈希（SHA-256）"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"计算内容哈希失败: {file_path}, 错误: {e}")
            return ""
    
    def _get_file_info(self, file_path: Path) -> Dict:
        """获取文件信息"""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'ctime': stat.st_ctime,
                'inode': stat.st_ino,
                'device_id': stat.st_dev
            }
        except Exception as e:
            logger.error(f"获取文件信息失败: {file_path}, 错误: {e}")
            return {}
    
    def _process_file(self, file_path: Path, volume_id: str = None) -> Optional[Dict]:
        """处理单个文件"""
        try:
            if self._is_blacklisted(file_path):
                return None
            
            # 获取文件信息
            file_info = self._get_file_info(file_path)
            if not file_info:
                return None
            
            # 计算快速哈希
            fast_hash = self._calculate_fast_hash(file_path)
            if not fast_hash:
                return None
            
            # 检查是否已存在相同快速哈希的内容
            existing_blob = self.db.query(Blob).filter(Blob.fast_hash == fast_hash).first()
            
            if existing_blob:
                # 使用现有的内容哈希
                content_hash = existing_blob.content_hash
            else:
                # 计算内容哈希
                content_hash = self._calculate_content_hash(file_path)
                if not content_hash:
                    return None
            
            return {
                'file_path': str(file_path),
                'content_hash': content_hash,
                'fast_hash': fast_hash,
                'size': file_info['size'],
                'mtime': file_info['mtime'],
                'ctime': file_info['ctime'],
                'inode': file_info['inode'],
                'device_id': file_info['device_id'],
                'volume_id': volume_id or str(file_path.anchor)
            }
            
        except Exception as e:
            logger.error(f"处理文件失败: {file_path}, 错误: {e}")
            return None
    
    def _scan_directory(self, directory: Path, volume_id: str = None) -> List[Dict]:
        """扫描目录"""
        results = []
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    file_info = self._process_file(item, volume_id)
                    if file_info:
                        results.append(file_info)
                        
                        # 调用进度回调
                        if self.progress_callback:
                            self.progress_callback({
                                'type': 'file_processed',
                                'path': str(item),
                                'total_found': len(results)
                            })
                
                elif item.is_dir() and not self._is_blacklisted(item):
                    # 递归扫描子目录
                    sub_results = self._scan_directory(item, volume_id)
                    results.extend(sub_results)
                    
        except PermissionError:
            logger.warning(f"权限不足，跳过目录: {directory}")
        except Exception as e:
            logger.error(f"扫描目录失败: {directory}, 错误: {e}")
        
        return results
    
    def scan_path(self, path: str, volume_id: str = None) -> Dict:
        """扫描指定路径"""
        scan_path = Path(path)
        
        if not scan_path.exists():
            raise ValueError(f"路径不存在: {path}")
        
        self.scanning = True
        start_time = time.time()
        
        try:
            if scan_path.is_file():
                # 扫描单个文件
                file_info = self._process_file(scan_path, volume_id)
                results = [file_info] if file_info else []
            else:
                # 扫描目录
                results = self._scan_directory(scan_path, volume_id)
            
            # 保存到数据库
            saved_count = self._save_scan_results(results)
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'success': True,
                'path': path,
                'files_found': len(results),
                'files_saved': saved_count,
                'duration': duration,
                'scan_time': end_time
            }
            
        except Exception as e:
            logger.error(f"扫描失败: {path}, 错误: {e}")
            return {
                'success': False,
                'path': path,
                'error': str(e)
            }
        finally:
            self.scanning = False
    
    def _save_scan_results(self, results: List[Dict]) -> int:
        """保存扫描结果到数据库"""
        saved_count = 0
        
        try:
            for result in results:
                # 检查Blob是否已存在
                blob = self.db.query(Blob).filter(
                    Blob.content_hash == result['content_hash']
                ).first()
                
                if not blob:
                    # 创建新的Blob
                    blob = Blob(
                        content_hash=result['content_hash'],
                        fast_hash=result['fast_hash'],
                        size=result['size']
                    )
                    self.db.add(blob)
                
                # 检查Asset是否已存在
                existing_asset = self.db.query(Asset).filter(
                    Asset.content_hash == result['content_hash'],
                    Asset.full_path == result['file_path']
                ).first()
                
                if not existing_asset:
                    # 创建新的Asset
                    asset = Asset(
                        content_hash=result['content_hash'],
                        full_path=result['file_path'],
                        volume_id=result['volume_id'],
                        inode=str(result['inode']),
                        device_id=str(result['device_id'])
                    )
                    self.db.add(asset)
                    saved_count += 1
                else:
                    # 更新现有Asset的最后发现时间
                    existing_asset.last_seen = time.time()
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"保存扫描结果失败: {e}")
            self.db.rollback()
        
        return saved_count
    
    def stop_scan(self):
        """停止扫描"""
        self.scanning = False
    
    def get_scan_status(self) -> Dict:
        """获取扫描状态"""
        return {
            'scanning': self.scanning,
            'total_files': self.db.query(Asset).count(),
            'available_files': self.db.query(Asset).filter(Asset.is_available == True).count()
        }
