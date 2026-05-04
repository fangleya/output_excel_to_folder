import sys
import os
from PySide6.QtWidgets import QApplication


# -------------------------- 打包专属路径兼容 --------------------------
def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = get_base_path()

# 把src目录加入Python路径，解决子包导入报错
sys.path.insert(0, BASE_PATH)

# 2. 强制设置PySide6 Qt插件路径，彻底解决打包后窗口不显示/插件缺失
QT_PLUGIN_PATH = os.path.join(BASE_PATH, "PySide6", "plugins")
if os.path.exists(QT_PLUGIN_PATH):
    os.environ["QT_PLUGIN_PATH"] = QT_PLUGIN_PATH
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(QT_PLUGIN_PATH, "platforms")

# 3. 把程序目录加入系统PATH，解决DLL加载失败
os.environ["PATH"] = BASE_PATH + os.pathsep + os.environ.get("PATH", "")

# -------------------------- 以下是import代码 --------------------------

# 导入UI窗口（无循环！）
from src.app.app_view import MainWindow


# -------------------------- main启动函数 --------------------------
def main():
    app = QApplication(sys.argv)
    # 设置图标（可选）
    try:
        from src.utils.resource_manager import get_icon

        app_icon = get_icon("icon_app.ico")
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
    except (ImportError, Exception):
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


# -------------------------- 程序入口 --------------------------
if __name__ == "__main__":
    main()
