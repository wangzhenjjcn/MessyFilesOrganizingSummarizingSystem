#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本 - 使用清华源
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        print(f"[OK] 成功: {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 失败: {cmd}")
        print(f"错误: {e.stderr}")
        return False

def install_backend_deps():
    """安装后端依赖"""
    print("=" * 50)
    print("安装后端依赖...")
    print("=" * 50)
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("[ERROR] 后端目录不存在")
        return False
    
    # 使用清华源安装依赖
    cmd = f"pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/"
    return run_command(cmd, cwd=backend_dir)

def install_frontend_deps():
    """安装前端依赖"""
    print("=" * 50)
    print("安装前端依赖...")
    print("=" * 50)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("[ERROR] 前端目录不存在")
        return False
    
    # 使用清华源安装依赖
    cmd = f"pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/"
    return run_command(cmd, cwd=frontend_dir)

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[ERROR] Python版本过低: {version.major}.{version.minor}")
        print("需要Python 3.8或更高版本")
        return False
    
    print(f"[OK] Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def test_imports():
    """测试关键模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)
    
    test_modules = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "watchdog",
        "blake3",
        "PIL",
        "mutagen",
        "imagehash",
        "py7zr",
        "pdf2image",
        "docx",
        "PyPDF2",
        "librosa",
        "sklearn",
        "pycdlib",
        "psutil"
    ]
    
    failed_modules = []
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError as e:
            print(f"[ERROR] {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n失败的模块: {failed_modules}")
        return False
    
    print("\n[OK] 所有模块导入成功")
    return True

def main():
    """主函数"""
    print("文件整理和总结系统 - 依赖安装脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装后端依赖
    if not install_backend_deps():
        print("[ERROR] 后端依赖安装失败")
        return False
    
    # 安装前端依赖
    if not install_frontend_deps():
        print("[ERROR] 前端依赖安装失败")
        return False
    
    # 测试导入
    if not test_imports():
        print("[ERROR] 模块导入测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("[OK] 所有依赖安装完成！")
    print("=" * 50)
    
    print("\n下一步:")
    print("1. 启动后端: cd backend && python start_dev.py")
    print("2. 启动前端: cd frontend && python run.py")
    print("3. 运行测试: cd backend && python test_system.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
