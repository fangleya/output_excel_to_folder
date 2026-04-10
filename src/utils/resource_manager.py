# -*- coding: utf-8 -*-
"""
资源管理器 - 统一管理资源访问，支持开发环境和打包环境
功能：获取icon、获取图片资源、获取文件路径、判断文件是否存在等
"""
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List

from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import QFile, QIODevice


class ResourceManager:
    """资源管理器（单例模式）- 统一处理资源访问"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._resource_cache = {}
            self._icon_cache = {}
            self._pixmap_cache = {}
            self._base_paths = self._get_all_base_paths()

    def _get_all_base_paths(self) -> List[str]:
        """获取所有可能的基础路径（开发环境和打包环境）"""
        paths = []

        # 1. PyInstaller 打包临时目录（最高优先级）
        if hasattr(sys, "_MEIPASS"):
            paths.append(sys._MEIPASS)  # type: ignore

        # 2. 可执行文件目录（打包环境）
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
            paths.append(exe_dir)
            # 打包后资源可能在 exe 同级的 resource 目录
            paths.append(os.path.join(exe_dir, "resource"))

        # 3. 项目根目录（开发环境）
        current_file = Path(__file__).resolve()
        # 根据文件位置向上找到项目根目录
        project_root = current_file.parent.parent
        paths.append(str(project_root))

        # 4. 当前工作目录
        paths.append(os.getcwd())

        # 5. 可能的资源目录
        possible_dirs = ["resource", "resources", "assets", "icons", "images"]
        for base in paths.copy():
            for sub_dir in possible_dirs:
                possible_path = os.path.join(base, sub_dir)
                if os.path.exists(possible_path):
                    paths.append(possible_path)

        # 去重并返回
        return list(dict.fromkeys(paths))

    def find_resource(self, relative_path: str) -> Optional[str]:
        """
        查找资源文件的真实路径
        :param relative_path: 资源相对路径，如 'icons/app.png'
        :return: 绝对路径或Qt资源路径，找不到返回None
        """
        # 1. 检查缓存
        if relative_path in self._resource_cache:
            cached = self._resource_cache[relative_path]
            if cached is None or os.path.exists(cached) or QFile.exists(cached):
                return cached

        # 2. 检查Qt资源系统（格式 :/path/to/resource）
        qt_resource_path = f":/{relative_path}"
        if QFile.exists(qt_resource_path):
            self._resource_cache[relative_path] = qt_resource_path
            return qt_resource_path

        # 3. 检查相对Qt资源路径
        if not relative_path.startswith(":/"):
            qt_paths = [
                f":/icons/{relative_path}",
                f":/images/{relative_path}",
                f":/resource/{relative_path}",
                f":/{relative_path}",
            ]
            for qt_path in qt_paths:
                if QFile.exists(qt_path):
                    self._resource_cache[relative_path] = qt_path
                    return qt_path

        # 4. 在文件系统中查找
        # 首先尝试直接路径
        if os.path.isabs(relative_path) and os.path.exists(relative_path):
            abs_path = os.path.normpath(relative_path)
            self._resource_cache[relative_path] = abs_path
            return abs_path

        # 5. 尝试所有基础路径
        search_paths = []

        # 直接拼接
        for base_path in self._base_paths:
            search_paths.append(os.path.join(base_path, relative_path))

        # 尝试 common 子目录
        common_dirs = ["", "resource", "resources", "assets", "icons", "images"]
        for base_path in self._base_paths:
            for sub_dir in common_dirs:
                if sub_dir:
                    search_paths.append(os.path.join(base_path, sub_dir, relative_path))
                else:
                    search_paths.append(os.path.join(base_path, relative_path))

        # 检查所有可能路径
        for path in search_paths:
            normalized = os.path.normpath(path)
            if os.path.exists(normalized):
                self._resource_cache[relative_path] = normalized
                return normalized

        # 6. 尝试父目录查找（针对开发环境）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_levels = ["..", "../..", "../../.."]
        for level in parent_levels:
            test_path = os.path.join(current_dir, level, "resource", relative_path)
            normalized = os.path.normpath(test_path)
            if os.path.exists(normalized):
                self._resource_cache[relative_path] = normalized
                return normalized

        # 7. 未找到，缓存None并输出调试信息
        print(f"⚠️ 资源未找到: {relative_path}")
        print(f"   搜索路径: {self._base_paths[:3]}...")  # 只显示前3个
        self._resource_cache[relative_path] = None
        return None

    def get_icon(self, icon_name: str, default_on_fail: bool = True) -> QIcon:
        """
        获取图标
        :param icon_name: 图标文件名或路径
        :param default_on_fail: 找不到时是否返回默认图标
        :return: QIcon对象
        """
        cache_key = f"icon:{icon_name}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # 查找资源
        icon_path = self.find_resource(icon_name)

        if icon_path:
            if icon_path.startswith(":/"):
                # Qt资源路径
                icon = QIcon(icon_path)
            else:
                # 文件系统路径
                icon = QIcon(icon_path)
        elif default_on_fail:
            # 使用系统主题图标
            icon = QIcon.fromTheme("application-x-executable")
            if icon.isNull():
                # 创建默认灰色图标
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(180, 180, 180))
                icon = QIcon(pixmap)
        else:
            icon = QIcon()

        self._icon_cache[cache_key] = icon
        return icon

    def get_pixmap(
        self, image_name: str, size: Optional[Tuple[int, int]] = None, default_on_fail: bool = True
    ) -> QPixmap:
        """
        获取像素图
        :param image_name: 图片文件名或路径
        :param size: 可选尺寸 (width, height)
        :param default_on_fail: 找不到时是否返回默认图片
        :return: QPixmap对象
        """
        size_key = f"{size[0]}x{size[1]}" if size else "original"
        cache_key = f"pixmap:{image_name}:{size_key}"

        if cache_key in self._pixmap_cache:
            return self._pixmap_cache[cache_key]

        # 查找资源
        image_path = self.find_resource(image_name)

        if image_path:
            if image_path.startswith(":/"):
                pixmap = QPixmap(image_path)
            else:
                pixmap = QPixmap(image_path)
        elif default_on_fail:
            # 创建默认灰色图片
            width, height = size if size else (64, 64)
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(200, 200, 200))
        else:
            pixmap = QPixmap()

        # 调整尺寸
        if not pixmap.isNull() and size:
            pixmap = pixmap.scaled(size[0], size[1])

        self._pixmap_cache[cache_key] = pixmap
        return pixmap

    def get_file_path(self, relative_path: str) -> Optional[str]:
        """获取文件路径（不加载，仅返回路径）"""
        return self.find_resource(relative_path)

    def file_exists(self, relative_path: str) -> bool:
        """检查资源文件是否存在"""
        path = self.find_resource(relative_path)
        if path is None:
            return False
        if path.startswith(":/"):
            return QFile.exists(path)
        return os.path.exists(path)

    def get_base_path(self) -> str:
        """获取当前运行环境的基础路径"""
        # 优先使用打包环境路径
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS  # type: ignore

        # 2. 可执行文件目录（打包环境）
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)

        # 3. 项目根目录（开发环境）
        current_file = Path(__file__).resolve()
        return str(current_file.parent.parent)


# 全局单例实例
_resource_manager_instance = None


def get_resource_manager() -> ResourceManager:
    """获取资源管理器单例"""
    global _resource_manager_instance
    if _resource_manager_instance is None:
        _resource_manager_instance = ResourceManager()
    return _resource_manager_instance


# 便捷函数
def get_icon(icon_name: str, default_on_fail: bool = True) -> QIcon:
    return get_resource_manager().get_icon(icon_name, default_on_fail)


def get_pixmap(image_name: str, size: Optional[Tuple[int, int]] = None, default_on_fail: bool = True) -> QPixmap:
    return get_resource_manager().get_pixmap(image_name, size, default_on_fail)


def get_resource_path(relative_path: str) -> Optional[str]:
    return get_resource_manager().get_file_path(relative_path)


def resource_exists(relative_path: str) -> bool:
    return get_resource_manager().file_exists(relative_path)


def get_app_base_path() -> str:
    return get_resource_manager().get_base_path()
