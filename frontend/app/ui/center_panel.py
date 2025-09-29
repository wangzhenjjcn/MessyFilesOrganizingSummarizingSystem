"""
中央面板 - 文件列表
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, pyqtSignal, QTimer
from PySide6.QtGui import QIcon, QFont
import asyncio

class CenterPanel(QWidget):
    """中央面板 - 文件列表"""
    
    # 信号定义
    file_selected = pyqtSignal(dict)  # 文件选择
    
    def __init__(self):
        super().__init__()
        self.current_files = []
        self.current_query = ""
        self.current_filters = {}
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 创建工具栏
        self.setup_toolbar(layout)
        
        # 创建表格
        self.setup_table(layout)
        
        # 创建分页控件
        self.setup_pagination(layout)
    
    def setup_toolbar(self, layout):
        """设置工具栏"""
        toolbar_layout = QHBoxLayout()
        
        # 视图模式选择
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["列表视图", "网格视图", "详细信息"])
        toolbar_layout.addWidget(QLabel("视图:"))
        toolbar_layout.addWidget(self.view_mode_combo)
        
        toolbar_layout.addStretch()
        
        # 排序选择
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["名称", "大小", "修改时间", "类型"])
        toolbar_layout.addWidget(QLabel("排序:"))
        toolbar_layout.addWidget(self.sort_combo)
        
        # 排序方向
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["升序", "降序"])
        toolbar_layout.addWidget(self.sort_order_combo)
        
        toolbar_layout.addStretch()
        
        # 选择模式
        self.selection_mode_combo = QComboBox()
        self.selection_mode_combo.addItems(["单选", "多选"])
        toolbar_layout.addWidget(QLabel("选择:"))
        toolbar_layout.addWidget(self.selection_mode_combo)
        
        layout.addLayout(toolbar_layout)
    
    def setup_table(self, layout):
        """设置表格"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "名称", "大小", "类型", "修改时间", "路径", "标签"
        ])
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 名称列自适应
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 大小列
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 类型列
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 时间列
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # 路径列自适应
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 标签列
        
        layout.addWidget(self.table)
    
    def setup_pagination(self, layout):
        """设置分页控件"""
        pagination_layout = QHBoxLayout()
        
        # 页面信息
        self.page_info_label = QLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_info_label)
        
        pagination_layout.addStretch()
        
        # 每页数量选择
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "500"])
        self.page_size_combo.setCurrentText("100")
        pagination_layout.addWidget(QLabel("每页:"))
        pagination_layout.addWidget(self.page_size_combo)
        
        # 导航按钮
        self.prev_button = QPushButton("上一页")
        self.prev_button.setEnabled(False)
        pagination_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("下一页")
        self.next_button.setEnabled(False)
        pagination_layout.addWidget(self.next_button)
        
        layout.addLayout(pagination_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.table.itemSelectionChanged.connect(self.handle_selection_changed)
        self.table.cellDoubleClicked.connect(self.handle_double_click)
        
        self.view_mode_combo.currentTextChanged.connect(self.handle_view_mode_changed)
        self.sort_combo.currentTextChanged.connect(self.handle_sort_changed)
        self.sort_order_combo.currentTextChanged.connect(self.handle_sort_changed)
        self.selection_mode_combo.currentTextChanged.connect(self.handle_selection_mode_changed)
        
        self.page_size_combo.currentTextChanged.connect(self.handle_page_size_changed)
        self.prev_button.clicked.connect(self.handle_prev_page)
        self.next_button.clicked.connect(self.handle_next_page)
    
    def handle_selection_changed(self):
        """处理选择变化"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            if row < len(self.current_files):
                file_info = self.current_files[row]
                self.file_selected.emit(file_info)
    
    def handle_double_click(self, row: int, column: int):
        """处理双击"""
        if row < len(self.current_files):
            file_info = self.current_files[row]
            # TODO: 打开文件或显示详细信息
            self.file_selected.emit(file_info)
    
    def handle_view_mode_changed(self, mode: str):
        """处理视图模式变化"""
        # TODO: 实现不同的视图模式
        pass
    
    def handle_sort_changed(self):
        """处理排序变化"""
        self.refresh_files()
    
    def handle_selection_mode_changed(self, mode: str):
        """处理选择模式变化"""
        if mode == "多选":
            self.table.setSelectionMode(QTableWidget.MultiSelection)
        else:
            self.table.setSelectionMode(QTableWidget.SingleSelection)
    
    def handle_page_size_changed(self, size: str):
        """处理页面大小变化"""
        self.refresh_files()
    
    def handle_prev_page(self):
        """处理上一页"""
        # TODO: 实现分页逻辑
        pass
    
    def handle_next_page(self):
        """处理下一页"""
        # TODO: 实现分页逻辑
        pass
    
    def search_files(self, query: str, filters: dict):
        """搜索文件"""
        self.current_query = query
        self.current_filters = filters
        self.refresh_files()
    
    def refresh_files(self):
        """刷新文件列表"""
        # TODO: 从API获取文件列表
        # 这里先显示一些示例数据
        self.load_sample_data()
    
    def load_sample_data(self):
        """加载示例数据"""
        sample_files = [
            {
                "name": "document1.pdf",
                "size": "2.5 MB",
                "type": "PDF文档",
                "modified": "2024-01-01 10:30:00",
                "path": "C:\\Users\\Documents\\document1.pdf",
                "tags": "工作,重要"
            },
            {
                "name": "image1.jpg",
                "size": "1.2 MB",
                "type": "JPEG图片",
                "modified": "2024-01-01 09:15:00",
                "path": "C:\\Users\\Pictures\\image1.jpg",
                "tags": "照片,个人"
            },
            {
                "name": "video1.mp4",
                "size": "150 MB",
                "type": "MP4视频",
                "modified": "2024-01-01 08:45:00",
                "path": "D:\\Videos\\video1.mp4",
                "tags": "娱乐,高清"
            }
        ]
        
        self.current_files = sample_files
        self.update_table(sample_files)
    
    def update_table(self, files: list):
        """更新表格"""
        self.table.setRowCount(len(files))
        
        for row, file_info in enumerate(files):
            # 名称
            name_item = QTableWidgetItem(file_info.get("name", ""))
            name_item.setIcon(self.get_file_icon(file_info.get("type", "")))
            self.table.setItem(row, 0, name_item)
            
            # 大小
            self.table.setItem(row, 1, QTableWidgetItem(file_info.get("size", "")))
            
            # 类型
            self.table.setItem(row, 2, QTableWidgetItem(file_info.get("type", "")))
            
            # 修改时间
            self.table.setItem(row, 3, QTableWidgetItem(file_info.get("modified", "")))
            
            # 路径
            self.table.setItem(row, 4, QTableWidgetItem(file_info.get("path", "")))
            
            # 标签
            self.table.setItem(row, 5, QTableWidgetItem(file_info.get("tags", "")))
    
    def get_file_icon(self, file_type: str) -> QIcon:
        """获取文件图标"""
        # TODO: 根据文件类型返回相应图标
        return QIcon(":/icons/file.png")
    
    def get_selected_files(self) -> list:
        """获取选中的文件"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        return [self.current_files[row] for row in selected_rows if row < len(self.current_files)]
