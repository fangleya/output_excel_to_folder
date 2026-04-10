import sys
import os
from PySide6.QtWidgets import QApplication


# -------------------------- 打包专属路径兼容 --------------------------
def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = get_base_path()
sys.path.insert(0, BASE_PATH)

QT_PLUGIN_PATH = os.path.join(BASE_PATH, "PySide6", "plugins")
if os.path.exists(QT_PLUGIN_PATH):
    os.environ["QT_PLUGIN_PATH"] = QT_PLUGIN_PATH
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(QT_PLUGIN_PATH, "platforms")

os.environ["PATH"] = BASE_PATH + os.pathsep + os.environ.get("PATH", "")

# 导入UI窗口（无循环！）
from app.app_view import MainWindow


# -------------------------- main启动函数 --------------------------
def main():
    app = QApplication(sys.argv)
    # 设置图标（可选）
    try:
        from utils.resource_manager import get_icon

        app_icon = get_icon("my_app.ico")
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
