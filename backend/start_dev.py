"""
开发环境启动脚本
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖"""
    try:
        import fastapi
        import sqlalchemy
        # import blake3  # 暂时注释
        print("[OK] 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"[ERROR] 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def init_database():
    """初始化数据库"""
    try:
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
        
        print("正在初始化数据库...")
        Base.metadata.create_all(bind=engine)
        print("[OK] 数据库初始化完成")
        return True
    except Exception as e:
        print(f"[ERROR] 数据库初始化失败: {e}")
        return False

def start_server():
    """启动服务器"""
    try:
        print("正在启动服务器...")
        print("服务器地址: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"[ERROR] 启动服务器失败: {e}")

def main():
    """主函数"""
    print("文件整理和总结系统 - 开发环境")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 初始化数据库
    if not init_database():
        return
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
