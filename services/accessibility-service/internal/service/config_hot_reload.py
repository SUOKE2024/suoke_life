"""
配置热重载系统
支持配置文件变更时自动重新加载，无需重启服务
"""

import asyncio
import hashlib
import json
import logging
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class ConfigFormat(Enum):
    """配置文件格式"""

    JSON = "json"
    YAML = "yaml"
    YML = "yml"
    TOML = "toml"
    INI = "ini"


@dataclass
class ConfigFile:
    """配置文件信息"""

    path: Path
    format: ConfigFormat
    last_modified: float = 0.0
    content_hash: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """初始化后处理"""
        if isinstance(self.path, str):
            self.path = Path(self.path)

        if self.path.exists():
            self.last_modified = self.path.stat().st_mtime
            self.content_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """计算文件内容哈希"""
        if not self.path.exists():
            return ""

        try:
            with open(self.path, "rb") as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            return ""

    def has_changed(self) -> bool:
        """检查文件是否已更改"""
        if not self.path.exists():
            return False

        current_modified = self.path.stat().st_mtime
        current_hash = self._calculate_hash()

        return (
            current_modified != self.last_modified or current_hash != self.content_hash
        )

    def update_metadata(self) -> None:
        """更新文件元数据"""
        if self.path.exists():
            self.last_modified = self.path.stat().st_mtime
            self.content_hash = self._calculate_hash()


class ConfigChangeEvent:
    """配置变更事件"""

    def __init__(
        self,
        file_path: Path,
        old_data: dict[str, Any],
        new_data: dict[str, Any],
        change_type: str = "modified",
    ):
        self.file_path = file_path
        self.old_data = old_data
        self.new_data = new_data
        self.change_type = change_type
        self.timestamp = time.time()

    def get_changed_keys(self) -> set[str]:
        """获取变更的键"""
        changed_keys = set()

        # 检查新增和修改的键
        for key, value in self.new_data.items():
            if key not in self.old_data or self.old_data[key] != value:
                changed_keys.add(key)

        # 检查删除的键
        for key in self.old_data:
            if key not in self.new_data:
                changed_keys.add(key)

        return changed_keys


