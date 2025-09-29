# 文件整理和总结系统 - 前端

## 项目结构

```
frontend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 主应用入口
│   ├── config.py            # 配置管理
│   ├── services/            # 服务模块
│   │   ├── __init__.py
│   │   └── api_client.py     # API客户端
│   └── ui/                  # 用户界面
│       ├── __init__.py
│       ├── main_window.py   # 主窗口
│       ├── left_panel.py     # 左侧面板
│       ├── center_panel.py   # 中央面板
│       ├── right_panel.py   # 右侧面板
│       └── search_bar.py    # 搜索栏
├── requirements.txt         # 依赖包
└── run.py                  # 启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动前端应用

```bash
python run.py
```

### 3. 确保后端服务运行

前端需要后端API服务支持，请确保后端服务在 http://localhost:8000 运行。

## 功能特性

### 主界面布局
- **左侧面板**: 源、标签、动态集合、规则管理
- **中央面板**: 文件列表，支持多种视图模式
- **右侧面板**: 文件详情，包括预览、元数据、相似文件、关系图
- **顶部搜索栏**: 智能搜索，支持多种过滤条件

### 核心功能
1. **文件浏览**: 虚拟化表格，支持大量文件流畅显示
2. **智能搜索**: 全文搜索，支持类型、大小、扩展名过滤
3. **文件预览**: 多媒体文件预览生成
4. **相似文件**: 基于感知哈希和音频指纹的相似文件检测
5. **关系管理**: 文件间关系可视化和编辑
6. **动态集合**: 保存的搜索查询，支持软链接导出

### 技术特性
- **PySide6**: 现代Qt6 Python绑定
- **异步API**: 基于aiohttp的异步HTTP客户端
- **响应式UI**: 支持窗口大小调整和布局自适应
- **主题支持**: 现代化Material Design风格
- **国际化**: 支持多语言界面

## 开发指南

### 添加新UI组件

1. 在 `app/ui/` 中创建新组件文件
2. 继承适当的Qt基类
3. 在 `main_window.py` 中集成新组件

### 添加新API接口

1. 在 `app/services/api_client.py` 中添加新方法
2. 在相应的UI组件中调用API方法
3. 处理异步响应和错误

### 配置管理

修改 `app/config.py` 中的配置项，支持环境变量覆盖：

```python
# .env 文件
API_BASE_URL=http://localhost:8000
WINDOW_WIDTH=1400
WINDOW_HEIGHT=900
```

## 构建和部署

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py
```

### 生产环境

```bash
# 使用PyInstaller打包
pip install pyinstaller
pyinstaller --onefile --windowed run.py

# 或使用cx_Freeze
pip install cx_freeze
python setup.py build
```

## 故障排除

### 常见问题

1. **API连接失败**: 检查后端服务是否运行在正确端口
2. **界面显示异常**: 检查PySide6版本兼容性
3. **搜索无结果**: 确认后端数据库已初始化并包含数据

### 调试模式

设置环境变量启用调试模式：

```bash
export DEBUG=1
python run.py
```

## 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

## 许可证

MIT License
