# test_resource.py
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.resource_manager import (
    get_resource_manager,
    get_icon,
    get_pixmap,
    get_resource_path,
    resource_exists,
    get_app_base_path,
)

# from src.utils.config_manager import (
#     load_config,
#     save_config,
#     get_config_value,
#     set_config_value,
#     get_config_file_path,
#     get_app_data_directory,
# )


# from src.utils.path_utils import (
#     # get_resource_path,
#     get_appdata_path,
#     get_config_path,
# )


def test_resource_files():
    """测试资源文件访问"""
    test_files = ["excel.ico", "icon.ico"]

    print("测试资源文件访问：")
    print("=" * 50)

    print(get_app_base_path())

    for file_name in test_files:
        path = get_resource_path(file_name)
        file_exists = resource_exists(file_name)

        status = "✅ 找到" if file_exists else "❌ 未找到"
        print(f"{status} {file_name}")
        if file_exists:
            print(f"   路径: {path}")
            print(f"   文件大小: {os.path.getsize(path) if os.path.exists(path) else 'N/A'} 字节")  # type: ignore
        print("-" * 30)

    print("\n调试信息：")
    print(f"当前目录: {os.getcwd()}")
    print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")

    # 检查是否有 _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        print(f"打包环境: 是")
        print(f"_MEIPASS: {sys._MEIPASS}")  # type: ignore
    else:
        print(f"打包环境: 否")


if __name__ == "__main__":
    test_resource_files()
