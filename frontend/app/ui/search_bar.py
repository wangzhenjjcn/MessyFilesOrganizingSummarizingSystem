"""
搜索栏
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, 
    QComboBox, QSpinBox, QCheckBox, QLabel
)
from PySide6.QtCore import Qt, pyqtSignal, QTimer
from PySide6.QtGui import QIcon

class SearchBar(QWidget):
    """搜索栏"""
    
    # 信号定义
    search_requested = pyqtSignal(str, dict)  # 搜索请求 (query, filters)
    
    def __init__(self):
        super().__init__()
        self.current_query = ""
        self.current_filters = {}
        
        self.init_ui()
        self.setup_connections()
        self.setup_timer()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件...")
        self.search_input.setMinimumWidth(200)
        layout.addWidget(self.search_input)
        
        # 搜索按钮
        self.search_button = QPushButton("搜索")
        self.search_button.setIcon(QIcon(":/icons/search.png"))
        layout.addWidget(self.search_button)
        
        # 清除按钮
        self.clear_button = QPushButton("清除")
        self.clear_button.setIcon(QIcon(":/icons/clear.png"))
        layout.addWidget(self.clear_button)
        
        layout.addWidget(QLabel("|"))  # 分隔符
        
        # 文件类型过滤
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["所有类型", "图片", "视频", "音频", "文档", "压缩包"])
        layout.addWidget(QLabel("类型:"))
        layout.addWidget(self.file_type_combo)
        
        # 文件大小过滤
        self.size_min_spin = QSpinBox()
        self.size_min_spin.setRange(0, 10000)
        self.size_min_spin.setSuffix(" MB")
        self.size_min_spin.setValue(0)
        layout.addWidget(QLabel("最小:"))
        layout.addWidget(self.size_min_spin)
        
        self.size_max_spin = QSpinBox()
        self.size_max_spin.setRange(0, 10000)
        self.size_max_spin.setSuffix(" MB")
        self.size_max_spin.setValue(10000)
        layout.addWidget(QLabel("最大:"))
        layout.addWidget(self.size_max_spin)
        
        # 扩展名过滤
        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText("扩展名")
        self.extension_input.setMaximumWidth(100)
        layout.addWidget(QLabel("扩展名:"))
        layout.addWidget(self.extension_input)
        
        # 高级搜索按钮
        self.advanced_button = QPushButton("高级")
        self.advanced_button.setCheckable(True)
        layout.addWidget(self.advanced_button)
        
        # 保存搜索按钮
        self.save_search_button = QPushButton("保存搜索")
        self.save_search_button.setIcon(QIcon(":/icons/save.png"))
        layout.addWidget(self.save_search_button)
    
    def setup_connections(self):
        """设置信号连接"""
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_button.clicked.connect(self.perform_search)
        self.clear_button.clicked.connect(self.clear_search)
        
        self.file_type_combo.currentTextChanged.connect(self.on_filter_changed)
        self.size_min_spin.valueChanged.connect(self.on_filter_changed)
        self.size_max_spin.valueChanged.connect(self.on_filter_changed)
        self.extension_input.textChanged.connect(self.on_filter_changed)
        
        self.advanced_button.toggled.connect(self.toggle_advanced_search)
        self.save_search_button.clicked.connect(self.save_search)
    
    def setup_timer(self):
        """设置定时器"""
        # 搜索延迟定时器
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
    
    def perform_search(self):
        """执行搜索"""
        query = self.search_input.text().strip()
        filters = self.get_filters()
        
        self.current_query = query
        self.current_filters = filters
        
        self.search_requested.emit(query, filters)
    
    def clear_search(self):
        """清除搜索"""
        self.search_input.clear()
        self.file_type_combo.setCurrentIndex(0)
        self.size_min_spin.setValue(0)
        self.size_max_spin.setValue(10000)
        self.extension_input.clear()
        
        self.current_query = ""
        self.current_filters = {}
        
        self.search_requested.emit("", {})
    
    def get_filters(self) -> dict:
        """获取过滤条件"""
        filters = {}
        
        # 文件类型过滤
        file_type = self.file_type_combo.currentText()
        if file_type != "所有类型":
            type_mapping = {
                "图片": "image",
                "视频": "video", 
                "音频": "audio",
                "文档": "document",
                "压缩包": "archive"
            }
            if file_type in type_mapping:
                filters["file_type"] = type_mapping[file_type]
        
        # 文件大小过滤
        min_size = self.size_min_spin.value()
        max_size = self.size_max_spin.value()
        
        if min_size > 0:
            filters["min_size"] = min_size * 1024 * 1024  # 转换为字节
        
        if max_size < 10000:
            filters["max_size"] = max_size * 1024 * 1024  # 转换为字节
        
        # 扩展名过滤
        extension = self.extension_input.text().strip()
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            filters["extension"] = extension
        
        return filters
    
    def on_filter_changed(self):
        """过滤条件变化"""
        # 延迟搜索，避免频繁请求
        self.search_timer.start(500)  # 500ms延迟
    
    def toggle_advanced_search(self, checked: bool):
        """切换高级搜索"""
        # TODO: 显示/隐藏高级搜索选项
        pass
    
    def save_search(self):
        """保存搜索"""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, 
            "保存搜索", 
            "请输入搜索名称:"
        )
        
        if ok and name:
            # TODO: 保存搜索到API
            pass
    
    def set_search(self, query: str, filters: dict = None):
        """设置搜索条件"""
        self.search_input.setText(query)
        
        if filters:
            # 设置文件类型
            if "file_type" in filters:
                type_mapping = {
                    "image": "图片",
                    "video": "视频",
                    "audio": "音频", 
                    "document": "文档",
                    "archive": "压缩包"
                }
                file_type = filters["file_type"]
                if file_type in type_mapping:
                    index = self.file_type_combo.findText(type_mapping[file_type])
                    if index >= 0:
                        self.file_type_combo.setCurrentIndex(index)
            
            # 设置文件大小
            if "min_size" in filters:
                min_size_mb = filters["min_size"] // (1024 * 1024)
                self.size_min_spin.setValue(min_size_mb)
            
            if "max_size" in filters:
                max_size_mb = filters["max_size"] // (1024 * 1024)
                self.size_max_spin.setValue(max_size_mb)
            
            # 设置扩展名
            if "extension" in filters:
                self.extension_input.setText(filters["extension"])
    
    def get_current_search(self) -> tuple:
        """获取当前搜索条件"""
        return self.current_query, self.current_filters
