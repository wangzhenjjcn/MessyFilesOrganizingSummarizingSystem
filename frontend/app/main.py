"""
文件整理和总结系统 - 主应用入口
"""
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from app.ui.main_window import MainWindow
from app.services.api_client import APIClient
from app.config import Config

class FileOrganizerApp:
    """文件整理和总结系统主应用"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("文件整理和总结系统")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("FileOrganizer")
        
        # 设置应用图标
        self.app.setWindowIcon(QIcon(":/icons/app_icon.png"))
        
        # 初始化配置
        self.config = Config()
        
        # 初始化API客户端
        self.api_client = APIClient(self.config.api_base_url)
        
        # 创建主窗口
        self.main_window = MainWindow(self.api_client, self.config)
        
        # 设置应用样式
        self.setup_style()
        
        # 连接信号
        self.setup_connections()
    
    def setup_style(self):
        """设置应用样式"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QSplitter {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        
        QTreeView, QListView, QTableView {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            selection-background-color: #e3f2fd;
        }
        
        QHeaderView::section {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            padding: 4px;
            font-weight: bold;
        }
        
        QPushButton {
            background-color: #2196f3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1976d2;
        }
        
        QPushButton:pressed {
            background-color: #0d47a1;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        
        QLineEdit {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: #ffffff;
        }
        
        QLineEdit:focus {
            border-color: #2196f3;
        }
        
        QStatusBar {
            background-color: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }
        
        QProgressBar {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #4caf50;
            border-radius: 3px;
        }
        """
        
        self.app.setStyleSheet(style)
    
    def setup_connections(self):
        """设置信号连接"""
        # 应用退出时清理资源
        self.app.aboutToQuit.connect(self.cleanup)
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'api_client'):
            self.api_client.close()
    
    def run(self):
        """运行应用"""
        try:
            # 显示主窗口
            self.main_window.show()
            
            # 启动应用
            return self.app.exec()
            
        except Exception as e:
            QMessageBox.critical(
                None,
                "应用启动失败",
                f"应用启动时发生错误：\n{str(e)}"
            )
            return 1

def main():
    """主函数"""
    try:
        app = FileOrganizerApp()
        return app.run()
    except Exception as e:
        print(f"应用启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