class ConfigHotReloader:
    """配置热重载器"""

    def __init__(self, check_interval: float = 1.0):
        self.config_files: dict[Path, ConfigFile] = {}
        self.change_callbacks: list[Callable[[ConfigChangeEvent], None]] = []
        self.check_interval = check_interval
        self.running = False
        self.logger = logging.getLogger("config_hot_reloader")

        # 线程安全
        self._lock = threading.RLock()

    def add_config_file(
        self, file_path: str, config_format: ConfigFormat | None = None
    ) -> bool:
        """添加配置文件监控"""
        path = Path(file_path)

        if not path.exists():
            self.logger.error(f"配置文件不存在: {path}")
            return False

        # 自动检测格式
        if config_format is None:
            suffix = path.suffix.lower()
            format_map = {
                ".json": ConfigFormat.JSON,
                ".yaml": ConfigFormat.YAML,
                ".yml": ConfigFormat.YML,
                ".toml": ConfigFormat.TOML,
                ".ini": ConfigFormat.INI,
            }
            config_format = format_map.get(suffix, ConfigFormat.YAML)

        with self._lock:
            config_file = ConfigFile(path=path, format=config_format)

            # 加载初始数据
            if self._load_config_data(config_file):
                self.config_files[path] = config_file
                self.logger.info(f"添加配置文件监控: {path} ({config_format.value})")
                return True
            else:
                self.logger.error(f"加载配置文件失败: {path}")
                return False

    def remove_config_file(self, file_path: str):
        """移除配置文件监控"""
        path = Path(file_path)

        with self._lock:
            if path in self.config_files:
                del self.config_files[path]
                self.logger.info(f"移除配置文件监控: {path}")

    def add_change_callback(self, callback: Callable[[ConfigChangeEvent], None]):
        """添加配置变更回调"""
        self.change_callbacks.append(callback)
        self.logger.info(f"添加配置变更回调: {callback.__name__}")

    def remove_change_callback(self, callback: Callable[[ConfigChangeEvent], None]):
        """移除配置变更回调"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
        self.logger.info(f"移除配置变更回调: {callback.__name__}")

    def start(self) -> None:
        """启动热重载监控"""
        if self.running:
            self.logger.warning("配置热重载已在运行")
            return

        self.running = True

        # 启动定期检查任务
        asyncio.create_task(self._periodic_check())

        self.logger.info("配置热重载监控已启动")

    def stop(self) -> None:
        """停止热重载监控"""
        if not self.running:
            return

        self.running = False
        self.logger.info("配置热重载监控已停止")

    def get_config(self, file_path: str) -> dict[str, Any] | None:
        """获取配置数据"""
        path = Path(file_path)

        with self._lock:
            config_file = self.config_files.get(path)
            if config_file:
                return config_file.data.copy()
            return None

    def get_all_configs(self) -> dict[str, dict[str, Any]]:
        """获取所有配置数据"""
        with self._lock:
            return {
                str(path): config_file.data.copy()
                for path, config_file in self.config_files.items()
            }

    def reload_config(self, file_path: str) -> bool:
        """手动重新加载配置"""
        path = Path(file_path)

        with self._lock:
            config_file = self.config_files.get(path)
            if not config_file:
                self.logger.error(f"配置文件未监控: {path}")
                return False

            return self._reload_config_file(config_file)

    def reload_all_configs(self) -> dict[str, bool]:
        """重新加载所有配置"""
        results = {}

        with self._lock:
            for path, config_file in self.config_files.items():
                results[str(path)] = self._reload_config_file(config_file)

        return results

    async def _periodic_check(self) -> None:
        """定期检查配置文件变更"""
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)

                with self._lock:
                    for path, config_file in self.config_files.items():
                        if config_file.has_changed():
                            await self._handle_file_change(path)

            except Exception as e:
                self.logger.error(f"定期检查配置文件异常: {e}")

    async def _handle_file_change(self, file_path: Path):
        """处理文件变更"""
        with self._lock:
            config_file = self.config_files.get(file_path)
            if not config_file:
                return

            old_data = config_file.data.copy()

            if self._reload_config_file(config_file):
                # 创建变更事件
                event = ConfigChangeEvent(
                    file_path=file_path,
                    old_data=old_data,
                    new_data=config_file.data,
                    change_type="modified",
                )

                # 通知所有回调
                await self._notify_callbacks(event)

    async def _notify_callbacks(self, event: ConfigChangeEvent):
        """通知配置变更回调"""
        for callback in self.change_callbacks[:]:  # 复制列表避免并发修改
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error(f"配置变更回调异常: {callback.__name__}: {e}")

    def _reload_config_file(self, config_file: ConfigFile) -> bool:
        """重新加载配置文件"""
        try:
            if self._load_config_data(config_file):
                config_file.update_metadata()
                self.logger.info(f"配置文件重新加载成功: {config_file.path}")
                return True
            else:
                self.logger.error(f"配置文件重新加载失败: {config_file.path}")
                return False
        except Exception as e:
            self.logger.error(f"重新加载配置文件异常: {config_file.path}: {e}")
            return False

    def _load_config_data(self, config_file: ConfigFile) -> bool:
        """加载配置文件数据"""
        try:
            with open(config_file.path, encoding="utf-8") as f:
                if config_file.format == ConfigFormat.JSON:
                    config_file.data = json.load(f)
                elif config_file.format in [ConfigFormat.YAML, ConfigFormat.YML]:
                    config_file.data = yaml.safe_load(f) or {}
                elif config_file.format == ConfigFormat.TOML:
                    try:
                        import tomli

                        content = f.read()
                        config_file.data = tomli.loads(content)
                    except ImportError:
                        self.logger.error("需要安装 tomli 库来支持 TOML 格式")
                        return False
                elif config_file.format == ConfigFormat.INI:
                    import configparser

                    parser = configparser.ConfigParser()
                    parser.read_string(f.read())
                    config_file.data = {
                        section: dict(parser[section]) for section in parser.sections()
                    }
                else:
                    self.logger.error(f"不支持的配置格式: {config_file.format}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"加载配置文件失败: {config_file.path}: {e}")
            return False


# 全局配置热重载器实例
config_hot_reloader = ConfigHotReloader()


# 装饰器：配置变更时自动重新加载
def config_reload_on_change(config_path: str):
    """配置变更时自动重新加载装饰器"""

    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs) -> Any:
            original_init(self, *args, **kwargs)

            # 添加配置文件监控
            config_hot_reloader.add_config_file(config_path)

            # 添加变更回调
            def on_config_change(event: ConfigChangeEvent):
                if hasattr(self, "reload_config"):
                    self.reload_config(event.new_data)

            config_hot_reloader.add_change_callback(on_config_change)

        cls.__init__ = new_init
        return cls

    return decorator


# 使用示例
if __name__ == "__main__":

    async def demo_config_hot_reload() -> None:
        """演示配置热重载"""
        print("🚀 配置热重载系统演示")

        # 创建测试配置文件
        test_config_path = "test_config.yaml"
        test_config = {
            "app": {
                "name": "accessibility-service",
                "version": "1.0.0",
                "debug": False,
            },
            "database": {"host": "localhost", "port": 5432, "name": "accessibility_db"},
        }

        with open(test_config_path, "w") as f:
            yaml.dump(test_config, f)

        # 创建热重载器
        reloader = ConfigHotReloader(check_interval=0.5)

        # 配置变更回调
        def on_config_change(event: ConfigChangeEvent):
            print(f"📝 配置文件变更: {event.file_path}")
            print(f"   变更的键: {event.get_changed_keys()}")
            print(
                f"   新配置: {json.dumps(event.new_data, indent=2, ensure_ascii=False)}"
            )

        # 添加配置文件和回调
        reloader.add_config_file(test_config_path)
        reloader.add_change_callback(on_config_change)

        # 启动热重载
        reloader.start()

        print("📊 初始配置:")
        initial_config = reloader.get_config(test_config_path)
        print(json.dumps(initial_config, indent=2, ensure_ascii=False))

        print("\n⏳ 等待配置文件变更...")
        print("请手动修改 test_config.yaml 文件来测试热重载功能")

        # 模拟配置变更
        await asyncio.sleep(2)

        # 修改配置文件
        test_config["app"]["debug"] = True
        test_config["app"]["version"] = "1.1.0"
        test_config["monitoring"] = {"enabled": True, "interval": 30}

        with open(test_config_path, "w") as f:
            yaml.dump(test_config, f)

        print("🔄 已修改配置文件，等待热重载...")
        await asyncio.sleep(3)

        # 获取更新后的配置
        updated_config = reloader.get_config(test_config_path)
        print("📊 更新后配置:")
        print(json.dumps(updated_config, indent=2, ensure_ascii=False))

        # 停止热重载
        reloader.stop()

        # 清理测试文件
        os.remove(test_config_path)

        print("✅ 配置热重载系统演示完成")

    asyncio.run(demo_config_hot_reload())
