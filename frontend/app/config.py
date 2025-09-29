"""
应用配置管理
"""
import os
from pathlib import Path
from pydantic import BaseSettings

class Config(BaseSettings):
    """应用配置"""
    
    # API配置
    api_base_url: str = "http://localhost:8000"
    api_timeout: int = 30
    
    # 应用配置
    app_name: str = "文件整理和总结系统"
    app_version: str = "1.0.0"
    
    # 界面配置
    window_width: int = 1200
    window_height: int = 800
    window_min_width: int = 800
    window_min_height: int = 600
    
    # 文件配置
    max_file_size_mb: int = 100  # 最大文件大小（MB）
    supported_extensions: list = [
        '.txt', '.md', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
        '.mp3', '.wav', '.flac', '.aac', '.ogg',
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
        '.zip', '.rar', '.7z', '.tar', '.gz'
    ]
    
    # 扫描配置
    scan_batch_size: int = 100  # 批量扫描文件数
    scan_timeout: int = 300  # 扫描超时时间（秒）
    
    # 预览配置
    preview_max_size: int = 1024  # 预览图最大尺寸
    preview_quality: int = 85  # 预览图质量
    
    # 缓存配置
    cache_dir: str = str(Path.home() / ".file_organizer" / "cache")
    cache_max_size_mb: int = 500  # 缓存最大大小（MB）
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = str(Path.home() / ".file_organizer" / "logs" / "app.log")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保缓存和日志目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
