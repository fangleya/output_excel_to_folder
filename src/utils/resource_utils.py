# -*- coding: utf-8 -*-
"""
资源文件访问工具 - 支持开发环境和打包环境
"""
import os
import sys
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import QFile


class ResourceUtils:
    """资源工具类，支持多种资源访问方式"""

    # 单例模式
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """
        获取资源文件的绝对路径（支持打包和开发环境）

        规则：
        1. 打包环境：使用 sys._MEIPASS 作为基础路径
        2. 开发环境：使用项目根目录作为基础路径
        """
        try:
            # 场景1：PyInstaller 打包后
            if hasattr(sys, "_MEIPASS"):
                base_path = sys._MEIPASS  # type: ignore
                # 打包后资源通常在根目录
                resource_path = os.path.join(base_path, relative_path)
                if os.path.exists(resource_path):
                    return resource_path
        except AttributeError:
            pass

        # 场景2：开发环境
        # 尝试从项目根目录的resource文件夹查找
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        resource_path = os.path.join(base_path, "resource", relative_path)

        if os.path.exists(resource_path):
            return resource_path

        # 场景3：相对路径查找（兜底）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 尝试多种可能的相对路径
        possible_paths = [
            os.path.join(current_dir, "..", "..", "resource", relative_path),
            os.path.join(current_dir, "..", "..", "..", "resource", relative_path),
            os.path.join(os.getcwd(), "resource", relative_path),
        ]

        for path in possible_paths:
            normalized_path = os.path.normpath(path)
            if os.path.exists(normalized_path):
                return normalized_path

        # 如果都找不到，返回预期的路径
        return os.path.join(base_path, "resource", relative_path)

    @staticmethod
    def get_icon(icon_name: str) -> QIcon:
        """获取图标（支持多种方式）"""
        # 方法1：尝试使用Qt资源系统（如果使用了.qrc）
        qt_resource_path = f":/icons/{icon_name}" if not icon_name.startswith(":/") else icon_name
        icon = QIcon(qt_resource_path)

        if not icon.isNull():
            return icon

        # 方法2：尝试从文件系统获取
        file_path = ResourceUtils.get_resource_path(icon_name)
        if os.path.exists(file_path):
            icon = QIcon(file_path)
            if not icon.isNull():
                return icon

        # 方法3：使用系统主题图标（兜底）
        icon = QIcon.fromTheme("application-x-executable")
        return icon

    @staticmethod
    def get_pixmap(image_name: str, size=None) -> QPixmap:
        """获取像素图"""
        # 方法1：尝试使用Qt资源系统
        qt_resource_path = f":/images/{image_name}" if not image_name.startswith(":/") else image_name
        pixmap = QPixmap(qt_resource_path)

        if not pixmap.isNull():
            if size:
                pixmap = pixmap.scaled(size[0], size[1])
            return pixmap

        # 方法2：尝试从文件系统获取
        file_path = ResourceUtils.get_resource_path(image_name)
        if os.path.exists(file_path):
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                if size:
                    pixmap = pixmap.scaled(size[0], size[1])
                return pixmap

        # 方法3：创建默认像素图（兜底）
        pixmap = QPixmap(21, 21)
        pixmap.fill(QColor(200, 200, 200))
        return pixmap

    @staticmethod
    def file_exists(file_name: str) -> bool:
        """检查资源文件是否存在"""
        # 先检查Qt资源系统
        if QFile.exists(f":/{file_name}"):
            return True

        # 再检查文件系统
        file_path = ResourceUtils.get_resource_path(file_name)
        return os.path.exists(file_path)
