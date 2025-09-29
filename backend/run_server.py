#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器启动脚本
"""
import os
import sys
import uvicorn

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动服务器"""
    print("文件整理和总结系统 - 服务器启动")
    print("=" * 50)
    print("服务器地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"[ERROR] 启动服务器失败: {e}")

if __name__ == "__main__":
    main()
