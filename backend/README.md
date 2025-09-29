# 文件整理和总结系统 - 后端

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 主应用
│   ├── database.py          # 数据库配置
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── blobs.py         # 内容实体
│   │   ├── assets.py        # 位置实体
│   │   ├── containers.py    # 容器文件
│   │   ├── tags.py          # 标签系统
│   │   ├── entities.py      # 业务实体
│   │   ├── relations.py     # 关系映射
│   │   ├── saved_views.py   # 动态集合
│   │   ├── jobs.py          # 任务队列
│   │   └── audits.py        # 审计记录
│   └── routers/             # API 路由
│       ├── __init__.py
│       ├── files.py         # 文件管理
│       ├── search.py        # 搜索功能
│       ├── preview.py      # 预览服务
│       └── admin.py        # 管理功能
├── alembic/                 # 数据库迁移
├── requirements.txt         # 依赖包
├── run.py                  # 启动脚本
└── init_db.py              # 数据库初始化
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

### 3. 启动服务

```bash
python run.py
```

服务将在 http://localhost:8000 启动

## API 文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库模型

### 核心表结构

- **Blobs**: 内容实体，以 content_hash 为唯一标识
- **Assets**: 位置实体，记录文件的物理位置
- **Containers**: 容器文件（压缩包、镜像等）
- **Tags**: 标签系统
- **Relations**: 文件间关系
- **SavedViews**: 动态集合
- **Jobs**: 任务队列
- **Audits**: 审计记录

### 关键特性

1. **两级哈希**: fast_hash (BLAKE3) + content_hash (SHA-256)
2. **跨平台支持**: Windows, macOS, Linux
3. **增量扫描**: 基于文件系统事件
4. **全文搜索**: SQLite FTS5
5. **预览服务**: 多媒体文件预览
6. **关系推断**: 自动发现文件关系

## 开发指南

### 添加新模型

1. 在 `app/models/` 中创建新模型文件
2. 在 `app/models/__init__.py` 中导入
3. 运行数据库迁移

### 添加新API

1. 在 `app/routers/` 中创建新路由文件
2. 在 `app/main.py` 中注册路由
3. 添加相应的数据模型和业务逻辑

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```
