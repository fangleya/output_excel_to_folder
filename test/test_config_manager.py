from src.utils.config_manager import *

# 获取配置管理器
config_manager = get_config_manager()

# 获取所有支持的配置类型
config_list = get_config_list()
print(f"支持的配置: {config_list}")  # ['user_config', 'app_config', ...]

# 获取用户配置
user_config = get_config(USER_CONFIG)
output_path = get_config(USER_CONFIG, "output_path", "~/Desktop")

# 获取应用配置
language = get_config(APP_CONFIG, "language", "zh_CN")

# 设置配置
set_config(USER_CONFIG, "last_add_file_path", "/path/to/file.xlsx")
set_config(THEME_CONFIG, "dark_mode", True, auto_save=True)

# 保存配置
save_config(USER_CONFIG)

# 获取配置路径
config_path = get_config_path(USER_CONFIG)
print(f"配置文件路径: {config_path}")

# 获取应用名称
app_name = get_app_name()
print(f"应用名称: {app_name}")

# 获取应用数据目录
app_data_dir = get_app_data_dir()
print(f"应用数据目录: {app_data_dir}")

# 添加最近文件
add_recent_file("/path/to/recent/file.xlsx")
