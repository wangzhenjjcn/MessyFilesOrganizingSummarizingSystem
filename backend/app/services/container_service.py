"""
容器文件提取服务
"""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from app.database import SessionLocal
from app.models.blobs import Blob
from app.models.assets import Asset
from app.models.containers import Container, Containment

logger = logging.getLogger(__name__)

class ContainerService:
    """容器文件提取服务"""
    
    def __init__(self):
        self.db = SessionLocal()
        
        # 支持的容器类型
        self.supported_types = {
            'zip': ['.zip'],
            '7z': ['.7z'],
            'tar': ['.tar', '.tar.gz', '.tar.bz2', '.tar.xz'],
            'iso': ['.iso'],
            'rar': ['.rar']
        }
    
    def get_container_type(self, file_path: str) -> Optional[str]:
        """获取容器类型"""
        ext = Path(file_path).suffix.lower()
        
        for container_type, extensions in self.supported_types.items():
            if ext in extensions:
                return container_type
        
        return None
    
    def extract_zip(self, file_path: str, content_hash: str) -> Dict[str, Any]:
        """提取ZIP文件"""
        try:
            import zipfile
            
            extracted_files = []
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 获取文件列表
                file_list = zip_ref.namelist()
                
                for file_name in file_list:
                    # 跳过目录
                    if file_name.endswith('/'):
                        continue
                    
                    try:
                        # 获取文件信息
                        file_info = zip_ref.getinfo(file_name)
                        
                        extracted_files.append({
                            'name': file_name,
                            'size': file_info.file_size,
                            'compressed_size': file_info.compress_size,
                            'modified': file_info.date_time,
                            'crc': file_info.CRC
                        })
                    except Exception as e:
                        logger.warning(f"获取ZIP文件信息失败: {file_name}, 错误: {e}")
                        continue
            
            return {
                'success': True,
                'container_type': 'zip',
                'total_files': len(extracted_files),
                'files': extracted_files
            }
            
        except Exception as e:
            logger.error(f"提取ZIP文件失败: {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_7z(self, file_path: str, content_hash: str) -> Dict[str, Any]:
        """提取7Z文件"""
        try:
            import py7zr
            
            extracted_files = []
            
            with py7zr.SevenZipFile(file_path, mode='r') as archive:
                # 获取文件列表
                file_list = archive.getnames()
                
                for file_name in file_list:
                    try:
                        # 获取文件信息
                        file_info = archive.getmember(file_name)
                        
                        extracted_files.append({
                            'name': file_name,
                            'size': file_info.uncompressed_size,
                            'compressed_size': file_info.compressed_size,
                            'modified': file_info.creationtime,
                            'crc': file_info.crc
                        })
                    except Exception as e:
                        logger.warning(f"获取7Z文件信息失败: {file_name}, 错误: {e}")
                        continue
            
            return {
                'success': True,
                'container_type': '7z',
                'total_files': len(extracted_files),
                'files': extracted_files
            }
            
        except Exception as e:
            logger.error(f"提取7Z文件失败: {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_tar(self, file_path: str, content_hash: str) -> Dict[str, Any]:
        """提取TAR文件"""
        try:
            import tarfile
            
            extracted_files = []
            
            with tarfile.open(file_path, 'r') as tar_ref:
                # 获取文件列表
                file_list = tar_ref.getnames()
                
                for file_name in file_list:
                    try:
                        # 获取文件信息
                        file_info = tar_ref.getmember(file_name)
                        
                        extracted_files.append({
                            'name': file_name,
                            'size': file_info.size,
                            'modified': file_info.mtime,
                            'type': file_info.type,
                            'mode': file_info.mode
                        })
                    except Exception as e:
                        logger.warning(f"获取TAR文件信息失败: {file_name}, 错误: {e}")
                        continue
            
            return {
                'success': True,
                'container_type': 'tar',
                'total_files': len(extracted_files),
                'files': extracted_files
            }
            
        except Exception as e:
            logger.error(f"提取TAR文件失败: {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_iso(self, file_path: str, content_hash: str) -> Dict[str, Any]:
        """提取ISO文件"""
        try:
            # 使用pycdlib库处理ISO文件
            import pycdlib
            
            extracted_files = []
            
            iso = pycdlib.PyCdlib()
            iso.open(file_path)
            
            try:
                # 遍历ISO文件系统
                for root, dirs, files in iso.walk():
                    for file_name in files:
                        try:
                            # 获取文件信息
                            file_info = iso.get_file_info(file_name)
                            
                            extracted_files.append({
                                'name': file_name,
                                'size': file_info.size,
                                'modified': file_info.date,
                                'type': 'file'
                            })
                        except Exception as e:
                            logger.warning(f"获取ISO文件信息失败: {file_name}, 错误: {e}")
                            continue
            finally:
                iso.close()
            
            return {
                'success': True,
                'container_type': 'iso',
                'total_files': len(extracted_files),
                'files': extracted_files
            }
            
        except Exception as e:
            logger.error(f"提取ISO文件失败: {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_container(self, content_hash: str, file_path: str) -> Dict[str, Any]:
        """提取容器文件"""
        try:
            # 获取容器类型
            container_type = self.get_container_type(file_path)
            if not container_type:
                return {
                    'success': False,
                    'error': '不支持的容器类型'
                }
            
            # 根据类型提取
            if container_type == 'zip':
                result = self.extract_zip(file_path, content_hash)
            elif container_type == '7z':
                result = self.extract_7z(file_path, content_hash)
            elif container_type == 'tar':
                result = self.extract_tar(file_path, content_hash)
            elif container_type == 'iso':
                result = self.extract_iso(file_path, content_hash)
            else:
                return {
                    'success': False,
                    'error': f'不支持的容器类型: {container_type}'
                }
            
            if result['success']:
                # 保存到数据库
                self.save_container_info(content_hash, container_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"提取容器文件失败: {content_hash}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_container_info(self, content_hash: str, container_type: str, extraction_result: Dict[str, Any]):
        """保存容器信息到数据库"""
        try:
            # 检查容器是否已存在
            container = self.db.query(Container).filter(Container.content_hash == content_hash).first()
            
            if not container:
                # 创建容器记录
                container = Container(
                    type=container_type,
                    content_hash=content_hash,
                    meta_json=str(extraction_result)
                )
                self.db.add(container)
                self.db.flush()  # 获取ID
            
            # 清空现有内容记录
            self.db.query(Containment).filter(Containment.container_id == container.id).delete()
            
            # 添加内容记录
            for file_info in extraction_result.get('files', []):
                containment = Containment(
                    container_id=container.id,
                    child_content_hash=None,  # 容器内文件没有独立的内容哈希
                    path_in_container=file_info['name'],
                    meta=str(file_info)
                )
                self.db.add(containment)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"保存容器信息失败: {content_hash}, 错误: {e}")
            self.db.rollback()
    
    def get_container_info(self, content_hash: str) -> Dict[str, Any]:
        """获取容器信息"""
        try:
            container = self.db.query(Container).filter(Container.content_hash == content_hash).first()
            if not container:
                return {
                    'success': False,
                    'error': '容器不存在'
                }
            
            # 获取内容列表
            containments = self.db.query(Containment).filter(Containment.container_id == container.id).all()
            
            files = []
            for containment in containments:
                files.append({
                    'path': containment.path_in_container,
                    'meta': containment.meta
                })
            
            return {
                'success': True,
                'container_id': container.id,
                'type': container.type,
                'content_hash': container.content_hash,
                'total_files': len(files),
                'files': files
            }
            
        except Exception as e:
            logger.error(f"获取容器信息失败: {content_hash}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_containers(self) -> List[Dict[str, Any]]:
        """列出所有容器"""
        try:
            containers = self.db.query(Container).all()
            
            result = []
            for container in containers:
                # 获取文件数量
                file_count = self.db.query(Containment).filter(Containment.container_id == container.id).count()
                
                result.append({
                    'id': container.id,
                    'type': container.type,
                    'content_hash': container.content_hash,
                    'file_count': file_count
                })
            
            return result
            
        except Exception as e:
            logger.error(f"列出容器失败: {e}")
            return []
    
    def delete_container(self, content_hash: str) -> Dict[str, Any]:
        """删除容器信息"""
        try:
            container = self.db.query(Container).filter(Container.content_hash == content_hash).first()
            if not container:
                return {
                    'success': False,
                    'error': '容器不存在'
                }
            
            # 删除内容记录
            self.db.query(Containment).filter(Containment.container_id == container.id).delete()
            
            # 删除容器记录
            self.db.delete(container)
            self.db.commit()
            
            return {
                'success': True,
                'message': f'容器已删除: {content_hash}'
            }
            
        except Exception as e:
            logger.error(f"删除容器失败: {content_hash}, 错误: {e}")
            self.db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_container_file(self, content_hash: str, file_path: str, target_path: str) -> Dict[str, Any]:
        """提取容器中的特定文件"""
        try:
            # 获取容器信息
            container_info = self.get_container_info(content_hash)
            if not container_info['success']:
                return container_info
            
            # 查找目标文件
            target_file = None
            for file_info in container_info['files']:
                if file_info['path'] == file_path:
                    target_file = file_info
                    break
            
            if not target_file:
                return {
                    'success': False,
                    'error': '文件不存在于容器中'
                }
            
            # 根据容器类型提取文件
            container_type = container_info['type']
            source_path = self.get_source_path(content_hash)
            
            if not source_path or not os.path.exists(source_path):
                return {
                    'success': False,
                    'error': '源容器文件不存在'
                }
            
            # 提取文件
            if container_type == 'zip':
                return self.extract_zip_file(source_path, file_path, target_path)
            elif container_type == '7z':
                return self.extract_7z_file(source_path, file_path, target_path)
            elif container_type == 'tar':
                return self.extract_tar_file(source_path, file_path, target_path)
            else:
                return {
                    'success': False,
                    'error': f'不支持的容器类型: {container_type}'
                }
                
        except Exception as e:
            logger.error(f"提取容器文件失败: {content_hash}, {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_source_path(self, content_hash: str) -> Optional[str]:
        """获取源文件路径"""
        try:
            asset = self.db.query(Asset).filter(
                Asset.content_hash == content_hash,
                Asset.is_available == True
            ).first()
            
            return asset.full_path if asset else None
            
        except Exception as e:
            logger.error(f"获取源文件路径失败: {content_hash}, 错误: {e}")
            return None
    
    def extract_zip_file(self, source_path: str, file_path: str, target_path: str) -> Dict[str, Any]:
        """从ZIP中提取特定文件"""
        try:
            import zipfile
            
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                # 检查文件是否存在
                if file_path not in zip_ref.namelist():
                    return {
                        'success': False,
                        'error': '文件不存在于ZIP中'
                    }
                
                # 提取文件
                with zip_ref.open(file_path) as source_file:
                    with open(target_path, 'wb') as target_file:
                        shutil.copyfileobj(source_file, target_file)
            
            return {
                'success': True,
                'target_path': target_path,
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"从ZIP提取文件失败: {source_path}, {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_7z_file(self, source_path: str, file_path: str, target_path: str) -> Dict[str, Any]:
        """从7Z中提取特定文件"""
        try:
            import py7zr
            
            with py7zr.SevenZipFile(source_path, mode='r') as archive:
                # 检查文件是否存在
                if file_path not in archive.getnames():
                    return {
                        'success': False,
                        'error': '文件不存在于7Z中'
                    }
                
                # 提取文件
                archive.extract(paths=[file_path], target_dir=os.path.dirname(target_path))
                
                # 移动文件到目标位置
                extracted_path = os.path.join(os.path.dirname(target_path), file_path)
                if os.path.exists(extracted_path):
                    shutil.move(extracted_path, target_path)
            
            return {
                'success': True,
                'target_path': target_path,
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"从7Z提取文件失败: {source_path}, {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_tar_file(self, source_path: str, file_path: str, target_path: str) -> Dict[str, Any]:
        """从TAR中提取特定文件"""
        try:
            import tarfile
            
            with tarfile.open(source_path, 'r') as tar_ref:
                # 检查文件是否存在
                if file_path not in tar_ref.getnames():
                    return {
                        'success': False,
                        'error': '文件不存在于TAR中'
                    }
                
                # 提取文件
                member = tar_ref.getmember(file_path)
                with tar_ref.extractfile(member) as source_file:
                    with open(target_path, 'wb') as target_file:
                        shutil.copyfileobj(source_file, target_file)
            
            return {
                'success': True,
                'target_path': target_path,
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"从TAR提取文件失败: {source_path}, {file_path}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
