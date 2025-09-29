"""
主窗口
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QStatusBar, QMenuBar, QMenu, QToolBar,
    QMessageBox, QProgressBar, QLabel
)
from PySide6.QtCore import Qt, QTimer, pyqtSignal
from PySide6.QtGui import QAction, QIcon

from app.ui.left_panel import LeftPanel
from app.ui.center_panel import CenterPanel
from app.ui.right_panel import RightPanel
from app.ui.search_bar import SearchBar
from app.services.api_client import APIClient

class MainWindow(QMainWindow):
    """主窗口"""
    
    # 信号定义
    file_selected = pyqtSignal(dict)  # 文件选择
    search_requested = pyqtSignal(str, dict)  # 搜索请求
    scan_requested = pyqtSignal(str)  # 扫描请求
    
    def __init__(self, api_client: APIClient, config):
        super().__init__()
        self.api_client = api_client
        self.config = config
        
        # 初始化UI
        self.init_ui()
        
        # 设置窗口属性
        self.setup_window()
        
        # 连接信号
        self.setup_connections()
        
        # 启动定时器
        self.setup_timers()
    
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建搜索栏
        self.search_bar = SearchBar()
        main_layout.addWidget(self.search_bar)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # 创建三个面板
        self.left_panel = LeftPanel()
        self.center_panel = CenterPanel()
        self.right_panel = RightPanel()
        
        # 添加到分割器
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.center_panel)
        self.splitter.addWidget(self.right_panel)
        
        # 设置分割器比例
        self.splitter.setSizes([200, 600, 300])
        
        # 创建状态栏
        self.setup_status_bar()
        
        # 创建菜单栏
        self.setup_menu_bar()
        
        # 创建工具栏
        self.setup_tool_bar()
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle(f"{self.config.app_name} v{self.config.app_version}")
        self.resize(self.config.window_width, self.config.window_height)
        self.setMinimumSize(self.config.window_min_width, self.config.window_min_height)
        
        # 设置窗口图标
        # self.setWindowIcon(QIcon(":/icons/app_icon.png"))
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 添加扫描状态标签
        self.scan_status_label = QLabel("")
        self.status_bar.addPermanentWidget(self.scan_status_label)
    
    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 扫描文件夹
        scan_action = QAction("扫描文件夹(&S)", self)
        scan_action.setShortcut("Ctrl+O")
        scan_action.triggered.connect(self.show_scan_dialog)
        file_menu.addAction(scan_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 刷新
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        
        # 系统统计
        stats_action = QAction("系统统计(&S)", self)
        stats_action.triggered.connect(self.show_system_stats)
        tools_menu.addAction(stats_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tool_bar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 扫描按钮
        scan_action = QAction("扫描", self)
        scan_action.triggered.connect(self.show_scan_dialog)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        # 刷新按钮
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
    
    def setup_connections(self):
        """设置信号连接"""
        # 搜索栏信号
        self.search_bar.search_requested.connect(self.handle_search)
        
        # 左侧面板信号
        self.left_panel.scan_requested.connect(self.handle_scan_request)
        
        # 中央面板信号
        self.center_panel.file_selected.connect(self.handle_file_selection)
        
        # API客户端信号
        self.api_client.request_started.connect(self.handle_request_started)
        self.api_client.request_finished.connect(self.handle_request_finished)
        self.api_client.error_occurred.connect(self.handle_error)
    
    def setup_timers(self):
        """设置定时器"""
        # 扫描状态更新定时器
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan_status)
        self.scan_timer.start(2000)  # 每2秒更新一次
    
    def handle_search(self, query: str, filters: dict):
        """处理搜索请求"""
        self.search_requested.emit(query, filters)
        self.center_panel.search_files(query, filters)
    
    def handle_scan_request(self, path: str):
        """处理扫描请求"""
        self.scan_requested.emit(path)
        self.start_scan(path)
    
    def handle_file_selection(self, file_info: dict):
        """处理文件选择"""
        self.file_selected.emit(file_info)
        self.right_panel.show_file_details(file_info)
    
    def handle_request_started(self, url: str):
        """处理请求开始"""
        self.status_label.setText("请求中...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
    
    def handle_request_finished(self, url: str, success: bool):
        """处理请求完成"""
        if success:
            self.status_label.setText("请求完成")
        else:
            self.status_label.setText("请求失败")
        
        self.progress_bar.setVisible(False)
    
    def handle_error(self, error_type: str, message: str):
        """处理错误"""
        self.status_label.setText(f"错误: {message}")
        self.progress_bar.setVisible(False)
        
        # 显示错误消息框
        QMessageBox.warning(self, "错误", f"{error_type}: {message}")
    
    def show_scan_dialog(self):
        """显示扫描对话框"""
        from PySide6.QtWidgets import QFileDialog
        
        path = QFileDialog.getExistingDirectory(
            self, 
            "选择要扫描的文件夹",
            ""
        )
        
        if path:
            self.start_scan(path)
    
    def start_scan(self, path: str):
        """开始扫描"""
        import asyncio
        
        async def scan():
            result = await self.api_client.start_scan(path)
            if "error" in result:
                QMessageBox.warning(self, "扫描失败", result["error"])
            else:
                self.status_label.setText(f"扫描任务已创建: {result.get('job_id', '')}")
        
        asyncio.create_task(scan())
    
    def update_scan_status(self):
        """更新扫描状态"""
        import asyncio
        
        async def update():
            status = await self.api_client.get_scan_status()
            if status:
                if status.get("scanning", False):
                    self.scan_status_label.setText("扫描中...")
                else:
                    total_files = status.get("total_files", 0)
                    available_files = status.get("available_files", 0)
                    self.scan_status_label.setText(f"文件: {available_files}/{total_files}")
        
        asyncio.create_task(update())
    
    def refresh_data(self):
        """刷新数据"""
        self.center_panel.refresh_files()
        self.left_panel.refresh_sources()
    
    def show_system_stats(self):
        """显示系统统计"""
        import asyncio
        
        async def get_stats():
            stats = await self.api_client.get_system_stats()
            if stats:
                QMessageBox.information(
                    self, 
                    "系统统计", 
                    f"总文件数: {stats.get('total_files', 0)}\n"
                    f"总大小: {stats.get('total_size', 0)} MB\n"
                    f"扫描状态: {'扫描中' if stats.get('scanning', False) else '空闲'}"
                )
        
        asyncio.create_task(get_stats())
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"{self.config.app_name}\n"
            f"版本: {self.config.app_version}\n"
            f"智能文件管理和总结系统"
        )
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止定时器
        if hasattr(self, 'scan_timer'):
            self.scan_timer.stop()
        
        # 关闭API客户端
        import asyncio
        asyncio.create_task(self.api_client.close())
        
        event.accept()
