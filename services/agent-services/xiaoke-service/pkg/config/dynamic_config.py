#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态配置管理器
支持配置热重载、配置版本管理和回滚、环境特定配置覆盖、配置变更通知等功能
"""

import asyncio
import logging
import json
import yaml
import os
import hashlib
import time
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import aioredis

logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    """配置源类型"""
    FILE = "file"
    REDIS = "redis"
    ENVIRONMENT = "environment"
    REMOTE = "remote"

class ConfigFormat(Enum):
    """配置格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"

@dataclass
class ConfigVersion:
    """配置版本信息"""
    version: str
    timestamp: datetime
    checksum: str
    source: ConfigSource
    data: Dict[str, Any]
    description: str = ""

@dataclass
class ConfigChange:
    """配置变更信息"""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: ConfigSource

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件监控处理器"""
    
    def __init__(self, config_manager):
        """
        初始化文件监控处理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # 防止重复触发
        current_time = time.time()
        if (file_path in self.last_modified and 
            current_time - self.last_modified[file_path] < 1.0):
            return
        
        self.last_modified[file_path] = current_time
        
        # 检查是否是监控的配置文件
        if file_path in self.config_manager.watched_files:
            logger.info("检测到配置文件变更: %s", file_path)
            asyncio.create_task(self.config_manager._reload_file(file_path))

