#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器启动
"""
import sys
import os
from pathlib import Path

def test_server_start():
    """测试服务器启动"""
    print("测试服务器启动...")
    
    try:
        # 确保backend目录在PYTHONPATH中
        backend_path = Path(__file__).parent / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        # 测试导入
        from app.main import app
        print("[OK] FastAPI应用导入成功")
        
        # 测试数据库连接
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("[OK] 数据库连接成功")
        
        # 测试启动服务器
        import uvicorn
        print("正在启动服务器...")
        print("服务器地址: http://127.0.0.1:8000")
        print("API文档: http://127.0.0.1:8000/docs")
        print("按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        
    except Exception as e:
        print(f"[ERROR] 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_server_start()
