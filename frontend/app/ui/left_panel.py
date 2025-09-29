"""
左侧面板 - 源、标签、集合
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, pyqtSignal
from PySide6.QtGui import QIcon

class LeftPanel(QWidget):
    """左侧面板"""
    
    # 信号定义
    scan_requested = pyqtSignal(str)  # 扫描请求
    source_selected = pyqtSignal(str)  # 源选择
    tag_selected = pyqtSignal(str)  # 标签选择
    collection_selected = pyqtSignal(str)  # 集合选择
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 创建树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("文件库")
        self.tree.setRootIsDecorated(True)
        layout.addWidget(self.tree)
        
        # 创建根节点
        self.setup_tree_structure()
        
        # 创建操作按钮
        self.setup_action_buttons(layout)
    
    def setup_tree_structure(self):
        """设置树形结构"""
        # 源节点
        self.sources_item = QTreeWidgetItem(self.tree, ["源"])
        self.sources_item.setIcon(0, QIcon(":/icons/folder.png"))
        
        # 标签节点
        self.tags_item = QTreeWidgetItem(self.tree, ["标签"])
        self.tags_item.setIcon(0, QIcon(":/icons/tag.png"))
        
        # 集合节点
        self.collections_item = QTreeWidgetItem(self.tree, ["动态集合"])
        self.collections_item.setIcon(0, QIcon(":/icons/collection.png"))
        
        # 规则节点
        self.rules_item = QTreeWidgetItem(self.tree, ["规则"])
        self.rules_item.setIcon(0, QIcon(":/icons/rule.png"))
        
        # 展开所有节点
        self.tree.expandAll()
    
    def setup_action_buttons(self, layout):
        """设置操作按钮"""
        # 扫描按钮
        self.scan_button = QPushButton("扫描文件夹")
        self.scan_button.setIcon(QIcon(":/icons/scan.png"))
        layout.addWidget(self.scan_button)
        
        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setIcon(QIcon(":/icons/refresh.png"))
        layout.addWidget(self.refresh_button)
        
        # 添加集合按钮
        self.add_collection_button = QPushButton("新建集合")
        self.add_collection_button.setIcon(QIcon(":/icons/add.png"))
        layout.addWidget(self.add_collection_button)
    
    def setup_connections(self):
        """设置信号连接"""
        self.tree.itemClicked.connect(self.handle_item_clicked)
        self.scan_button.clicked.connect(self.handle_scan_clicked)
        self.refresh_button.clicked.connect(self.refresh_sources)
        self.add_collection_button.clicked.connect(self.handle_add_collection)
    
    def handle_item_clicked(self, item: QTreeWidgetItem, column: int):
        """处理项目点击"""
        if item.parent() is None:
            return  # 根节点
        
        parent = item.parent()
        if parent == self.sources_item:
            self.source_selected.emit(item.text(0))
        elif parent == self.tags_item:
            self.tag_selected.emit(item.text(0))
        elif parent == self.collections_item:
            self.collection_selected.emit(item.text(0))
    
    def handle_scan_clicked(self):
        """处理扫描按钮点击"""
        from PySide6.QtWidgets import QFileDialog
        
        path = QFileDialog.getExistingDirectory(
            self, 
            "选择要扫描的文件夹",
            ""
        )
        
        if path:
            self.scan_requested.emit(path)
    
    def handle_add_collection(self):
        """处理添加集合"""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, 
            "新建集合", 
            "请输入集合名称:"
        )
        
        if ok and name:
            # TODO: 创建新集合
            self.add_collection_item(name)
    
    def add_source_item(self, path: str, name: str = None):
        """添加源项目"""
        if name is None:
            name = path.split('/')[-1] or path.split('\\')[-1]
        
        item = QTreeWidgetItem(self.sources_item, [name])
        item.setIcon(0, QIcon(":/icons/folder.png"))
        item.setData(0, Qt.UserRole, path)
        
        return item
    
    def add_tag_item(self, tag_name: str, count: int = 0):
        """添加标签项目"""
        display_text = f"{tag_name} ({count})" if count > 0 else tag_name
        
        item = QTreeWidgetItem(self.tags_item, [display_text])
        item.setIcon(0, QIcon(":/icons/tag.png"))
        item.setData(0, Qt.UserRole, tag_name)
        
        return item
    
    def add_collection_item(self, name: str):
        """添加集合项目"""
        item = QTreeWidgetItem(self.collections_item, [name])
        item.setIcon(0, QIcon(":/icons/collection.png"))
        item.setData(0, Qt.UserRole, name)
        
        return item
    
    def refresh_sources(self):
        """刷新源列表"""
        # 清空现有源
        self.sources_item.takeChildren()
        
        # TODO: 从API获取源列表
        # 这里先添加一些示例数据
        self.add_source_item("C:\\Users\\Documents", "Documents")
        self.add_source_item("D:\\Projects", "Projects")
    
    def refresh_tags(self):
        """刷新标签列表"""
        # 清空现有标签
        self.tags_item.takeChildren()
        
        # TODO: 从API获取标签列表
        # 这里先添加一些示例数据
        self.add_tag_item("图片", 150)
        self.add_tag_item("文档", 200)
        self.add_tag_item("视频", 50)
    
    def refresh_collections(self):
        """刷新集合列表"""
        # 清空现有集合
        self.collections_item.takeChildren()
        
        # TODO: 从API获取集合列表
        # 这里先添加一些示例数据
        self.add_collection_item("最近文件")
        self.add_collection_item("大文件")
        self.add_collection_item("重复文件")
    
    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_sources()
        self.refresh_tags()
        self.refresh_collections()