class DynamicConfigManager:
    """动态配置管理器"""
    
    def __init__(self, redis_url: str = None):
        """
        初始化动态配置管理器
        
        Args:
            redis_url: Redis连接URL（可选）
        """
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # 配置数据
        self.config_data: Dict[str, Any] = {}
        self.config_versions: List[ConfigVersion] = []
        self.max_versions = 10  # 最大保留版本数
        
        # 文件监控
        self.watched_files: Dict[str, ConfigFormat] = {}
        self.file_observer: Optional[Observer] = None
        self.file_handler: Optional[ConfigFileHandler] = None
        
        # 变更通知
        self.change_callbacks: List[Callable] = []
        self.key_callbacks: Dict[str, List[Callable]] = {}
        
        # 环境配置
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.env_prefix = os.getenv('CONFIG_ENV_PREFIX', 'XIAOKE_')
        
        # 远程配置
        self.remote_config_url: Optional[str] = None
        self.remote_poll_interval = 60  # 远程配置轮询间隔（秒）
        self.remote_poll_task: Optional[asyncio.Task] = None
        
        # 配置缓存
        self.cache_enabled = True
        self.cache_ttl = 300  # 缓存TTL（秒）
        
        logger.info("动态配置管理器初始化完成，环境: %s", self.environment)
    
    async def initialize(self):
        """初始化配置管理器"""
        # 初始化Redis连接（如果提供）
        if self.redis_url:
            try:
                self.redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("Redis配置存储连接建立成功")
            except Exception as e:
                logger.warning("Redis配置存储连接失败: %s", str(e))
                self.redis_client = None
        
        # 加载环境变量配置
        await self._load_environment_config()
        
        # 启动文件监控
        self._start_file_watcher()
        
        logger.info("动态配置管理器初始化完成")
    
    def add_file_source(self, file_path: str, format_type: ConfigFormat = None):
        """
        添加文件配置源
        
        Args:
            file_path: 配置文件路径
            format_type: 配置文件格式
        """
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            logger.warning("配置文件不存在: %s", file_path)
            return
        
        # 自动检测格式
        if format_type is None:
            ext = Path(file_path).suffix.lower()
            if ext in ['.json']:
                format_type = ConfigFormat.JSON
            elif ext in ['.yaml', '.yml']:
                format_type = ConfigFormat.YAML
            elif ext in ['.toml']:
                format_type = ConfigFormat.TOML
            else:
                logger.warning("无法识别配置文件格式: %s", file_path)
                return
        
        self.watched_files[file_path] = format_type
        
        # 立即加载配置
        asyncio.create_task(self._load_file_config(file_path, format_type))
        
        logger.info("添加配置文件源: %s (%s)", file_path, format_type.value)
    
    def set_remote_source(self, url: str, poll_interval: int = 60):
        """
        设置远程配置源
        
        Args:
            url: 远程配置URL
            poll_interval: 轮询间隔（秒）
        """
        self.remote_config_url = url
        self.remote_poll_interval = poll_interval
        
        # 启动远程配置轮询
        if self.remote_poll_task:
            self.remote_poll_task.cancel()
        
        self.remote_poll_task = asyncio.create_task(self._remote_config_poller())
        
        logger.info("设置远程配置源: %s", url)
    
    async def _load_file_config(self, file_path: str, format_type: ConfigFormat):
        """加载文件配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析配置
            if format_type == ConfigFormat.JSON:
                data = json.loads(content)
            elif format_type == ConfigFormat.YAML:
                data = yaml.safe_load(content)
            elif format_type == ConfigFormat.TOML:
                import toml
                data = toml.loads(content)
            else:
                logger.error("不支持的配置格式: %s", format_type)
                return
            
            # 应用环境特定配置
            data = self._apply_environment_overrides(data)
            
            # 更新配置
            await self._update_config(data, ConfigSource.FILE, f"从文件加载: {file_path}")
            
            logger.info("成功加载配置文件: %s", file_path)
            
        except Exception as e:
            logger.error("加载配置文件失败: %s, 错误: %s", file_path, str(e))
    
    async def _load_environment_config(self):
        """加载环境变量配置"""
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # 移除前缀并转换为小写
                config_key = key[len(self.env_prefix):].lower()
                
                # 尝试解析JSON值
                try:
                    parsed_value = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    parsed_value = value
                
                # 支持嵌套键（用双下划线分隔）
                keys = config_key.split('__')
                current = env_config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = parsed_value
        
        if env_config:
            await self._update_config(env_config, ConfigSource.ENVIRONMENT, "从环境变量加载")
            logger.info("加载了 %d 个环境变量配置", len(env_config))
    
    def _apply_environment_overrides(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境特定配置覆盖"""
        if not isinstance(data, dict):
            return data
        
        # 查找环境特定配置
        env_key = f"environments.{self.environment}"
        env_config = self._get_nested_value(data, env_key)
        
        if env_config and isinstance(env_config, dict):
            # 深度合并环境配置
            data = self._deep_merge(data, env_config)
            logger.debug("应用环境配置覆盖: %s", self.environment)
        
        return data
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """获取嵌套键值"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    async def _remote_config_poller(self):
        """远程配置轮询器"""
        import aiohttp
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.remote_config_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # 尝试解析JSON
                            try:
                                data = json.loads(content)
                                await self._update_config(
                                    data, 
                                    ConfigSource.REMOTE, 
                                    f"从远程源加载: {self.remote_config_url}"
                                )
                                logger.debug("成功更新远程配置")
                            except json.JSONDecodeError as e:
                                logger.error("远程配置JSON解析失败: %s", str(e))
                        else:
                            logger.warning("远程配置请求失败，状态码: %d", response.status)
                
                await asyncio.sleep(self.remote_poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("远程配置轮询异常: %s", str(e))
                await asyncio.sleep(self.remote_poll_interval)
    
    async def _reload_file(self, file_path: str):
        """重新加载文件配置"""
        if file_path in self.watched_files:
            format_type = self.watched_files[file_path]
            await self._load_file_config(file_path, format_type)
    
    def _start_file_watcher(self):
        """启动文件监控"""
        if self.watched_files:
            self.file_handler = ConfigFileHandler(self)
            self.file_observer = Observer()
            
            # 监控所有配置文件的目录
            watched_dirs = set()
            for file_path in self.watched_files.keys():
                dir_path = os.path.dirname(file_path)
                if dir_path not in watched_dirs:
                    self.file_observer.schedule(
                        self.file_handler, 
                        dir_path, 
                        recursive=False
                    )
                    watched_dirs.add(dir_path)
            
            self.file_observer.start()
            logger.info("文件监控已启动，监控 %d 个目录", len(watched_dirs))
    
    async def _update_config(self, new_data: Dict[str, Any], source: ConfigSource, description: str = ""):
        """更新配置数据"""
        # 计算变更
        changes = self._calculate_changes(self.config_data, new_data)
        
        if not changes:
            logger.debug("配置无变更")
            return
        
        # 备份当前版本
        if self.config_data:
            current_checksum = self._calculate_checksum(self.config_data)
            current_version = ConfigVersion(
                version=f"v{len(self.config_versions) + 1}",
                timestamp=datetime.now(),
                checksum=current_checksum,
                source=source,
                data=self.config_data.copy(),
                description=description
            )
            self.config_versions.append(current_version)
            
            # 限制版本数量
            if len(self.config_versions) > self.max_versions:
                self.config_versions.pop(0)
        
        # 更新配置
        old_config = self.config_data.copy()
        self.config_data = self._deep_merge(self.config_data, new_data)
        
        # 保存到Redis（如果可用）
        if self.redis_client:
            try:
                await self.redis_client.set(
                    "xiaoke:config:current",
                    json.dumps(self.config_data),
                    ex=self.cache_ttl if self.cache_enabled else None
                )
            except Exception as e:
                logger.warning("保存配置到Redis失败: %s", str(e))
        
        # 通知变更
        await self._notify_changes(changes, old_config, self.config_data)
        
        logger.info("配置已更新，来源: %s, 变更数量: %d", source.value, len(changes))
    
    def _calculate_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> List[ConfigChange]:
        """计算配置变更"""
        changes = []
        
        def compare_dict(old_dict: Dict[str, Any], new_dict: Dict[str, Any], prefix: str = ""):
            # 检查新增和修改
            for key, new_value in new_dict.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if key not in old_dict:
                    # 新增
                    changes.append(ConfigChange(
                        key=full_key,
                        old_value=None,
                        new_value=new_value,
                        timestamp=datetime.now(),
                        source=ConfigSource.FILE  # 这里可以根据实际情况调整
                    ))
                elif old_dict[key] != new_value:
                    if isinstance(old_dict[key], dict) and isinstance(new_value, dict):
                        # 递归比较嵌套字典
                        compare_dict(old_dict[key], new_value, full_key)
                    else:
                        # 修改
                        changes.append(ConfigChange(
                            key=full_key,
                            old_value=old_dict[key],
                            new_value=new_value,
                            timestamp=datetime.now(),
                            source=ConfigSource.FILE
                        ))
            
            # 检查删除
            for key, old_value in old_dict.items():
                if key not in new_dict:
                    full_key = f"{prefix}.{key}" if prefix else key
                    changes.append(ConfigChange(
                        key=full_key,
                        old_value=old_value,
                        new_value=None,
                        timestamp=datetime.now(),
                        source=ConfigSource.FILE
                    ))
        
        compare_dict(old_data, new_data)
        return changes
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """计算配置数据校验和"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def _notify_changes(self, changes: List[ConfigChange], old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """通知配置变更"""
        # 全局变更回调
        for callback in self.change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(changes, old_config, new_config)
                else:
                    callback(changes, old_config, new_config)
            except Exception as e:
                logger.error("配置变更回调异常: %s", str(e))
        
        # 特定键变更回调
        for change in changes:
            if change.key in self.key_callbacks:
                for callback in self.key_callbacks[change.key]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(change)
                        else:
                            callback(change)
                    except Exception as e:
                        logger.error("键变更回调异常 (%s): %s", change.key, str(e))
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点分隔的嵌套键）
            default: 默认值
            
        Returns:
            配置值
        """
        return self._get_nested_value(self.config_data, key) or default
    
    async def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.REMOTE):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            source: 配置源
        """
        # 构建嵌套字典
        keys = key.split('.')
        new_data = {}
        current = new_data
        
        for k in keys[:-1]:
            current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        await self._update_config(new_data, source, f"设置配置: {key}")
    
    def add_change_callback(self, callback: Callable):
        """添加全局配置变更回调"""
        self.change_callbacks.append(callback)
    
    def add_key_callback(self, key: str, callback: Callable):
        """添加特定键变更回调"""
        if key not in self.key_callbacks:
            self.key_callbacks[key] = []
        self.key_callbacks[key].append(callback)
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()
    
    def get_versions(self) -> List[ConfigVersion]:
        """获取配置版本历史"""
        return self.config_versions.copy()
    
    async def rollback_to_version(self, version: str) -> bool:
        """
        回滚到指定版本
        
        Args:
            version: 版本号
            
        Returns:
            是否成功回滚
        """
        target_version = None
        for v in self.config_versions:
            if v.version == version:
                target_version = v
                break
        
        if not target_version:
            logger.error("未找到版本: %s", version)
            return False
        
        await self._update_config(
            target_version.data, 
            target_version.source, 
            f"回滚到版本: {version}"
        )
        
        logger.info("成功回滚到版本: %s", version)
        return True
    
    async def export_config(self, file_path: str, format_type: ConfigFormat = ConfigFormat.JSON):
        """
        导出配置到文件
        
        Args:
            file_path: 导出文件路径
            format_type: 导出格式
        """
        try:
            if format_type == ConfigFormat.JSON:
                content = json.dumps(self.config_data, indent=2, ensure_ascii=False)
            elif format_type == ConfigFormat.YAML:
                content = yaml.dump(self.config_data, default_flow_style=False, allow_unicode=True)
            elif format_type == ConfigFormat.TOML:
                import toml
                content = toml.dumps(self.config_data)
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("配置已导出到: %s", file_path)
            
        except Exception as e:
            logger.error("导出配置失败: %s", str(e))
            raise
    
    async def validate_config(self, schema: Dict[str, Any] = None) -> List[str]:
        """
        验证配置
        
        Args:
            schema: 配置模式（可选）
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 基本验证
        if not isinstance(self.config_data, dict):
            errors.append("配置数据必须是字典类型")
            return errors
        
        # 如果提供了模式，进行模式验证
        if schema:
            try:
                import jsonschema
                jsonschema.validate(self.config_data, schema)
            except ImportError:
                logger.warning("jsonschema未安装，跳过模式验证")
            except jsonschema.ValidationError as e:
                errors.append(f"配置验证失败: {e.message}")
        
        return errors
    
    async def close(self):
        """关闭配置管理器"""
        # 停止文件监控
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        # 停止远程配置轮询
        if self.remote_poll_task:
            self.remote_poll_task.cancel()
            try:
                await self.remote_poll_task
            except asyncio.CancelledError:
                pass
        
        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("动态配置管理器已关闭")

# 全局配置管理器实例
_config_manager: Optional[DynamicConfigManager] = None

async def get_config_manager(redis_url: str = None) -> DynamicConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = DynamicConfigManager(redis_url)
        await _config_manager.initialize()
    
    return _config_manager

async def close_config_manager():
    """关闭配置管理器"""
    global _config_manager
    
    if _config_manager:
        await _config_manager.close()
        _config_manager = None

# 便捷函数
async def get_config(key: str, default: Any = None) -> Any:
    """获取配置值"""
    config_manager = await get_config_manager()
    return config_manager.get(key, default)

async def set_config(key: str, value: Any):
    """设置配置值"""
    config_manager = await get_config_manager()
    await config_manager.set(key, value) 