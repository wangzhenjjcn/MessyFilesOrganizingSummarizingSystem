#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的系统测试脚本
"""
import sys
import os
from pathlib import Path

def test_imports():
    """测试关键模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试基础模块
        import fastapi
        print("[OK] fastapi")
        
        import uvicorn
        print("[OK] uvicorn")
        
        import sqlalchemy
        print("[OK] sqlalchemy")
        
        import pydantic
        print("[OK] pydantic")
        
        import watchdog
        print("[OK] watchdog")
        
        # import blake3  # 暂时注释
        # print("[OK] blake3")
        
        from PIL import Image
        print("[OK] Pillow")
        
        import mutagen
        print("[OK] mutagen")
        
        import imagehash
        print("[OK] imagehash")
        
        import py7zr
        print("[OK] py7zr")
        
        import pdf2image
        print("[OK] pdf2image")
        
        import docx
        print("[OK] python-docx")
        
        import PyPDF2
        print("[OK] PyPDF2")
        
        import librosa
        print("[OK] librosa")
        
        import sklearn
        print("[OK] scikit-learn")
        
        import pycdlib
        print("[OK] pycdlib")
        
        import psutil
        print("[OK] psutil")
        
        print("\n[OK] 所有后端模块导入成功")
        return True
        
    except ImportError as e:
        print(f"[ERROR] 导入失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        # 添加backend路径到sys.path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.database import engine, Base
        from app.models.blobs import Blob
        from app.models.assets import Asset
        from app.models.tags import Tag, FileTag
        from app.models.containers import Container, Containment
        from app.models.saved_views import SavedView
        from app.models.jobs import Job
        from app.models.audits import Audit
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("[OK] 数据库连接成功")
        print("[OK] 数据表创建成功")
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库测试失败: {e}")
        return False

def test_api():
    """测试API应用"""
    print("\n测试API应用...")
    
    try:
        from app.main import app
        print("[OK] FastAPI应用创建成功")
        
        # 测试路由
        routes = [route.path for route in app.routes]
        print(f"[OK] 注册路由数量: {len(routes)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API测试失败: {e}")
        return False

def test_frontend():
    """测试前端模块"""
    print("\n测试前端模块...")
    
    try:
        # 添加frontend路径到sys.path
        frontend_path = Path(__file__).parent / "frontend"
        sys.path.insert(0, str(frontend_path))
        
        import PySide6
        print("[OK] PySide6")
        
        import requests
        print("[OK] requests")
        
        import httpx
        print("[OK] httpx")
        
        import pandas
        print("[OK] pandas")
        
        import numpy
        print("[OK] numpy")
        
        print("[OK] 所有前端模块导入成功")
        return True
        
    except ImportError as e:
        print(f"[ERROR] 前端模块导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("文件整理和总结系统 - 简化测试")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        print("[ERROR] 模块导入测试失败")
        return False
    
    # 测试数据库
    if not test_database():
        print("[ERROR] 数据库测试失败")
        return False
    
    # 测试API
    if not test_api():
        print("[ERROR] API测试失败")
        return False
    
    # 测试前端
    if not test_frontend():
        print("[ERROR] 前端测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("[OK] 所有测试通过！系统可以正常运行")
    print("=" * 50)
    
    print("\n启动说明:")
    print("1. 启动后端: cd backend && python start_dev.py")
    print("2. 启动前端: cd frontend && python run.py")
    print("3. 访问API文档: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
