# -*- coding: utf-8 -*-
"""
对话框管理器 - 统一管理各种对话框，支持跨平台和配置集成
功能：打开文件夹、文件选择、目录选择等
"""
import os
import sys
import platform
import subprocess
from typing import List, Tuple
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QWidget,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
)

# from PySide6.QtCore import Qt, QThread, Signal

# 导入配置管理器
# try:
#     from .config_manager import get_config, set_config, USER_CONFIG, add_recent_file
# except ImportError:
#     # 如果在不同目录结构下，尝试直接导入
#     try:
#         from config_manager import get_config, set_config, USER_CONFIG, add_recent_file
#     except ImportError:
#         print("警告: 无法导入 config_manager 模块")

#         # 定义模拟函数
#         def get_config(config_key, key=None, default=None):
#             return default

#         def set_config(config_key, key, value, auto_save=True):
#             return True

#         USER_CONFIG = "user_config"

#         def add_recent_file(file_path):
#             return True

from .config_manager import get_config, set_config, USER_CONFIG, add_recent_file


class DialogManager:
    """对话框管理器（单例模式）- 管理各种对话框操作"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._last_dirs = {}  # 缓存最后使用的目录
            self._init_last_dirs()

    def _init_last_dirs(self):
        """初始化最后使用的目录缓存"""
        # 从配置加载最近使用的目录
        recent_dirs = get_config(USER_CONFIG, "recent_dirs", {})
        if recent_dirs:
            self._last_dirs = recent_dirs

    def _get_default_dir(self, dir_type: str = "default") -> str:
        """
        获取默认目录（跨平台）
        :param dir_type: 目录类型，如 "home", "documents", "desktop", "downloads"
        :return: 默认目录路径
        """
        home = os.path.expanduser("~")
        system = platform.system()

        if dir_type == "home":
            return home

        elif dir_type == "documents":
            if system == "Windows":
                try:
                    # Windows: 使用系统API获取文档目录
                    import ctypes.wintypes

                    CSIDL_PERSONAL = 5  # My Documents
                    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf)
                    return buf.value
                except:
                    return os.path.join(home, "Documents")
            elif system == "Darwin":  # macOS
                return os.path.join(home, "Documents")
            else:  # Linux and others
                return os.path.join(home, "Documents")

        elif dir_type == "desktop":
            if system == "Windows":
                try:
                    # Windows: 使用系统API获取桌面目录
                    import ctypes.wintypes

                    CSIDL_DESKTOP = 0  # Desktop
                    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, 0, buf)
                    return buf.value
                except:
                    return os.path.join(home, "Desktop")
            elif system == "Darwin":  # macOS
                return os.path.join(home, "Desktop")
            else:  # Linux and others
                return os.path.join(home, "Desktop")

        elif dir_type == "downloads":
            if system == "Windows":
                try:
                    # Windows: 使用系统API获取下载目录
                    import ctypes.wintypes

                    CSIDL_PROFILE = 40  # User profile
                    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PROFILE, None, 0, buf)
                    downloads = os.path.join(buf.value, "Downloads")
                    if os.path.exists(downloads):
                        return downloads
                except:
                    pass
                return os.path.join(home, "Downloads")
            elif system == "Darwin":  # macOS
                return os.path.join(home, "Downloads")
            else:  # Linux and others
                return os.path.join(home, "Downloads")

        # 默认返回家目录
        return home

    def _get_exe_dir(self) -> str:
        """获取exe所在目录（打包环境）或项目根目录（开发环境）"""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        else:
            current_file = Path(__file__).resolve()
            return str(current_file.parent.parent.parent)  # 项目根目录

    def _save_last_dir(self, dir_type: str, directory: str):
        """保存最后使用的目录到配置"""
        if directory and os.path.isdir(directory):
            self._last_dirs[dir_type] = directory

            # 保存到配置文件
            set_config(USER_CONFIG, "recent_dirs", self._last_dirs, auto_save=True)

    def _get_last_dir(self, dir_type: str = "default") -> str:
        """获取最后使用的目录"""
        # 从缓存中获取
        if dir_type in self._last_dirs:
            last_dir = self._last_dirs[dir_type]
            if os.path.isdir(last_dir):
                return last_dir

        # 如果不存在或无效，返回默认目录
        return self._get_default_dir("home")

    def _validate_and_get_dir(self, input_path: str = "", dir_type: str = "default") -> str:
        """
        验证并获取有效的目录路径
        :param input_path: 输入的路径
        :param dir_type: 目录类型
        :return: 有效的目录路径
        """
        # 如果输入路径存在且是目录，直接使用
        if input_path and os.path.isdir(input_path):
            return os.path.normpath(input_path)

        # 如果输入路径存在但是文件，使用其父目录
        if input_path and os.path.isfile(input_path):
            return os.path.dirname(os.path.normpath(input_path))

        # 否则使用最后使用的目录或默认目录
        return self._get_last_dir(dir_type)

    def open_local_folder(self, path: str = "") -> bool:
        """
        1. 打开本地文件夹（在系统文件管理器中打开）
        :param path: 要打开的路径，为空时打开程序所在目录
        :return: 是否成功打开
        """
        try:
            # 验证并获取有效的目录路径
            if not path:
                # 如果未指定路径，打开程序所在目录
                folder_path = self._get_exe_dir()
            else:
                folder_path = self._validate_and_get_dir(path, "open_folder")

            # 检查目录是否存在
            if not os.path.isdir(folder_path):
                print(f"目录不存在: {folder_path}")
                return False

            # 根据系统使用不同的命令打开文件夹
            system = platform.system()

            if system == "Windows":
                # Windows: 使用 explorer 命令
                os.startfile(folder_path)
            elif system == "Darwin":  # macOS
                # macOS: 使用 open 命令
                subprocess.run(["open", folder_path], check=True)
            else:  # Linux and others
                # Linux: 使用 xdg-open 或文件管理器
                try:
                    subprocess.run(["xdg-open", folder_path], check=True)
                except:
                    # 尝试使用常见的文件管理器
                    file_managers = ["nautilus", "dolphin", "thunar", "pcmanfm", "nemo"]
                    for fm in file_managers:
                        try:
                            subprocess.run([fm, folder_path], check=True)
                            break
                        except:
                            continue

            print(f"已打开文件夹: {folder_path}")
            return True

        except Exception as e:
            print(f"打开文件夹失败: {e}")
            return False

    def select_files_dialog(
        self,
        parent: QWidget,
        title: str = "选择文件",
        initial_dir: str = "",
        file_filter: str = "所有文件 (*.*)",
        multi_select: bool = True,
        dir_type: str = "select_files",
    ) -> List[str]:
        """
        2. 打开文件选择对话框（支持单选和多选）
        :param parent: 父窗口
        :param title: 对话框标题
        :param initial_dir: 初始目录
        :param file_filter: 文件过滤器
        :param multi_select: 是否允许多选
        :param dir_type: 目录类型，用于保存最后使用的目录
        :return: 选择的文件路径列表
        """
        try:
            # 验证并获取有效的初始目录
            directory = self._validate_and_get_dir(initial_dir, dir_type)

            # 根据是否多选使用不同的方法
            if multi_select:
                # 多选模式
                file_paths, _ = QFileDialog.getOpenFileNames(parent, title, directory, file_filter)
            else:
                # 单选模式
                file_path, _ = QFileDialog.getOpenFileName(parent, title, directory, file_filter)
                file_paths = [file_path] if file_path else []

            # 如果选择了文件，保存目录并添加到最近文件
            if file_paths:
                # 保存最后使用的目录（使用第一个文件的目录）
                first_file_dir = os.path.dirname(file_paths[0])
                self._save_last_dir(dir_type, first_file_dir)

                # 将文件添加到最近文件列表
                for file_path in file_paths:
                    add_recent_file(file_path)

            return file_paths

        except Exception as e:
            print(f"文件选择对话框失败: {e}")
            return []

    def select_dir_dialog(
        self, parent: QWidget, title: str = "选择目录", initial_dir: str = "", dir_type: str = "select_dir"
    ) -> str:
        """
        3. 打开目录选择对话框（用于选择目录）
        :param parent: 父窗口
        :param title: 对话框标题
        :param initial_dir: 初始目录
        :param dir_type: 目录类型，用于保存最后使用的目录
        :return: 选择的目录路径
        """
        try:
            # 验证并获取有效的初始目录
            directory = self._validate_and_get_dir(initial_dir, dir_type)

            # 打开目录选择对话框
            dir_path = QFileDialog.getExistingDirectory(parent, title, directory, QFileDialog.Option.ShowDirsOnly)

            # 如果选择了目录，保存最后使用的目录
            if dir_path:
                self._save_last_dir(dir_type, dir_path)

            return dir_path if dir_path else ""

        except Exception as e:
            print(f"目录选择对话框失败: {e}")
            return ""

    def select_save_file_dialog(
        self,
        parent: QWidget,
        title: str = "保存文件",
        initial_dir: str = "",
        default_filename: str = "",
        file_filter: str = "所有文件 (*.*)",
        dir_type: str = "save_file",
    ) -> str:
        """
        打开保存文件对话框
        :param parent: 父窗口
        :param title: 对话框标题
        :param initial_dir: 初始目录
        :param default_filename: 默认文件名
        :param file_filter: 文件过滤器
        :param dir_type: 目录类型
        :return: 保存的文件路径
        """
        try:
            # 验证并获取有效的初始目录
            directory = self._validate_and_get_dir(initial_dir, dir_type)

            # 如果有默认文件名，构建完整路径
            if default_filename:
                initial_path = os.path.join(directory, default_filename)
            else:
                initial_path = directory

            # 打开保存文件对话框
            file_path, _ = QFileDialog.getSaveFileName(parent, title, initial_path, file_filter)

            # 如果选择了保存路径，保存目录
            if file_path:
                save_dir = os.path.dirname(file_path)
                self._save_last_dir(dir_type, save_dir)

            return file_path if file_path else ""

        except Exception as e:
            print(f"保存文件对话框失败: {e}")
            return ""

    def create_custom_file_dialog(
        self,
        parent: QWidget,
        title: str = "选择文件",
        initial_dir: str = "",
        file_filter: str = "所有文件 (*.*)",
        multi_select: bool = True,
    ) -> Tuple[List[str], str, bool]:
        """
        创建自定义文件选择对话框（带更多选项）
        :return: (文件列表, 选择的目录, 是否记住选择)
        """
        try:
            # 验证并获取有效的初始目录
            directory = self._validate_and_get_dir(initial_dir, "custom_dialog")

            # 创建自定义对话框
            dialog = QDialog(parent)
            dialog.setWindowTitle(title)
            dialog.setMinimumWidth(500)

            layout = QVBoxLayout(dialog)

            # 路径显示
            path_layout = QHBoxLayout()
            path_label = QLabel("路径:")
            path_edit = QLineEdit(directory)
            path_browse_btn = QPushButton("浏览...")

            path_layout.addWidget(path_label)
            path_layout.addWidget(path_edit)
            path_layout.addWidget(path_browse_btn)
            layout.addLayout(path_layout)

            # 选项
            remember_checkbox = QCheckBox("记住此目录")
            remember_checkbox.setChecked(True)
            layout.addWidget(remember_checkbox)

            # 按钮区域
            button_layout = QHBoxLayout()
            ok_btn = QPushButton("确定")
            cancel_btn = QPushButton("取消")

            button_layout.addStretch()
            button_layout.addWidget(ok_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)

            # 连接信号
            selected_files = []
            selected_dir = directory

            def browse_folder():
                nonlocal selected_dir
                dir_path = self.select_dir_dialog(dialog, "选择目录", path_edit.text())
                if dir_path:
                    path_edit.setText(dir_path)
                    selected_dir = dir_path

            def accept_dialog():
                nonlocal selected_files, selected_dir
                selected_dir = path_edit.text()

                # 验证目录
                if not os.path.isdir(selected_dir):
                    QMessageBox.warning(dialog, "警告", "目录不存在！")
                    return

                # 根据是否多选打开文件选择
                if multi_select:
                    files = QFileDialog.getOpenFileNames(dialog, "选择文件", selected_dir, file_filter)[0]
                else:
                    file_path = QFileDialog.getOpenFileName(dialog, "选择文件", selected_dir, file_filter)[0]
                    files = [file_path] if file_path else []

                if files:
                    selected_files = files

                    # 如果勾选了记住，保存目录
                    if remember_checkbox.isChecked():
                        self._save_last_dir("custom_dialog", selected_dir)

                    dialog.accept()

            path_browse_btn.clicked.connect(browse_folder)
            ok_btn.clicked.connect(accept_dialog)
            cancel_btn.clicked.connect(dialog.reject)

            # 显示对话框
            if dialog.exec() == QDialog.accepted:
                return selected_files, selected_dir, remember_checkbox.isChecked()
            else:
                return [], "", False

        except Exception as e:
            print(f"自定义文件对话框失败: {e}")
            return [], "", False

    def get_predefined_filters(self) -> dict:
        """获取预定义的文件过滤器"""
        return {
            "excel": "Excel文件 (*.xlsx *.xlsm *.xls *.xlsb);;所有文件 (*.*)",
            "images": "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;所有文件 (*.*)",
            "text": "文本文件 (*.txt *.csv *.log *.ini *.json *.xml);;所有文件 (*.*)",
            "pdf": "PDF文件 (*.pdf);;所有文件 (*.*)",
            "all": "所有文件 (*.*)",
            "python": "Python文件 (*.py *.pyw);;所有文件 (*.*)",
        }

    def open_file_explorer_to_file(self, file_path: str) -> bool:
        """
        在文件管理器中打开并选中文件
        :param file_path: 文件路径
        :return: 是否成功
        """
        try:
            if not os.path.exists(file_path):
                return False

            system = platform.system()
            file_path = os.path.normpath(file_path)

            if system == "Windows":
                # Windows: 使用 explorer 的 /select 参数
                subprocess.run(["explorer", "/select,", file_path], check=True)
            elif system == "Darwin":  # macOS
                # macOS: 使用 open 的 -R 参数
                subprocess.run(["open", "-R", file_path], check=True)
            else:  # Linux and others
                # Linux: 尝试使用文件管理器打开父目录
                parent_dir = os.path.dirname(file_path)
                self.open_local_folder(parent_dir)

            return True

        except Exception as e:
            print(f"打开文件所在位置失败: {e}")
            return False


# 全局单例实例
_dialog_manager_instance = None


def get_dialog_manager() -> DialogManager:
    """获取对话框管理器单例"""
    global _dialog_manager_instance
    if _dialog_manager_instance is None:
        _dialog_manager_instance = DialogManager()
    return _dialog_manager_instance


# 便捷函数
def open_local_folder(path: str = "") -> bool:
    """打开本地文件夹"""
    return get_dialog_manager().open_local_folder(path)


def select_files_dialog(
    parent: QWidget,
    title: str = "选择文件",
    initial_dir: str = "",
    file_filter: str = "所有文件 (*.*)",
    multi_select: bool = True,
    dir_type: str = "select_files",
) -> List[str]:
    """打开文件选择对话框"""
    return get_dialog_manager().select_files_dialog(parent, title, initial_dir, file_filter, multi_select, dir_type)


def select_dir_dialog(
    parent: QWidget, title: str = "选择目录", initial_dir: str = "", dir_type: str = "select_dir"
) -> str:
    """打开目录选择对话框"""
    return get_dialog_manager().select_dir_dialog(parent, title, initial_dir, dir_type)


def select_save_file_dialog(
    parent: QWidget,
    title: str = "保存文件",
    initial_dir: str = "",
    default_filename: str = "",
    file_filter: str = "所有文件 (*.*)",
    dir_type: str = "save_file",
) -> str:
    """打开保存文件对话框"""
    return get_dialog_manager().select_save_file_dialog(
        parent, title, initial_dir, default_filename, file_filter, dir_type
    )


def get_predefined_filters() -> dict:
    """获取预定义的文件过滤器"""
    return get_dialog_manager().get_predefined_filters()


def open_file_explorer_to_file(file_path: str) -> bool:
    """在文件管理器中打开并选中文件"""
    return get_dialog_manager().open_file_explorer_to_file(file_path)


# 兼容性函数（保持与旧代码兼容）
def select_file_dialog(
    parent: QWidget,
    title: str = "选择文件",
    initial_dir: str = "",
    file_filter: str = "Excel文件 (*.xlsx *.xlsm *.xls);;所有文件 (*.*)",
) -> List[str]:
    """兼容旧版本的文件选择对话框（多选）"""
    return select_files_dialog(parent, title, initial_dir, file_filter, True)


def select_single_file_dialog(
    parent: QWidget,
    title: str = "选择文件",
    initial_dir: str = "",
    file_filter: str = "Excel文件 (*.xlsx *.xlsm *.xls);;所有文件 (*.*)",
) -> str:
    """单选文件对话框"""
    files = select_files_dialog(parent, title, initial_dir, file_filter, False, "select_single_file")
    return files[0] if files else ""
