"""
前端应用启动脚本
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from app.main import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
