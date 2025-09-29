"""
数据库初始化脚本
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.database import engine, Base
from app.models import *

def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_database()
