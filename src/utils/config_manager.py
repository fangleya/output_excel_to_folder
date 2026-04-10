# -*- coding: utf-8 -*-
"""
配置管理器 - 统一管理配置文件，支持开发环境和打包环境
支持：exe同目录配置文件、自动生成默认配置、热更新配置
"""
import json
import os
import sys
import platform
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""

    def __init__(self, config_manager, config_key: str):
        self.config_manager = config_manager
        self.config_key = config_key
        self.last_hash = None

    def on_modified(self, event):
        """文件修改时触发"""
        if not event.is_directory and event.src_path == self.config_manager.get_config_path(self.config_key):
            print(f"检测到配置文件变更: {event.src_path}")
            # 延迟一点时间再重新加载，确保文件写入完成
            threading.Timer(0.5, self._reload_config).start()

    def _reload_config(self):
        """重新加载配置"""
        try:
            # 检查文件哈希是否真的变化
            config_path = self.config_manager.get_config_path(self.config_key)
            if not config_path:
                return

            current_hash = self._get_file_hash(config_path)
            if current_hash != self.last_hash:
                self.last_hash = current_hash
                self.config_manager._load_single_config(self.config_key, force=True)
                print(f"配置文件已重新加载: {self.config_key}")
        except Exception as e:
            print(f"重新加载配置失败: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """获取文件哈希值"""
        if not os.path.exists(file_path):
            return ""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""


class ConfigManager:
    """配置管理器（单例模式）- 支持热更新和多环境"""

    # 支持的配置文件列表
    CONFIG_FILES = {
        "user_config": "user_config.json",  # 用户配置
        "app_config": "app_config.json",  # 应用配置
        "system_config": "system_config.json",  # 系统配置
        "theme_config": "theme_config.json",  # 主题配置
        "window_config": "window_config.json",  # 窗口配置
    }

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._app_name = self._get_app_name()
            self._configs = {}  # 存储所有配置数据
            self._config_paths = {}  # 存储所有配置路径
            self._file_observers = {}  # 文件观察器
            self._config_change_callbacks = {}  # 配置变更回调函数
            self._watch_enabled = True  # 是否启用文件监控

            # 初始化所有配置文件的默认配置
            self._default_configs = self._get_all_default_configs()

            # 获取所有配置文件的路径
            self._init_config_paths()

            # 确保所有配置目录存在
            self._ensure_all_config_directories()

            # 加载所有配置
            self._load_all_configs()

            # 启动配置监控
            self._start_all_config_watchers()

    def _get_app_name(self) -> str:
        """获取应用名称（从项目路径自动获取）"""
        # 尝试从环境变量获取
        env_app_name = os.getenv("APP_NAME")
        if env_app_name:
            return env_app_name

        # 尝试从打包环境获取
        if getattr(sys, "frozen", False):
            # 打包环境：从可执行文件名获取
            exe_path = sys.executable
            exe_name = os.path.basename(exe_path)
            return os.path.splitext(exe_name)[0]

        # 开发环境：从项目根目录名获取
        try:
            # 获取项目根目录（src的父目录）
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            return project_root.name
        except:
            # 如果无法获取，使用默认值
            return "pyside6_base_client"

    def _get_all_default_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有配置文件的默认配置"""
        return {
            "user_config": {
                "app_name": self._app_name,
                "version": "1.0.0",
                "output_path": self._get_default_output_path(),
                "last_add_file_path": "",
                "recent_files": [],
                "max_recent_files": 10,
                "auto_save_interval": 30,  # 自动保存间隔（秒）
                "config_version": "1.0",
            },
            "app_config": {
                "version": "1.0.0",
                "language": "zh_CN",
                "check_updates": True,
                "auto_save": True,
                "save_interval": 300,
                "backup_count": 5,
                "config_version": "1.0",
            },
            "system_config": {
                "max_threads": 4,
                "temp_dir": self._get_temp_dir(),
                "log_level": "INFO",
                "log_retention_days": 7,
                "cache_size": 100,
                "config_version": "1.0",
            },
            "theme_config": {
                "theme": "default",
                "font_family": "Microsoft YaHei",
                "font_size": 10,
                "ui_scale": 1.0,
                "dark_mode": False,
                "config_version": "1.0",
            },
            "window_config": {
                "window_geometry": None,
                "window_state": None,
                "splitter_sizes": [200, 600],
                "column_widths": {},
                "last_window_size": [800, 600],
                "config_version": "1.0",
            },
        }

    def _get_default_output_path(self) -> str:
        """获取默认输出路径（跨平台）"""
        home = os.path.expanduser("~")
        system = platform.system()

        if system == "Windows":
            # Windows: 使用文档目录或桌面
            try:
                # 尝试获取文档目录
                import ctypes.wintypes

                CSIDL_PERSONAL = 5  # My Documents
                buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf)
                return buf.value
            except:
                return os.path.join(home, "Desktop")
        elif system == "Darwin":  # macOS
            return os.path.join(home, "Desktop")
        else:  # Linux and others
            documents = os.path.join(home, "Documents")
            if os.path.exists(documents):
                return documents
            return os.path.join(home, "Desktop")

    def _get_temp_dir(self) -> str:
        """获取临时目录（跨平台）"""
        system = platform.system()

        if system == "Windows":
            temp = os.getenv("TEMP") or os.getenv("TMP")
            if temp:
                return temp
            return "C:\\Windows\\Temp"
        elif system == "Darwin":  # macOS
            return "/tmp"
        else:  # Linux and others
            return "/tmp"

    def _get_config_file_path(self, config_key: str) -> str:
        """
        获取配置文件路径（跨环境）
        规则：
        1. Windows打包环境：exe同目录下的config文件夹
        2. 其他打包环境：用户数据目录
        3. 开发环境：项目目录下的config文件夹
        """
        config_file = self.CONFIG_FILES.get(config_key, f"{config_key}.json")
        system = platform.system()

        # 检查是否在打包环境中
        is_frozen = getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS")

        if is_frozen:
            # 打包环境
            if system == "Windows":
                # Windows打包环境：exe同目录下的config文件夹
                exe_dir = os.path.dirname(sys.executable)
                config_dir = os.path.join(exe_dir, "config")
            else:
                # 非Windows打包环境：使用用户数据目录
                home = os.path.expanduser("~")
                if system == "Darwin":  # macOS
                    config_dir = os.path.join(home, "Library", "Application Support", self._app_name, "config")
                else:  # Linux and others
                    config_dir = os.path.join(home, ".config", self._app_name, "config")
        else:
            # 开发环境：使用项目目录的config文件夹
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            config_dir = os.path.join(project_root, "config")

        return os.path.join(config_dir, config_file)

    def _init_config_paths(self):
        """初始化所有配置文件的路径"""
        for config_key in self.CONFIG_FILES.keys():
            self._config_paths[config_key] = self._get_config_file_path(config_key)

    def _ensure_all_config_directories(self) -> None:
        """确保所有配置目录存在，不存在则创建"""
        for config_key, config_path in self._config_paths.items():
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                try:
                    os.makedirs(config_dir, exist_ok=True)
                    print(f"创建配置目录: {config_dir}")
                except Exception as e:
                    print(f"创建配置目录失败({config_key}): {e}")

    def _load_all_configs(self):
        """加载所有配置文件"""
        for config_key in self.CONFIG_FILES.keys():
            self._load_single_config(config_key)

    def _load_single_config(self, config_key: str, force: bool = False) -> Dict[str, Any]:
        """加载单个配置文件"""
        if config_key in self._configs and not force:
            return self._configs[config_key].copy()

        config_path = self._config_paths.get(config_key)
        if not config_path:
            return {}

        default_config = self._default_configs.get(config_key, {})

        # 检查配置文件是否存在
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)

                # 合并默认配置和加载的配置（加载的配置优先）
                merged_config = default_config.copy()
                for key, value in loaded_config.items():
                    merged_config[key] = value

                self._configs[config_key] = merged_config
                print(f"配置已加载({config_key}): {config_path}")

                # 触发配置变更回调
                self._trigger_config_change_callbacks(config_key)

            except Exception as e:
                print(f"加载配置失败({config_key}): {e}")
                # 加载失败时使用默认配置
                self._configs[config_key] = default_config.copy()
                # 尝试保存默认配置
                self._save_single_config(config_key)
        else:
            # 配置文件不存在，使用默认配置
            print(f"配置文件不存在，使用默认配置({config_key}): {config_path}")
            self._configs[config_key] = default_config.copy()
            # 保存默认配置
            self._save_single_config(config_key)

        return self._configs[config_key].copy()

    def _save_single_config(self, config_key: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """保存单个配置文件"""
        try:
            # 暂停文件监控，避免自己触发的修改触发重新加载
            old_watch_state = self._watch_enabled
            self._watch_enabled = False

            # 确定要保存的配置
            if config is not None:
                save_config = config
                # 更新内存中的配置
                if config_key in self._configs:
                    self._configs[config_key].update(config)
                else:
                    self._configs[config_key] = config
            else:
                save_config = self._configs.get(config_key, {})

            config_path = self._config_paths.get(config_key)
            if not config_path:
                return False

            # 确保配置目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            # 写入文件
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(save_config, f, ensure_ascii=False, indent=4, sort_keys=True)

            print(f"配置已保存({config_key}): {config_path}")

            # 恢复文件监控
            self._watch_enabled = old_watch_state

            # 触发配置变更回调
            self._trigger_config_change_callbacks(config_key)

            return True

        except Exception as e:
            print(f"保存配置失败({config_key}): {e}")
            # 恢复文件监控
            self._watch_enabled = True
            return False

    def _start_all_config_watchers(self):
        """启动所有配置文件的监控"""
        system = platform.system()

        # 只在Windows和macOS/Linux启用文件监控
        # 注意：文件监控可能会增加系统资源消耗
        if system in ["Windows", "Darwin", "Linux"]:
            for config_key in self.CONFIG_FILES.keys():
                self._start_config_watcher(config_key)

    def _start_config_watcher(self, config_key: str):
        """启动单个配置文件的监控"""
        try:
            config_path = self._config_paths.get(config_key)
            if not config_path:
                return

            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                return

            # 创建观察器
            event_handler = ConfigFileHandler(self, config_key)
            observer = Observer()
            observer.schedule(event_handler, config_dir, recursive=False)
            observer.start()

            self._file_observers[config_key] = observer
            print(f"启动配置文件监控({config_key}): {config_path}")

        except Exception as e:
            print(f"启动配置文件监控失败({config_key}): {e}")

    def _stop_all_config_watchers(self):
        """停止所有配置文件的监控"""
        for config_key, observer in self._file_observers.items():
            try:
                observer.stop()
                observer.join()
                print(f"停止配置文件监控({config_key})")
            except:
                pass
        self._file_observers.clear()

    def _trigger_config_change_callbacks(self, config_key: str):
        """触发配置变更回调"""
        if config_key in self._config_change_callbacks:
            for callback in self._config_change_callbacks[config_key]:
                try:
                    callback(self._configs[config_key].copy())
                except Exception as e:
                    print(f"配置变更回调执行失败: {e}")

    # ========== 公共API ==========

    def get_config_list(self) -> List[str]:
        """获取所有支持的配置键列表"""
        return list(self.CONFIG_FILES.keys())

    def get_config(self, config_key: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取配置值
        :param config_key: 配置键（如 "user_config"）
        :param key: 配置项键，为None时返回整个配置
        :param default: 默认值（如果键不存在）
        :return: 配置值
        """
        if config_key not in self._configs:
            # 如果配置不存在，尝试加载
            self._load_single_config(config_key)

        config_data = self._configs.get(config_key, {})

        if key is None:
            return config_data.copy()

        return config_data.get(key, default)

    def set_config(self, config_key: str, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        设置配置值
        :param config_key: 配置键（如 "user_config"）
        :param key: 配置项键
        :param value: 配置值
        :param auto_save: 是否自动保存
        :return: 是否成功
        """
        if config_key not in self._configs:
            # 如果配置不存在，初始化它
            self._configs[config_key] = self._default_configs.get(config_key, {}).copy()

        self._configs[config_key][key] = value

        if auto_save:
            return self.save_config(config_key)

        return True

    def save_config(self, config_key: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存配置文件
        :param config_key: 配置键（如 "user_config"）
        :param config: 要保存的配置字典，为None时保存当前配置
        :return: 是否保存成功
        """
        return self._save_single_config(config_key, config)

    def reload_config(self, config_key: str = None) -> bool:  # type: ignore
        """
        重新加载配置文件
        :param config_key: 配置键，为None时重新加载所有配置
        :return: 是否成功
        """
        try:
            if config_key is None:
                # 重新加载所有配置
                for key in self.CONFIG_FILES.keys():
                    self._load_single_config(key, force=True)
                return True
            else:
                # 重新加载指定配置
                return self._load_single_config(config_key, force=True) is not None
        except Exception as e:
            print(f"重新加载配置失败: {e}")
            return False

    def reset_config(self, config_key: str) -> bool:
        """重置配置为默认值"""
        if config_key in self._default_configs:
            self._configs[config_key] = self._default_configs[config_key].copy()
            return self.save_config(config_key)
        return False

    def get_config_path(self, config_key: str) -> Optional[str]:
        """获取配置文件路径"""
        return self._config_paths.get(config_key)

    def add_config_change_callback(self, config_key: str, callback: Callable[[Dict[str, Any]], None]):
        """添加配置变更回调"""
        if config_key not in self._config_change_callbacks:
            self._config_change_callbacks[config_key] = []
        self._config_change_callbacks[config_key].append(callback)

    def remove_config_change_callback(self, config_key: str, callback: Callable[[Dict[str, Any]], None]):
        """移除配置变更回调"""
        if config_key in self._config_change_callbacks and callback in self._config_change_callbacks[config_key]:
            self._config_change_callbacks[config_key].remove(callback)

    def add_recent_file(self, file_path: str) -> bool:
        """添加最近使用的文件（添加到user_config）"""
        if not file_path or not os.path.exists(file_path):
            return False

        recent_files = self.get_config("user_config", "recent_files", [])

        # 移除重复项
        if file_path in recent_files:
            recent_files.remove(file_path)

        # 添加到开头
        recent_files.insert(0, file_path)

        # 限制最大数量
        max_files = self.get_config("user_config", "max_recent_files", 10)
        if len(recent_files) > max_files:
            recent_files = recent_files[:max_files]

        # 更新配置
        return self.set_config("user_config", "recent_files", recent_files)

    def clear_recent_files(self) -> bool:
        """清空最近使用的文件"""
        return self.set_config("user_config", "recent_files", [])

    def get_app_name(self) -> str:
        """获取应用名称"""
        return self._app_name

    def get_app_data_dir(self) -> str:
        """获取应用程序数据目录（跨平台）"""
        system = platform.system()
        home = os.path.expanduser("~")

        if system == "Windows":
            appdata = os.getenv("LOCALAPPDATA")
            if appdata:
                return os.path.join(appdata, self._app_name)
            else:
                return os.path.join(home, "AppData", "Local", self._app_name)
        elif system == "Darwin":  # macOS
            return os.path.join(home, "Library", "Application Support", self._app_name)
        else:  # Linux and others
            return os.path.join(home, ".config", self._app_name)

    def get_exe_dir(self) -> str:
        """获取exe所在目录（打包环境）或项目根目录（开发环境）"""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        else:
            current_file = Path(__file__).resolve()
            return str(current_file.parent.parent)

    def enable_watch(self, enabled: bool = True):
        """启用或禁用文件监控"""
        self._watch_enabled = enabled
        if not enabled:
            self._stop_all_config_watchers()
        else:
            self._start_all_config_watchers()

    def cleanup(self):
        """清理资源"""
        self._stop_all_config_watchers()


# 全局单例实例
_config_manager_instance = None


def get_config_manager() -> ConfigManager:
    """获取配置管理器单例"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance


# 便捷函数
def get_config_list() -> List[str]:
    """获取所有支持的配置键列表"""
    return get_config_manager().get_config_list()


def get_config(config_key: str, key: Optional[str] = None, default: Any = None) -> Any:
    """获取配置值"""
    return get_config_manager().get_config(config_key, key, default)


def set_config(config_key: str, key: str, value: Any, auto_save: bool = True) -> bool:
    """设置配置值"""
    return get_config_manager().set_config(config_key, key, value, auto_save)


def save_config(config_key: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """保存配置文件"""
    return get_config_manager().save_config(config_key, config)


def reload_config(config_key: str = None) -> bool:  # type: ignore
    """重新加载配置文件"""
    return get_config_manager().reload_config(config_key)


def get_config_path(config_key: str) -> Optional[str]:
    """获取配置文件路径"""
    return get_config_manager().get_config_path(config_key)


def get_app_name() -> str:
    """获取应用名称"""
    return get_config_manager().get_app_name()


def get_app_data_dir() -> str:
    """获取应用程序数据目录"""
    return get_config_manager().get_app_data_dir()


def get_exe_dir() -> str:
    """获取exe所在目录或项目根目录"""
    return get_config_manager().get_exe_dir()


def add_recent_file(file_path: str) -> bool:
    """添加最近使用的文件"""
    return get_config_manager().add_recent_file(file_path)


def clear_recent_files() -> bool:
    """清空最近使用的文件"""
    return get_config_manager().clear_recent_files()


def add_config_change_callback(config_key: str, callback: Callable[[Dict[str, Any]], None]):
    """添加配置变更回调"""
    get_config_manager().add_config_change_callback(config_key, callback)


def remove_config_change_callback(config_key: str, callback: Callable[[Dict[str, Any]], None]):
    """移除配置变更回调"""
    get_config_manager().remove_config_change_callback(config_key, callback)


def enable_config_watch(enabled: bool = True):
    """启用或禁用配置监控"""
    get_config_manager().enable_watch(enabled)


def cleanup_config_manager():
    """清理配置管理器资源"""
    if _config_manager_instance:
        _config_manager_instance.cleanup()


# 预定义的配置键常量
USER_CONFIG = "user_config"
APP_CONFIG = "app_config"
SYSTEM_CONFIG = "system_config"
THEME_CONFIG = "theme_config"
WINDOW_CONFIG = "window_config"
