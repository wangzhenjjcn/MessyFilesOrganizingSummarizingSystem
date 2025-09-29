#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试启动脚本
"""
import sys
import os

def test_imports():
    """测试导入"""
    try:
        print("测试导入...")
        
        from app.database import engine, Base
        print("[OK] 数据库模块导入成功")
        
        from app.models.blobs import Blob
        from app.models.assets import Asset
        from app.models.tags import Tag, FileTag
        from app.models.containers import Container, Containment
        from app.models.saved_views import SavedView
        from app.models.jobs import Job
        from app.models.audits import Audit
        from app.models.entities import Entity
        from app.models.relations import Relation
        print("[OK] 数据模型导入成功")
        
        from app.main import app
        print("[OK] FastAPI应用导入成功")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库"""
    try:
        print("\n测试数据库...")
        
        from app.database import engine, Base
        from app.models.blobs import Blob
        from app.models.assets import Asset
        from app.models.tags import Tag, FileTag
        from app.models.containers import Container, Containment
        from app.models.saved_views import SavedView
        from app.models.jobs import Job
        from app.models.audits import Audit
        from app.models.entities import Entity
        from app.models.relations import Relation
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("[OK] 数据库表创建成功")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("文件整理和总结系统 - 测试启动")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("[ERROR] 导入测试失败")
        return False
    
    # 测试数据库
    if not test_database():
        print("[ERROR] 数据库测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("[OK] 所有测试通过！系统可以正常启动")
    print("=" * 50)
    
    print("\n启动命令:")
    print("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
