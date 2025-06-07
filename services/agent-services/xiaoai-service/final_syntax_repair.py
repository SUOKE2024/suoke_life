#!/usr/bin/env python3
"""
最终语法修复脚本 - 索克生活项目
批量修复所有严重的语法错误
"""

import re
from pathlib import Path


def fix_config_manager():
    """修复config_manager.py"""
    file_path = Path("xiaoai/utils/config_manager.py")
    if not file_path.exists():
        return
        
    content = """#!/usr/bin/env python3
\"\"\"
配置管理模块 - 提供配置文件加载和监控功能
\"\"\"

import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigManager:
    \"\"\"配置管理器\"\"\"

    def __init__(self, config_dir: str = "config", watch_interval: float = 1.0):
        self.config_dir = Path(config_dir)
        self.watch_interval = watch_interval
        self.config_data: Dict[str, Any] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.watch_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def load_config(self, config_name: str) -> Dict[str, Any]:
        \"\"\"加载配置文件\"\"\"
        config_file = self.config_dir / f"{config_name}.yaml"
        
        if not config_file.exists():
            return {}
            
        return self._load_yaml_config(str(config_file))

    def _load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        \"\"\"加载YAML配置文件\"\"\"
        if not YAML_AVAILABLE:
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                
            with self._lock:
                self.config_data[file_path] = config
                self.file_timestamps[file_path] = Path(file_path).stat().st_mtime
                
            return config
        except Exception as e:
            print(f"Error loading config {file_path}: {e}")
            return {}

    def get_config(self, key: str, default: Any = None) -> Any:
        \"\"\"获取配置值\"\"\"
        with self._lock:
            for config in self.config_data.values():
                if key in config:
                    return config[key]
        return default

    def start_watching(self):
        \"\"\"开始监控配置文件变化\"\"\"
        if self.watch_thread is None or not self.watch_thread.is_alive():
            self.watch_thread = threading.Thread(target=self._watch_files, daemon=True)
            self.watch_thread.start()

    def _watch_files(self):
        \"\"\"监控文件变化\"\"\"
        while True:
            try:
                for file_path, last_mtime in self.file_timestamps.items():
                    if Path(file_path).exists():
                        current_mtime = Path(file_path).stat().st_mtime
                        if current_mtime > last_mtime:
                            print(f"Config file {file_path} changed, reloading...")
                            self._load_yaml_config(file_path)

                time.sleep(self.watch_interval)

            except Exception as e:
                print(f"Error watching config files: {e}")
                time.sleep(self.watch_interval)


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None
_config_lock = threading.Lock()


def get_config_manager() -> ConfigManager:
    \"\"\"获取配置管理器实例\"\"\"
    global _config_manager
    if _config_manager is None:
        with _config_lock:
            if _config_manager is None:
                _config_manager = ConfigManager()
    return _config_manager


def load_config(config_name: str) -> Dict[str, Any]:
    \"\"\"加载配置的便捷函数\"\"\"
    return get_config_manager().load_config(config_name)


def get_config(key: str, default: Any = None) -> Any:
    \"\"\"获取配置值的便捷函数\"\"\"
    return get_config_manager().get_config(key, default)
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"修复文件: {file_path}")


def fix_exceptions():
    """修复exceptions.py"""
    file_path = Path("xiaoai/utils/exceptions.py")
    if not file_path.exists():
        return
        
    content = """#!/usr/bin/env python3
\"\"\"
异常模块 - 定义服务相关的异常类
\"\"\"

from typing import Any, Dict, Optional


class BaseServiceError(Exception):
    \"\"\"
    基础服务错误类
    \"\"\"

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        \"\"\"
        初始化服务错误
        
        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详情
        \"\"\"
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class InvalidInputError(BaseServiceError):
    \"\"\"
    无效输入错误
    
    当用户输入不符合要求时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "INVALID_INPUT", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class AuthenticationError(BaseServiceError):
    \"\"\"
    认证错误
    
    当用户认证失败时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "AUTH_FAILED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class AuthorizationError(BaseServiceError):
    \"\"\"
    授权错误
    
    当用户权限不足时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "AUTH_DENIED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ResourceNotFoundError(BaseServiceError):
    \"\"\"
    资源未找到错误
    
    当请求的资源不存在时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "NOT_FOUND", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ResourceExistsError(BaseServiceError):
    \"\"\"
    资源已存在错误
    
    当尝试创建已存在的资源时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "ALREADY_EXISTS", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ProcessingError(BaseServiceError):
    \"\"\"
    处理错误
    
    当业务逻辑处理失败时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "PROCESSING_FAILED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class DatabaseError(BaseServiceError):
    \"\"\"
    数据库错误
    
    当数据库操作失败时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "DB_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ModelError(BaseServiceError):
    \"\"\"
    模型错误
    
    当AI模型操作失败时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "MODEL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ServiceUnavailableError(BaseServiceError):
    \"\"\"
    服务不可用错误
    
    当服务暂时不可用时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class TimeoutError(BaseServiceError):
    \"\"\"
    超时错误
    
    当操作超时时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "TIMEOUT", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ValidationError(InvalidInputError):
    \"\"\"
    验证错误
    
    当数据验证失败时抛出
    \"\"\"

    def __init__(self, message: str, code: str = "VALIDATION_FAILED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class ExternalServiceError(BaseServiceError):
    \"\"\"
    外部服务错误
    
    当调用外部服务失败时抛出
    \"\"\"

    def __init__(
        self,
        message: str,
        service_name: str,
        code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)
        self.service_name = service_name
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"修复文件: {file_path}")


def fix_metrics_imports():
    """修复metrics.py的导入问题"""
    file_path = Path("xiaoai/utils/metrics.py")
    if not file_path.exists():
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移动导入到文件顶部
    lines = content.split('\n')
    new_lines = []
    imports = []
    in_docstring = False
    docstring_count = 0
    
    for line in lines:
        if '"""' in line:
            docstring_count += 1
            if docstring_count == 2:
                in_docstring = False
            elif docstring_count == 1:
                in_docstring = True
        
        if not in_docstring and docstring_count >= 2:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line)
                continue
        
        new_lines.append(line)
    
    # 重新组织文件
    final_lines = []
    added_imports = False
    
    for line in new_lines:
        if '"""' in line and not added_imports:
            final_lines.append(line)
            if line.count('"""') == 2 or (line.count('"""') == 1 and docstring_count >= 2):
                final_lines.append('')
                final_lines.extend(imports)
                final_lines.append('')
                added_imports = True
        else:
            if not (line.strip().startswith('import ') or line.strip().startswith('from ')):
                final_lines.append(line)
    
    content = '\n'.join(final_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"修复文件导入: {file_path}")


def main():
    """主函数"""
    print("开始最终语法修复...")
    
    # 修复关键文件
    fix_config_manager()
    fix_exceptions()
    fix_metrics_imports()
    
    print("最终语法修复完成！")


if __name__ == "__main__":
    main() 