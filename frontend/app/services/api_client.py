"""
API客户端服务
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class APIClient(QObject):
    """API客户端"""
    
    # 信号定义
    request_started = pyqtSignal(str)  # 请求开始
    request_finished = pyqtSignal(str, bool)  # 请求完成 (url, success)
    error_occurred = pyqtSignal(str, str)  # 错误发生 (error_type, message)
    
    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self):
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.request_started.emit(url)
            
            session = await self._get_session()
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    self.request_finished.emit(url, True)
                    return data
                else:
                    error_msg = f"HTTP {response.status}: {await response.text()}"
                    self.error_occurred.emit("http_error", error_msg)
                    return {"error": error_msg}
                    
        except asyncio.TimeoutError:
            error_msg = f"请求超时: {url}"
            self.error_occurred.emit("timeout", error_msg)
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            self.error_occurred.emit("request_error", error_msg)
            return {"error": error_msg}
    
    async def get_files(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """获取文件列表"""
        return await self._make_request(
            "GET", 
            "/api/files/",
            params={"skip": skip, "limit": limit}
        )
    
    async def get_file_info(self, content_hash: str) -> Dict[str, Any]:
        """获取文件信息"""
        return await self._make_request("GET", f"/api/files/{content_hash}")
    
    async def start_scan(self, path: str) -> Dict[str, Any]:
        """开始扫描"""
        return await self._make_request(
            "POST",
            "/api/files/scan",
            json={"path": path}
        )
    
    async def get_scan_status(self) -> Dict[str, Any]:
        """获取扫描状态"""
        return await self._make_request("GET", "/api/files/scan/status")
    
    async def stop_scan(self) -> Dict[str, Any]:
        """停止扫描"""
        return await self._make_request("POST", "/api/files/scan/stop")
    
    async def search_files(self, query: str = "", **filters) -> Dict[str, Any]:
        """搜索文件"""
        params = {"q": query}
        params.update(filters)
        return await self._make_request("GET", "/api/search/", params=params)
    
    async def get_similar_files(self, content_hash: str, threshold: float = 0.8) -> Dict[str, Any]:
        """获取相似文件"""
        return await self._make_request(
            "GET",
            f"/api/search/similar/{content_hash}",
            params={"threshold": threshold}
        )
    
    async def get_search_suggestions(self, query: str) -> Dict[str, Any]:
        """获取搜索建议"""
        return await self._make_request(
            "GET",
            "/api/search/suggestions",
            params={"q": query}
        )
    
    async def get_preview(self, content_hash: str, size: str = "medium") -> Dict[str, Any]:
        """获取文件预览"""
        return await self._make_request(
            "GET",
            f"/api/preview/{content_hash}",
            params={"size": size}
        )
    
    async def generate_preview(self, content_hash: str) -> Dict[str, Any]:
        """生成文件预览"""
        return await self._make_request(
            "POST",
            f"/api/preview/generate/{content_hash}"
        )
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return await self._make_request("GET", "/api/admin/stats")
    
    async def get_jobs(self, status: str = None) -> Dict[str, Any]:
        """获取任务列表"""
        params = {}
        if status:
            params["status"] = status
        return await self._make_request("GET", "/api/admin/jobs", params=params)
    
    async def close(self):
        """关闭客户端"""
        if self.session and not self.session.closed:
            await self.session.close()
