# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import QFileDialog, QWidget


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径
    开发环境：基于项目根目录
    打包环境：基于PyInstaller临时目录
    兼容开发环境/打包后环境的资源路径获取（解决 sys._MEIPASS 不存在报错）
    :param relative_path: 相对路径（如 "cfg/user_config.json"）
    :return: 绝对路径
    """
    try:
        # 场景1：PyInstaller 打包后（优先尝试）
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        # 场景2：开发环境（兜底逻辑）
        # 定位到 src 目录（path_utils.py 所在目录是 src/utils，向上退1级到 src）
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 拼接最终路径（兼容 Windows/macOS/Linux 路径分隔符）
    abs_path = os.path.join(base_path, relative_path)
    # 确保路径是规范化的（消除 ../ 等冗余）
    return os.path.normpath(abs_path)


def select_file_dialog(parent: QWidget, title: str = "选择文件", initial_dir: str = "") -> list:
    """打开文件选择对话框（支持多选Excel）"""
    # 初始目录优先级：传入的路径 > 当前工作目录
    directory = initial_dir if initial_dir and os.path.exists(initial_dir) else os.getcwd()

    file_paths, _ = QFileDialog.getOpenFileNames(
        parent, title, directory, "Excel文件 (*.xlsx *.xlsm *.xls);;所有文件 (*.*)"
    )
    return file_paths


def select_dir_dialog(parent: QWidget, title: str = "选择输出目录") -> str:
    """打开目录选择对话框"""
    dir_path = QFileDialog.getExistingDirectory(parent, title, "", QFileDialog.Option.ShowDirsOnly)
    return dir_path if dir_path else ""


def validate_rgb_color(color_str: str) -> list:
    """验证RGB颜色格式"""
    try:
        rgb = [int(x.strip()) for x in color_str.split(",")]
        if len(rgb) != 3:
            return [255, 0, 0]
        for val in rgb:
            if val < 0 or val > 255:
                return [255, 0, 0]
        return rgb
    except:
        return [255, 0, 0]


def parse_column_str(col_str: str) -> list:
    """解析列标题字符串（逗号分隔）"""
    return [x.strip() for x in col_str.split(",") if x.strip()]


def get_appdata_path() -> str:
    """
    获取应用程序数据目录（用于存储配置文件）
    Windows: %LOCALAPPDATA%/<app_name>
    macOS: ~/Library/Application Support/<app_name>
    Linux: ~/.config/<app_name>
    """
    import platform
    import sys

    app_name = "pyside6_excel_clean"
    system = platform.system()

    if system == "Windows":
        # Windows
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            return os.path.join(appdata, app_name)
        else:
            # 备用
            home = os.path.expanduser("~")
            return os.path.join(home, "AppData", "Local", app_name)

    elif system == "Darwin":  # macOS
        home = os.path.expanduser("~")
        return os.path.join(home, "Library", "Application Support", app_name)

    else:  # Linux 和其他
        home = os.path.expanduser("~")
        return os.path.join(home, ".config", app_name)


def get_config_path(config_file: str = "user_config.json") -> str:
    """
    获取配置文件路径
    开发环境：使用项目内的配置文件
    打包环境：使用用户数据目录
    """
    # 检查是否在打包环境中
    is_frozen = getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS")

    if is_frozen:
        # 打包环境：使用用户数据目录
        appdata_dir = get_appdata_path()
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, config_file)
    else:
        # 开发环境：使用项目目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(current_dir)  # 从utils退到src
        return os.path.join(src_dir, "cfg", config_file)
