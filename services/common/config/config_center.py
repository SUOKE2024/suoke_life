"""
config_center - 索克生活项目模块
"""

    import consul
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
import consul
import json
import logging
import threading
import time
import yaml

#!/usr/bin/env python3
"""
配置中心客户端
支持Consul、Etcd等配置中心
"""



# 尝试导入配置中心客户端
try:

    HAS_CONSUL = True
except ImportError:
    HAS_CONSUL = False

try:

    HAS_ETCD = True
except ImportError:
    HAS_ETCD = False

logger = logging.getLogger(__name__)

@dataclass
class ConfigChange:
    """配置变更事件"""

    key: str
    old_value: Any
    new_value: Any
    operation: str  # create, update, delete
    timestamp: float

class ConfigFormat(Enum):
    """配置格式枚举"""

    JSON = "json"
    YAML = "yaml"
    TEXT = "text"

@dataclass
class ConfigItem:
    """配置项"""

    key: str
    value: Any
    format: ConfigFormat
    version: int
    created_at: datetime
    updated_at: datetime
    description: str = ""
    tags: list[str] = None

class ConfigCenter:
    """配置中心主类"""

    def __init__(
        self,
        consul_host: str = "localhost",
        consul_port: int = 8500,
        environment: str = "development",
    ):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.environment = environment
        self.config_cache: dict[str, ConfigItem] = {}
        self.watchers: dict[str, list[Callable]] = {}
        self.watch_threads: dict[str, threading.Thread] = {}
        self._stop_event = threading.Event()

        # 配置前缀
        self.config_prefix = f"config/{environment}"

        logger.info(f"ConfigCenter initialized for environment: {environment}")

    def get_config(
        self, key: str, default: Any = None, config_type: type | None = None
    ) -> Any:
        """获取配置值"""
        full_key = f"{self.config_prefix}/{key}"

        # 先检查缓存
        if full_key in self.config_cache:
            config_item = self.config_cache[full_key]
            return self._convert_value(config_item.value, config_type)

        try:
            _, data = self.consul.kv.get(full_key)
            if data:
                config_item = self._parse_config_data(full_key, data)
                self.config_cache[full_key] = config_item
                return self._convert_value(config_item.value, config_type)
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")

        return default

    def set_config(
        self,
        key: str,
        value: Any,
        description: str = "",
        tags: list[str] | None = None,
        config_format: ConfigFormat = None,
    ) -> bool:
        """设置配置值"""
        full_key = f"{self.config_prefix}/{key}"

        try:
            # 自动检测格式
            if config_format is None:
                config_format = self._detect_format(value)

            # 序列化值
            serialized_value = self._serialize_value(value, config_format)

            # 构建元数据
            metadata = {
                "format": config_format.value,
                "description": description,
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": self._get_next_version(full_key),
            }

            # 存储配置值
            success = self.consul.kv.put(full_key, serialized_value)

            # 存储元数据
            if success:
                metadata_key = f"{full_key}/_metadata"
                self.consul.kv.put(metadata_key, json.dumps(metadata))

                # 更新缓存
                config_item = ConfigItem(
                    key=key,
                    value=value,
                    format=config_format,
                    version=metadata["version"],
                    created_at=datetime.fromisoformat(metadata["created_at"]),
                    updated_at=datetime.fromisoformat(metadata["updated_at"]),
                    description=description,
                    tags=tags,
                )
                self.config_cache[full_key] = config_item

                # 通知观察者
                self._notify_watchers(key, value)

                logger.info(f"Config set: {key} = {value}")
                return True

        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")

        return False

    def delete_config(self, key: str) -> bool:
        """删除配置"""
        full_key = f"{self.config_prefix}/{key}"

        try:
            # 删除配置值和元数据
            success1 = self.consul.kv.delete(full_key)
            success2 = self.consul.kv.delete(f"{full_key}/_metadata")

            # 从缓存中移除
            if full_key in self.config_cache:
                del self.config_cache[full_key]

            # 通知观察者
            self._notify_watchers(key, None)

            logger.info(f"Config deleted: {key}")
            return success1 and success2

        except Exception as e:
            logger.error(f"Failed to delete config {key}: {e}")
            return False

    def watch_config(self, key: str, callback: Callable[[str, Any], None]):
        """监听配置变化"""
        if key not in self.watchers:
            self.watchers[key] = []

        self.watchers[key].append(callback)

        # 启动监听线程
        if key not in self.watch_threads:
            self._start_watch_thread(key)

        logger.info(f"Started watching config: {key}")

    def unwatch_config(self, key: str, callback: Callable[[str, Any], None]):
        """取消监听配置变化"""
        if key in self.watchers and callback in self.watchers[key]:
            self.watchers[key].remove(callback)

            # 如果没有观察者了，停止监听线程
            if not self.watchers[key] and key in self.watch_threads:
                self.watch_threads[key].join(timeout=1)
                del self.watch_threads[key]

    def get_config_history(self, key: str, limit: int = 10) -> list[ConfigItem]:
        """获取配置历史版本"""
        # 这里简化实现，实际应该存储历史版本
        full_key = f"{self.config_prefix}/{key}"
        if full_key in self.config_cache:
            return [self.config_cache[full_key]]
        return []

    def list_configs(self, prefix: str = "") -> list[ConfigItem]:
        """列出配置"""
        search_prefix = (
            f"{self.config_prefix}/{prefix}" if prefix else self.config_prefix
        )

        try:
            _, configs = self.consul.kv.get(search_prefix, recurse=True)
            if not configs:
                return []

            result = []
            for config in configs:
                key = config["Key"]

                # 跳过元数据
                if key.endswith("/_metadata"):
                    continue

                config_item = self._parse_config_data(key, config)
                result.append(config_item)

            return result

        except Exception as e:
            logger.error(f"Failed to list configs: {e}")
            return []

    def load_from_file(self, config_file: str, prefix: str = ""):
        """从文件加载配置"""
        file_path = Path(config_file)

        if not file_path.exists():
            logger.error(f"Config file not found: {config_file}")
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    config_data = yaml.safe_load(f)
                    config_format = ConfigFormat.YAML
                elif file_path.suffix.lower() == ".json":
                    config_data = json.load(f)
                    config_format = ConfigFormat.JSON
                else:
                    config_data = f.read()
                    config_format = ConfigFormat.TEXT

            # 递归上传配置
            if isinstance(config_data, dict):
                self._upload_config_dict(config_data, prefix, config_format)
            else:
                key = prefix or file_path.stem
                self.set_config(
                    key,
                    config_data,
                    description=f"Loaded from {config_file}",
                    config_format=config_format,
                )

            logger.info(f"Config loaded from file: {config_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load config from file {config_file}: {e}")
            return False

    def export_to_file(
        self,
        output_file: str,
        prefix: str = "",
        config_format: ConfigFormat = ConfigFormat.YAML,
    ):
        """导出配置到文件"""
        configs = self.list_configs(prefix)

        if not configs:
            logger.warning(f"No configs found with prefix: {prefix}")
            return False

        try:
            # 构建配置字典
            config_dict = {}
            for config in configs:
                # 移除环境前缀
                key = config.key.replace(f"{self.config_prefix}/", "")
                if prefix:
                    key = key.replace(f"{prefix}/", "")

                # 构建嵌套字典
                self._set_nested_value(config_dict, key.split("/"), config.value)

            # 写入文件
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                if config_format == ConfigFormat.YAML:
                    yaml.dump(
                        config_dict,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )
                elif config_format == ConfigFormat.JSON:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                else:
                    f.write(str(config_dict))

            logger.info(f"Config exported to file: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export config to file {output_file}: {e}")
            return False

    def _parse_config_data(self, key: str, data: dict) -> ConfigItem:
        """解析配置数据"""
        value = data["Value"].decode() if data["Value"] else ""

        # 获取元数据
        metadata_key = f"{key}/_metadata"
        try:
            _, metadata_data = self.consul.kv.get(metadata_key)
            if metadata_data:
                metadata = json.loads(metadata_data["Value"].decode())
            else:
                metadata = {
                    "format": "text",
                    "description": "",
                    "tags": [],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "version": 1,
                }
        except:
            metadata = {
                "format": "text",
                "description": "",
                "tags": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": 1,
            }

        # 解析值
        config_format = ConfigFormat(metadata.get("format", "text"))
        parsed_value = self._deserialize_value(value, config_format)

        return ConfigItem(
            key=key.replace(f"{self.config_prefix}/", ""),
            value=parsed_value,
            format=config_format,
            version=metadata.get("version", 1),
            created_at=datetime.fromisoformat(metadata.get("created_at")),
            updated_at=datetime.fromisoformat(metadata.get("updated_at")),
            description=metadata.get("description", ""),
            tags=metadata.get("tags", []),
        )

    def _detect_format(self, value: Any) -> ConfigFormat:
        """自动检测配置格式"""
        if isinstance(value, dict | list):
            return ConfigFormat.JSON
        elif isinstance(value, str):
            # 尝试解析为JSON
            try:
                json.loads(value)
                return ConfigFormat.JSON
            except:
                pass

            # 尝试解析为YAML
            try:
                yaml.safe_load(value)
                return ConfigFormat.YAML
            except:
                pass

        return ConfigFormat.TEXT

    def _serialize_value(self, value: Any, config_format: ConfigFormat) -> str:
        """序列化配置值"""
        if config_format == ConfigFormat.JSON:
            return json.dumps(value, ensure_ascii=False, indent=2)
        elif config_format == ConfigFormat.YAML:
            return yaml.dump(value, default_flow_style=False, allow_unicode=True)
        else:
            return str(value)

    def _deserialize_value(self, value: str, config_format: ConfigFormat) -> Any:
        """反序列化配置值"""
        try:
            if config_format == ConfigFormat.JSON:
                return json.loads(value)
            elif config_format == ConfigFormat.YAML:
                return yaml.safe_load(value)
            else:
                return value
        except:
            return value

    def _convert_value(self, value: Any, target_type: type) -> Any:
        """转换值类型"""
        if target_type is None:
            return value

        try:
            if target_type == bool:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == str:
                return str(value)
            else:
                return value
        except:
            return value

    def _get_next_version(self, key: str) -> int:
        """获取下一个版本号"""
        if key in self.config_cache:
            return self.config_cache[key].version + 1
        return 1

    def _notify_watchers(self, key: str, value: Any):
        """通知观察者"""
        if key in self.watchers:
            for callback in self.watchers[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    logger.error(f"Error in config watcher callback: {e}")

    def _start_watch_thread(self, key: str):
        """启动配置监听线程"""

        def watch_loop():
            full_key = f"{self.config_prefix}/{key}"
            index = None

            while not self._stop_event.is_set():
                try:
                    index, data = self.consul.kv.get(full_key, index=index, wait="30s")

                    if data:
                        config_item = self._parse_config_data(full_key, data)
                        old_value = self.config_cache.get(full_key)

                        # 检查是否有变化
                        if not old_value or old_value.value != config_item.value:
                            self.config_cache[full_key] = config_item
                            self._notify_watchers(key, config_item.value)
                    # 配置被删除
                    elif full_key in self.config_cache:
                        del self.config_cache[full_key]
                        self._notify_watchers(key, None)

                except Exception as e:
                    logger.error(f"Error watching config {key}: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=watch_loop, daemon=True)
        thread.start()
        self.watch_threads[key] = thread

    def _upload_config_dict(
        self,
        config_data: dict,
        prefix: str,
        config_format: ConfigFormat,
        parent_key: str = "",
    ):
        """递归上传配置字典"""
        for key, value in config_data.items():
            full_key = f"{parent_key}/{key}" if parent_key else key
            if prefix:
                full_key = f"{prefix}/{full_key}"

            if isinstance(value, dict):
                self._upload_config_dict(value, "", config_format, full_key)
            else:
                self.set_config(
                    full_key,
                    value,
                    description="Loaded from file",
                    config_format=config_format,
                )

    def _set_nested_value(self, dictionary: dict, keys: list[str], value: Any):
        """设置嵌套字典值"""
        for key in keys[:-1]:
            if key not in dictionary:
                dictionary[key] = {}
            dictionary = dictionary[key]
        dictionary[keys[-1]] = value

    def clear_cache(self):
        """清空配置缓存"""
        self.config_cache.clear()
        logger.debug("Config cache cleared")

    def shutdown(self):
        """关闭配置中心"""
        logger.info("Shutting down ConfigCenter...")

        # 停止所有监听线程
        self._stop_event.set()

        for thread in self.watch_threads.values():
            thread.join(timeout=5)

        self.watch_threads.clear()
        self.watchers.clear()
        self.config_cache.clear()

        logger.info("ConfigCenter shutdown complete")

# 服务配置管理器
class ServiceConfig:
    """服务配置管理器"""

    def __init__(self, service_name: str, config_center: ConfigCenter):
        self.service_name = service_name
        self.config_center = config_center
        self.config_prefix = f"services/{service_name}"

    def get(self, key: str, default: Any = None, config_type: type | None = None) -> Any:
        """获取服务配置"""
        full_key = f"{self.config_prefix}/{key}"
        return self.config_center.get_config(full_key, default, config_type)

    def set(self, key: str, value: Any, description: str = "", tags: list[str] | None = None):
        """设置服务配置"""
        full_key = f"{self.config_prefix}/{key}"
        return self.config_center.set_config(full_key, value, description, tags)

    def watch(self, key: str, callback: Callable[[str, Any], None]):
        """监听服务配置变化"""
        full_key = f"{self.config_prefix}/{key}"
        return self.config_center.watch_config(full_key, callback)

    def load_from_file(self, config_file: str):
        """从文件加载服务配置"""
        return self.config_center.load_from_file(config_file, self.config_prefix)

    def export_to_file(
        self, output_file: str, config_format: ConfigFormat = ConfigFormat.YAML
    ):
        """导出服务配置到文件"""
        return self.config_center.export_to_file(
            output_file, self.config_prefix, config_format
        )

# 全局配置中心实例
_config_center = None

def get_config_center(
    consul_host: str = "localhost",
    consul_port: int = 8500,
    environment: str = "development",
) -> ConfigCenter:
    """获取配置中心单例"""
    global _config_center
    if _config_center is None:
        _config_center = ConfigCenter(consul_host, consul_port, environment)
    return _config_center

# 使用示例
if __name__ == "__main__":
    # 创建配置中心
    config_center = ConfigCenter(environment="development")

    # 设置配置
    config_center.set_config("database/host", "localhost", "数据库主机地址")
    config_center.set_config("database/port", 5432, "数据库端口")
    config_center.set_config(
        "database/config", {"max_connections": 100, "timeout": 30}, "数据库连接配置"
    )

    # 获取配置
    db_host = config_center.get_config("database/host")
    db_port = config_center.get_config("database/port", config_type=int)
    db_config = config_center.get_config("database/config")

    print(f"Database: {db_host}:{db_port}")
    print(f"Config: {db_config}")

    # 监听配置变化
    def on_config_change(key, value):
        print(f"Config changed: {key} = {value}")

    config_center.watch_config("database/host", on_config_change)

    # 服务配置管理
    service_config = ServiceConfig("xiaoai-service", config_center)
    service_config.set("model_version", "v2.1.0", "AI模型版本")
    service_config.set("max_requests_per_minute", 1000, "每分钟最大请求数")

    model_version = service_config.get("model_version")
    print(f"Model version: {model_version}")

    # 从文件加载配置
    # config_center.load_from_file("config.yaml")

    # 导出配置
    # config_center.export_to_file("exported_config.yaml")

    try:
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        config_center.shutdown()
