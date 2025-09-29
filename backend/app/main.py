"""
文件整理和总结系统 - 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import files, search, preview, admin

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="文件整理和总结系统",
    description="智能文件管理和总结系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(files.router, prefix="/api/files", tags=["文件管理"])
app.include_router(search.router, prefix="/api/search", tags=["搜索"])
app.include_router(preview.router, prefix="/api/preview", tags=["预览"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理"])

@app.get("/")
async def root():
    return {"message": "文件整理和总结系统 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
