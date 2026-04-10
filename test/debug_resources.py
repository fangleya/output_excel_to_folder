#!/usr/bin/env python3
"""
资源调试工具 - 用于测试打包后资源访问
"""
import sys
import os
from pathlib import Path


def debug_resource_access():
    """调试资源访问"""
    print("=" * 80)
    print("资源调试信息")
    print("=" * 80)

    # 1. 检查是否打包
    is_frozen = getattr(sys, "frozen", False)
    print(f"是否打包: {is_frozen}")

    # 2. 检查 _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        print(f"_MEIPASS: {sys._MEIPASS}")  # type: ignore
    else:
        print("_MEIPASS: 未设置")

    # 3. 程序运行路径
    print(f"sys.executable: {sys.executable}")
    print(f"os.getcwd(): {os.getcwd()}")

    # 4. 检查可能的资源路径
    resource_paths = []

    # 打包环境
    if hasattr(sys, "_MEIPASS"):
        resource_paths.append(os.path.join(sys._MEIPASS, "excel.ico"))  # type: ignore
        resource_paths.append(os.path.join(sys._MEIPASS, "resource", "excel.ico"))  # type: ignore
        resource_paths.append(os.path.join(sys._MEIPASS, "resource", "icons", "excel.ico"))  # type: ignore

    # 程序目录
    exe_dir = os.path.dirname(sys.executable) if is_frozen else os.getcwd()
    resource_paths.extend(
        [
            os.path.join(exe_dir, "excel.ico"),
            os.path.join(exe_dir, "resource", "excel.ico"),
            os.path.join(exe_dir, "..", "resource", "excel.ico"),
        ]
    )

    # 当前目录
    resource_paths.extend(
        [
            os.path.join(os.getcwd(), "excel.ico"),
            os.path.join(os.getcwd(), "resource", "excel.ico"),
        ]
    )

    # 5. 检查文件是否存在
    print("\n检查资源文件路径:")
    for path in resource_paths:
        normalized = os.path.normpath(path)
        exists = os.path.exists(normalized)
        status = "✓" if exists else "✗"
        print(f"  {status} {normalized}")

    print("=" * 80)

    # 6. 测试资源管理器
    try:
        from src.utils.resource_manager import get_icon, resource_exists

        print("\n测试资源管理器:")
        path = get_icon("excel.ico")
        print(f"  找到的路径: {path}")
        exists = resource_exists("excel.ico")
        print(f"  资源存在: {exists}")
    except ImportError as e:
        print(f"\n无法导入资源管理器: {e}")


if __name__ == "__main__":
    debug_resource_access()
