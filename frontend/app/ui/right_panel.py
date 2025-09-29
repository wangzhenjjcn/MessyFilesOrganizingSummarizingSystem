"""
右侧面板 - 文件详情
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QTabWidget, QScrollArea, QGroupBox, QPushButton, QProgressBar,
    QListWidget, QSlider, QComboBox
)
from PySide6.QtCore import Qt, pyqtSignal
from PySide6.QtGui import QPixmap, QFont

class RightPanel(QWidget):
    """右侧面板 - 文件详情"""
    
    # 信号定义
    preview_requested = pyqtSignal(str)  # 预览请求
    similar_files_requested = pyqtSignal(str)  # 相似文件请求
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.setup_basic_info_tab()
        self.setup_preview_tab()
        self.setup_metadata_tab()
        self.setup_similar_tab()
        self.setup_relations_tab()
        
        # 创建操作按钮
        self.setup_action_buttons(layout)
    
    def setup_basic_info_tab(self):
        """设置基本信息标签页"""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)
        
        # 文件图标和名称
        self.file_icon_label = QLabel()
        self.file_icon_label.setAlignment(Qt.AlignCenter)
        self.file_icon_label.setFixedSize(64, 64)
        layout.addWidget(self.file_icon_label)
        
        self.file_name_label = QLabel("未选择文件")
        self.file_name_label.setAlignment(Qt.AlignCenter)
        self.file_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.file_name_label)
        
        # 基本信息组
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)
        
        self.size_label = QLabel("大小: -")
        self.type_label = QLabel("类型: -")
        self.modified_label = QLabel("修改时间: -")
        self.created_label = QLabel("创建时间: -")
        self.path_label = QLabel("路径: -")
        
        info_layout.addWidget(self.size_label)
        info_layout.addWidget(self.type_label)
        info_layout.addWidget(self.modified_label)
        info_layout.addWidget(self.created_label)
        info_layout.addWidget(self.path_label)
        
        layout.addWidget(info_group)
        
        # 标签组
        tags_group = QGroupBox("标签")
        tags_layout = QVBoxLayout(tags_group)
        
        self.tags_text = QTextEdit()
        self.tags_text.setMaximumHeight(100)
        self.tags_text.setReadOnly(True)
        tags_layout.addWidget(self.tags_text)
        
        layout.addWidget(tags_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(basic_widget, "基本信息")
    
    def setup_preview_tab(self):
        """设置预览标签页"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        # 预览区域
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)
        
        self.preview_label = QLabel("无预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(True)
        self.preview_scroll.setWidget(self.preview_label)
        
        layout.addWidget(self.preview_scroll)
        
        # 预览控制
        preview_controls = QHBoxLayout()
        
        self.generate_preview_button = QPushButton("生成预览")
        self.generate_preview_button.clicked.connect(self.handle_generate_preview)
        preview_controls.addWidget(self.generate_preview_button)
        
        self.preview_size_combo = QComboBox()
        self.preview_size_combo.addItems(["小", "中", "大"])
        self.preview_size_combo.setCurrentText("中")
        preview_controls.addWidget(QLabel("大小:"))
        preview_controls.addWidget(self.preview_size_combo)
        
        preview_controls.addStretch()
        
        layout.addLayout(preview_controls)
        
        # 预览进度
        self.preview_progress = QProgressBar()
        self.preview_progress.setVisible(False)
        layout.addWidget(self.preview_progress)
        
        self.tab_widget.addTab(preview_widget, "预览")
    
    def setup_metadata_tab(self):
        """设置元数据标签页"""
        metadata_widget = QWidget()
        layout = QVBoxLayout(metadata_widget)
        
        # 元数据显示
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.metadata_text)
        
        # 元数据操作
        metadata_controls = QHBoxLayout()
        
        self.refresh_metadata_button = QPushButton("刷新元数据")
        self.refresh_metadata_button.clicked.connect(self.handle_refresh_metadata)
        metadata_controls.addWidget(self.refresh_metadata_button)
        
        self.export_metadata_button = QPushButton("导出元数据")
        self.export_metadata_button.clicked.connect(self.handle_export_metadata)
        metadata_controls.addWidget(self.export_metadata_button)
        
        metadata_controls.addStretch()
        layout.addLayout(metadata_controls)
        
        self.tab_widget.addTab(metadata_widget, "元数据")
    
    def setup_similar_tab(self):
        """设置相似文件标签页"""
        similar_widget = QWidget()
        layout = QVBoxLayout(similar_widget)
        
        # 相似文件列表
        self.similar_list = QListWidget()
        layout.addWidget(self.similar_list)
        
        # 相似文件控制
        similar_controls = QHBoxLayout()
        
        self.find_similar_button = QPushButton("查找相似文件")
        self.find_similar_button.clicked.connect(self.handle_find_similar)
        similar_controls.addWidget(self.find_similar_button)
        
        self.similar_threshold_slider = QSlider(Qt.Horizontal)
        self.similar_threshold_slider.setRange(50, 100)
        self.similar_threshold_slider.setValue(80)
        self.similar_threshold_slider.valueChanged.connect(self.handle_threshold_changed)
        similar_controls.addWidget(QLabel("相似度:"))
        similar_controls.addWidget(self.similar_threshold_slider)
        
        self.threshold_label = QLabel("80%")
        similar_controls.addWidget(self.threshold_label)
        
        similar_controls.addStretch()
        layout.addLayout(similar_controls)
        
        self.tab_widget.addTab(similar_widget, "相似文件")
    
    def setup_relations_tab(self):
        """设置关系标签页"""
        relations_widget = QWidget()
        layout = QVBoxLayout(relations_widget)
        
        # 关系图显示
        self.relations_text = QTextEdit()
        self.relations_text.setReadOnly(True)
        self.relations_text.setFont(QFont("Arial", 10))
        layout.addWidget(self.relations_text)
        
        # 关系操作
        relations_controls = QHBoxLayout()
        
        self.refresh_relations_button = QPushButton("刷新关系")
        self.refresh_relations_button.clicked.connect(self.handle_refresh_relations)
        relations_controls.addWidget(self.refresh_relations_button)
        
        self.edit_relations_button = QPushButton("编辑关系")
        self.edit_relations_button.clicked.connect(self.handle_edit_relations)
        relations_controls.addWidget(self.edit_relations_button)
        
        relations_controls.addStretch()
        layout.addLayout(relations_controls)
        
        self.tab_widget.addTab(relations_widget, "关系")
    
    def setup_action_buttons(self, layout):
        """设置操作按钮"""
        action_layout = QHBoxLayout()
        
        self.open_file_button = QPushButton("打开文件")
        self.open_file_button.setEnabled(False)
        self.open_file_button.clicked.connect(self.handle_open_file)
        action_layout.addWidget(self.open_file_button)
        
        self.open_folder_button = QPushButton("打开文件夹")
        self.open_folder_button.setEnabled(False)
        self.open_folder_button.clicked.connect(self.handle_open_folder)
        action_layout.addWidget(self.open_folder_button)
        
        action_layout.addStretch()
        
        self.copy_path_button = QPushButton("复制路径")
        self.copy_path_button.setEnabled(False)
        self.copy_path_button.clicked.connect(self.handle_copy_path)
        action_layout.addWidget(self.copy_path_button)
        
        layout.addLayout(action_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.similar_threshold_slider.valueChanged.connect(self.handle_threshold_changed)
    
    def show_file_details(self, file_info: dict):
        """显示文件详情"""
        self.current_file = file_info
        self.update_basic_info(file_info)
        self.update_preview(file_info)
        self.update_metadata(file_info)
        self.update_relations(file_info)
        
        # 启用操作按钮
        self.open_file_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.copy_path_button.setEnabled(True)
    
    def update_basic_info(self, file_info: dict):
        """更新基本信息"""
        self.file_name_label.setText(file_info.get("name", "未知文件"))
        
        self.size_label.setText(f"大小: {file_info.get('size', '-')}")
        self.type_label.setText(f"类型: {file_info.get('type', '-')}")
        self.modified_label.setText(f"修改时间: {file_info.get('modified', '-')}")
        self.created_label.setText(f"创建时间: {file_info.get('created', '-')}")
        self.path_label.setText(f"路径: {file_info.get('path', '-')}")
        
        # 更新标签
        tags = file_info.get('tags', '')
        self.tags_text.setPlainText(tags)
    
    def update_preview(self, file_info: dict):
        """更新预览"""
        # TODO: 加载文件预览
        self.preview_label.setText("预览生成中...")
    
    def update_metadata(self, file_info: dict):
        """更新元数据"""
        metadata = file_info.get('metadata', {})
        metadata_text = ""
        for key, value in metadata.items():
            metadata_text += f"{key}: {value}\n"
        
        self.metadata_text.setPlainText(metadata_text or "无元数据")
    
    def update_relations(self, file_info: dict):
        """更新关系"""
        relations = file_info.get('relations', [])
        relations_text = ""
        for relation in relations:
            relations_text += f"{relation.get('type', '')}: {relation.get('target', '')}\n"
        
        self.relations_text.setPlainText(relations_text or "无关系")
    
    def handle_generate_preview(self):
        """处理生成预览"""
        if self.current_file:
            content_hash = self.current_file.get('content_hash')
            if content_hash:
                self.preview_requested.emit(content_hash)
    
    def handle_find_similar(self):
        """处理查找相似文件"""
        if self.current_file:
            content_hash = self.current_file.get('content_hash')
            if content_hash:
                self.similar_files_requested.emit(content_hash)
    
    def handle_threshold_changed(self, value):
        """处理相似度阈值变化"""
        self.threshold_label.setText(f"{value}%")
    
    def handle_refresh_metadata(self):
        """处理刷新元数据"""
        # TODO: 刷新元数据
        pass
    
    def handle_export_metadata(self):
        """处理导出元数据"""
        # TODO: 导出元数据
        pass
    
    def handle_refresh_relations(self):
        """处理刷新关系"""
        # TODO: 刷新关系
        pass
    
    def handle_edit_relations(self):
        """处理编辑关系"""
        # TODO: 编辑关系
        pass
    
    def handle_open_file(self):
        """处理打开文件"""
        if self.current_file:
            path = self.current_file.get('path')
            if path:
                import os
                os.startfile(path)
    
    def handle_open_folder(self):
        """处理打开文件夹"""
        if self.current_file:
            path = self.current_file.get('path')
            if path:
                import os
                folder = os.path.dirname(path)
                os.startfile(folder)
    
    def handle_copy_path(self):
        """处理复制路径"""
        if self.current_file:
            path = self.current_file.get('path')
            if path:
                from PySide6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(path)
