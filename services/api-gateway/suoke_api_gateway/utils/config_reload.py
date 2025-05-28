#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置热重载模块

支持配置文件和环境变量的动态更新，无需重启服务。
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ..core.config import Settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class ConfigChangeEvent:
    """配置变更事件"""
    
    def __init__(
        self,
        source: str,
        key: str,
        old_value: Any,
        new_value: Any,
        timestamp: float,
    ):
        self.source = source  # 'file' or 'env'
        self.key = key
        self.old_value = old_value
        self.new_value = new_value
        self.timestamp = timestamp


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""
    
    def __init__(self, reload_manager: 'ConfigReloadManager'):
        self.reload_manager = reload_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # 检查是否是配置文件
        if not self._is_config_file(file_path):
            return
        
        # 防止重复触发
        current_time = time.time()
        last_time = self.last_modified.get(file_path, 0)
        if current_time - last_time < 1.0:  # 1秒内的重复事件忽略
            return
        
        self.last_modified[file_path] = current_time
        
        logger.info("Config file modified", file=str(file_path))
        
        # 异步处理配置重载
        asyncio.create_task(self.reload_manager.reload_from_file(file_path))
    
    def _is_config_file(self, file_path: Path) -> bool:
        """检查是否是配置文件"""
        config_extensions = {'.yaml', '.yml', '.json', '.toml', '.env'}
        return file_path.suffix.lower() in config_extensions


