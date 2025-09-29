# 文件整理和总结系统 - 启动指南

## 系统状态
✅ 所有依赖已安装完成  
✅ 所有模块导入正常  
✅ 数据库连接正常  
✅ FastAPI应用创建成功  

## 启动步骤

### 1. 启动后端服务器

#### 方法一：使用Python脚本启动（推荐）
```bash
cd backend
python run_server.py
```

#### 方法二：使用uvicorn命令启动
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方法三：使用开发脚本启动
```bash
cd backend
python start_dev.py
```

### 2. 启动前端应用

```bash
cd frontend
python run.py
```

### 3. 访问系统

- **API文档**: http://localhost:8000/docs
- **系统主页**: http://localhost:8000/
- **前端界面**: 运行前端应用后显示

## 故障排除

### 问题1：模块导入错误
**错误**: `ModuleNotFoundError: No module named 'app'`

**解决方案**:
1. 确保在backend目录下运行
2. 使用 `python run_server.py` 启动
3. 检查Python路径设置

### 问题2：端口被占用
**错误**: `Address already in use`

**解决方案**:
1. 检查8000端口是否被占用
2. 使用其他端口: `--port 8001`
3. 关闭占用端口的进程

### 问题3：依赖缺失
**错误**: `ImportError: No module named 'xxx'`

**解决方案**:
1. 重新安装依赖: `pip install -r requirements.txt`
2. 使用清华源: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

## 系统功能

### 后端API接口
- **文件管理**: `/api/files/`
- **搜索功能**: `/api/search/`
- **预览服务**: `/api/preview/`
- **动态集合**: `/api/savedview/`
- **容器文件**: `/api/container/`
- **规则引擎**: `/api/rules/`

### 前端功能
- **文件浏览**: 三栏布局界面
- **搜索过滤**: 实时搜索和过滤
- **预览显示**: 多媒体文件预览
- **智能管理**: 自动化规则处理

## 技术架构

### 后端技术栈
- **框架**: FastAPI + Uvicorn
- **数据库**: SQLite + SQLAlchemy + Alembic
- **文件监控**: Watchdog
- **哈希算法**: SHA-256
- **多媒体处理**: Pillow + Mutagen + ImageHash
- **文档处理**: PDF2Image + Python-docx + PyPDF2
- **容器处理**: Py7zr + Pycdlib
- **相似度算法**: Librosa + Scikit-learn

### 前端技术栈
- **UI框架**: PySide6 (Qt6)
- **HTTP客户端**: Requests + Httpx
- **图像处理**: Pillow
- **数据处理**: Pandas + Numpy

## 系统特色

### 核心功能
1. **智能文件扫描** - 跨平台文件监控
2. **全文搜索** - SQLite FTS5高性能搜索
3. **多媒体预览** - 图片、文档、音频、视频预览
4. **相似度检测** - 图片、音频、文档相似度算法
5. **动态集合** - 基于查询的文件集合
6. **容器提取** - ZIP、7Z、TAR、ISO等格式支持
7. **规则引擎** - IFTTT式自动化规则
8. **现代化界面** - PySide6三栏布局设计

### 性能优化
- **两级哈希系统** - 快速哈希 + 内容哈希
- **虚拟化列表** - 支持大量文件流畅显示
- **异步处理** - 非阻塞后台任务
- **智能缓存** - 预览和搜索结果缓存

## 使用说明

### 1. 文件扫描
- 启动后端后，访问 `/api/files/scan` 开始扫描
- 支持实时文件监控和批量扫描
- 自动计算文件哈希和元数据

### 2. 搜索文件
- 使用全文搜索功能查找文件
- 支持多维度过滤（类型、大小、时间等）
- 智能搜索建议和相似文件推荐

### 3. 预览功能
- 自动生成多媒体文件预览
- 支持多种尺寸和格式
- 智能缓存管理

### 4. 规则引擎
- 创建自动化规则处理文件
- 支持条件判断和动作执行
- 批量文件处理

## 开发说明

### 项目结构
```
项目根目录/
├── backend/          # 后端服务
│   ├── app/         # 应用代码
│   │   ├── models/  # 数据模型
│   │   ├── services/# 业务服务
│   │   ├── routers/ # API路由
│   │   └── main.py  # 主应用
│   ├── alembic/     # 数据库迁移
│   └── requirements.txt
├── frontend/        # 前端应用
│   ├── app/        # 应用代码
│   │   ├── ui/     # 用户界面
│   │   ├── services/# 服务模块
│   │   └── main.py # 主应用
│   └── requirements.txt
├── rules/          # 规则文档
├── doc/            # 文档中心
├── bat/            # 批处理脚本
├── task/           # 任务管理
└── history/        # 历史记录
```

### 开发环境
- **Python**: 3.8+
- **依赖管理**: pip + requirements.txt
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **版本控制**: Git

---

**系统状态**: ✅ 完全可用  
**启动状态**: ✅ 可立即启动  
**功能状态**: ✅ 全部实现