class ConfigReloadManager:
    """配置重载管理器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.observers: List[Observer] = []
        self.change_handlers: List[Callable[[ConfigChangeEvent], None]] = []
        self.watched_files: Set[Path] = set()
        self.watched_dirs: Set[Path] = set()
        self.env_snapshot: Dict[str, str] = {}
        self.file_snapshots: Dict[Path, Dict[str, Any]] = {}
        self._running = False
        self._env_check_interval = 5.0  # 环境变量检查间隔（秒）
        
        # 初始化环境变量快照
        self._update_env_snapshot()
    
    def add_change_handler(self, handler: Callable[[ConfigChangeEvent], None]) -> None:
        """添加配置变更处理器"""
        self.change_handlers.append(handler)
        logger.info("Config change handler added", handler=handler.__name__)
    
    def remove_change_handler(self, handler: Callable[[ConfigChangeEvent], None]) -> None:
        """移除配置变更处理器"""
        if handler in self.change_handlers:
            self.change_handlers.remove(handler)
            logger.info("Config change handler removed", handler=handler.__name__)
    
    def watch_file(self, file_path: Path) -> None:
        """监控配置文件"""
        if not file_path.exists():
            logger.warning("Config file does not exist", file=str(file_path))
            return
        
        self.watched_files.add(file_path)
        
        # 监控文件所在目录
        directory = file_path.parent
        if directory not in self.watched_dirs:
            self.watched_dirs.add(directory)
            
            observer = Observer()
            observer.schedule(
                ConfigFileHandler(self),
                str(directory),
                recursive=False
            )
            self.observers.append(observer)
            
            if self._running:
                observer.start()
        
        # 创建文件快照
        self._create_file_snapshot(file_path)
        
        logger.info("Watching config file", file=str(file_path))
    
    def watch_directory(self, directory: Path, recursive: bool = False) -> None:
        """监控配置目录"""
        if not directory.exists():
            logger.warning("Config directory does not exist", directory=str(directory))
            return
        
        if directory not in self.watched_dirs:
            self.watched_dirs.add(directory)
            
            observer = Observer()
            observer.schedule(
                ConfigFileHandler(self),
                str(directory),
                recursive=recursive
            )
            self.observers.append(observer)
            
            if self._running:
                observer.start()
        
        logger.info("Watching config directory", directory=str(directory), recursive=recursive)
    
    async def start(self) -> None:
        """启动配置监控"""
        if self._running:
            return
        
        self._running = True
        
        # 启动文件监控
        for observer in self.observers:
            observer.start()
        
        # 启动环境变量监控
        asyncio.create_task(self._monitor_env_vars())
        
        logger.info("Config reload manager started")
    
    async def stop(self) -> None:
        """停止配置监控"""
        if not self._running:
            return
        
        self._running = False
        
        # 停止文件监控
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        logger.info("Config reload manager stopped")
    
    async def reload_from_file(self, file_path: Path) -> None:
        """从文件重载配置"""
        try:
            # 读取新配置
            new_config = self._load_config_file(file_path)
            if new_config is None:
                return
            
            # 获取旧配置快照
            old_config = self.file_snapshots.get(file_path, {})
            
            # 比较配置变更
            changes = self._compare_configs(old_config, new_config)
            
            if changes:
                # 更新快照
                self.file_snapshots[file_path] = new_config
                
                # 触发变更事件
                for key, (old_value, new_value) in changes.items():
                    event = ConfigChangeEvent(
                        source='file',
                        key=key,
                        old_value=old_value,
                        new_value=new_value,
                        timestamp=time.time(),
                    )
                    await self._handle_config_change(event)
                
                logger.info(
                    "Config reloaded from file",
                    file=str(file_path),
                    changes=len(changes)
                )
            
        except Exception as e:
            logger.error(
                "Failed to reload config from file",
                file=str(file_path),
                error=str(e)
            )
    
    async def _monitor_env_vars(self) -> None:
        """监控环境变量变更"""
        while self._running:
            try:
                await asyncio.sleep(self._env_check_interval)
                
                if not self._running:
                    break
                
                # 检查环境变量变更
                current_env = dict(os.environ)
                changes = self._compare_env_vars(self.env_snapshot, current_env)
                
                if changes:
                    # 更新快照
                    self.env_snapshot = current_env.copy()
                    
                    # 触发变更事件
                    for key, (old_value, new_value) in changes.items():
                        event = ConfigChangeEvent(
                            source='env',
                            key=key,
                            old_value=old_value,
                            new_value=new_value,
                            timestamp=time.time(),
                        )
                        await self._handle_config_change(event)
                    
                    logger.info("Environment variables changed", changes=len(changes))
                
            except Exception as e:
                logger.error("Error monitoring environment variables", error=str(e))
    
    async def _handle_config_change(self, event: ConfigChangeEvent) -> None:
        """处理配置变更事件"""
        try:
            # 调用所有变更处理器
            for handler in self.change_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(
                        "Config change handler failed",
                        handler=handler.__name__,
                        error=str(e)
                    )
            
            logger.debug(
                "Config change handled",
                source=event.source,
                key=event.key,
                old_value=event.old_value,
                new_value=event.new_value
            )
            
        except Exception as e:
            logger.error("Failed to handle config change", error=str(e))
    
    def _update_env_snapshot(self) -> None:
        """更新环境变量快照"""
        self.env_snapshot = dict(os.environ)
    
    def _create_file_snapshot(self, file_path: Path) -> None:
        """创建文件配置快照"""
        config = self._load_config_file(file_path)
        if config is not None:
            self.file_snapshots[file_path] = config
    
    def _load_config_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            suffix = file_path.suffix.lower()
            
            if suffix in ['.yaml', '.yml']:
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            
            elif suffix == '.json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif suffix == '.toml':
                import tomllib
                with open(file_path, 'rb') as f:
                    return tomllib.load(f)
            
            elif suffix == '.env':
                config = {}
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                config[key.strip()] = value.strip()
                return config
            
            else:
                logger.warning("Unsupported config file format", file=str(file_path))
                return None
                
        except Exception as e:
            logger.error("Failed to load config file", file=str(file_path), error=str(e))
            return None
    
    def _compare_configs(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any]
    ) -> Dict[str, tuple]:
        """比较配置变更"""
        changes = {}
        
        # 检查新增和修改的配置
        for key, new_value in new_config.items():
            old_value = old_config.get(key)
            if old_value != new_value:
                changes[key] = (old_value, new_value)
        
        # 检查删除的配置
        for key, old_value in old_config.items():
            if key not in new_config:
                changes[key] = (old_value, None)
        
        return changes
    
    def _compare_env_vars(
        self,
        old_env: Dict[str, str],
        new_env: Dict[str, str]
    ) -> Dict[str, tuple]:
        """比较环境变量变更"""
        changes = {}
        
        # 只检查与应用相关的环境变量
        app_prefixes = ['SUOKE_', 'GATEWAY_', 'API_']
        
        # 检查新增和修改的环境变量
        for key, new_value in new_env.items():
            if any(key.startswith(prefix) for prefix in app_prefixes):
                old_value = old_env.get(key)
                if old_value != new_value:
                    changes[key] = (old_value, new_value)
        
        # 检查删除的环境变量
        for key, old_value in old_env.items():
            if any(key.startswith(prefix) for prefix in app_prefixes):
                if key not in new_env:
                    changes[key] = (old_value, None)
        
        return changes


# 默认配置变更处理器
async def default_config_change_handler(event: ConfigChangeEvent) -> None:
    """默认配置变更处理器"""
    logger.info(
        "Configuration changed",
        source=event.source,
        key=event.key,
        old_value=event.old_value,
        new_value=event.new_value,
    )
    
    # 这里可以添加具体的配置更新逻辑
    # 例如：更新缓存配置、重新初始化连接池等


def create_config_reload_manager(settings: Settings) -> ConfigReloadManager:
    """创建配置重载管理器"""
    manager = ConfigReloadManager(settings)
    
    # 添加默认处理器
    manager.add_change_handler(default_config_change_handler)
    
    # 监控常见配置文件
    config_files = [
        Path('config.yaml'),
        Path('config.yml'),
        Path('config.json'),
        Path('.env'),
        Path('config/.env'),
    ]
    
    for config_file in config_files:
        if config_file.exists():
            manager.watch_file(config_file)
    
    # 监控配置目录
    config_dir = Path('config')
    if config_dir.exists():
        manager.watch_directory(config_dir)
    
    return manager 