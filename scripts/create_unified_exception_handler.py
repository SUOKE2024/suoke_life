#!/usr/bin/env python3
"""
索克生活项目 - 统一异常处理机制创建工具
建立项目级别的统一异常处理框架
"""

import os
import re
import ast
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ExceptionPattern:
    """异常处理模式"""
    file_path: str
    line_number: int
    pattern_type: str
    original_code: str
    suggested_fix: str

class UnifiedExceptionHandler:
    """统一异常处理创建器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.patterns_found = []
        self.backup_dir = self.project_root / "backups" / "exception_handling"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 项目目录
        self.project_dirs = ["src", "services", "scripts", "tests"]
        
        # 排除的目录模式
        self.exclude_patterns = [
            "*/.venv/*", "*/venv/*", "*/env/*",
            "*/node_modules/*", "*/.git/*", 
            "*/build/*", "*/dist/*", "*/__pycache__/*",
            "*/coverage/*", "*/htmlcov/*",
            "*/site-packages/*", "*/lib/python*/*"
        ]
        
        # 问题异常处理模式
        self.problematic_patterns = [
            # 过于宽泛的异常捕获
            r'except\s+Exception\s*:',
            r'except\s*:',
            # 静默忽略异常
            r'except.*:\s*pass',
            r'except.*:\s*continue',
            # 不具体的异常类型
            r'except\s+Exception\s+as\s+\w+\s*:',
        ]
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """检查文件是否应该被排除"""
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return True
        
        # 检查是否在项目目录中
        try:
            relative_path = file_path.relative_to(self.project_root)
            first_part = str(relative_path).split('/')[0]
            return first_part not in self.project_dirs
        except ValueError:
            return True
    
    def create_exception_framework(self):
        """创建统一异常处理框架"""
        
        # 1. 创建基础异常类
        base_exceptions_content = '''"""
索克生活项目 - 统一异常处理框架
定义项目级别的异常类和处理机制
"""

import logging
import traceback
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重性级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SuokeBaseException(Exception):
    """索克生活项目基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.context = context or {}
        self.timestamp = None
        
        # 自动记录异常
        self._log_exception()
    
    def _log_exception(self):
        """记录异常信息"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(self.severity, logging.ERROR)
        
        logger.log(
            log_level,
            f"[{self.error_code or 'UNKNOWN'}] {self.message}",
            extra={
                'error_code': self.error_code,
                'severity': self.severity.value,
                'context': self.context
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity.value,
            'context': self.context,
            'type': self.__class__.__name__
        }

# 业务异常类
class AgentException(SuokeBaseException):
    """智能体相关异常"""
    pass

class ServiceException(SuokeBaseException):
    """服务相关异常"""
    pass

class DataException(SuokeBaseException):
    """数据相关异常"""
    pass

class AuthenticationException(SuokeBaseException):
    """认证相关异常"""
    pass

class AuthorizationException(SuokeBaseException):
    """授权相关异常"""
    pass

class ValidationException(SuokeBaseException):
    """验证相关异常"""
    pass

class ConfigurationException(SuokeBaseException):
    """配置相关异常"""
    pass

class NetworkException(SuokeBaseException):
    """网络相关异常"""
    pass

class DatabaseException(SuokeBaseException):
    """数据库相关异常"""
    pass

class AIModelException(SuokeBaseException):
    """AI模型相关异常"""
    pass

# 异常处理装饰器
def handle_exceptions(
    default_return=None,
    log_errors=True,
    reraise=False,
    exception_mapping: Optional[Dict[type, type]] = None
):
    """
    统一异常处理装饰器
    
    Args:
        default_return: 异常时的默认返回值
        log_errors: 是否记录错误日志
        reraise: 是否重新抛出异常
        exception_mapping: 异常类型映射
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Exception in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                
                # 异常类型转换
                if exception_mapping and type(e) in exception_mapping:
                    mapped_exception = exception_mapping[type(e)]
                    raise mapped_exception(
                        f"Error in {func.__name__}: {str(e)}",
                        error_code=f"{func.__module__}.{func.__name__}",
                        context={'original_exception': str(e)}
                    )
                
                if reraise:
                    raise
                
                return default_return
        return wrapper
    return decorator

# 异常处理上下文管理器
class ExceptionContext:
    """异常处理上下文管理器"""
    
    def __init__(
        self, 
        operation_name: str,
        suppress_exceptions: bool = False,
        default_return=None
    ):
        self.operation_name = operation_name
        self.suppress_exceptions = suppress_exceptions
        self.default_return = default_return
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(
                f"Exception in {self.operation_name}: {exc_val}",
                exc_info=True
            )
            
            if self.suppress_exceptions:
                return True  # 抑制异常
        
        return False

# 全局异常处理器
class GlobalExceptionHandler:
    """全局异常处理器"""
    
    @staticmethod
    def setup_global_handler():
        """设置全局异常处理器"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
        
        sys.excepthook = handle_exception
    
    @staticmethod
    def handle_async_exception(loop, context):
        """处理异步异常"""
        exception = context.get('exception')
        if exception:
            logger.error(
                f"Async exception: {exception}",
                exc_info=exception
            )
        else:
            logger.error(f"Async error: {context['message']}")

# 异常恢复策略
class RecoveryStrategy:
    """异常恢复策略"""
    
    @staticmethod
    def retry_with_backoff(
        func, 
        max_retries: int = 3, 
        backoff_factor: float = 1.0,
        exceptions: Tuple[type, ...] = (Exception,)
    ):
        """带退避的重试策略"""
        import time
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries:
                    raise
                
                wait_time = backoff_factor * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                )
                time.sleep(wait_time)
    
    @staticmethod
    def circuit_breaker(
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        """断路器模式"""
        def decorator(func):
            func._failures = 0
            func._last_failure_time = 0
            func._state = 'closed'  # closed, open, half-open
            
            def wrapper(*args, **kwargs):
                import time
                current_time = time.time()
                
                # 检查是否可以从开路状态恢复
                if (func._state == 'open' and 
                    current_time - func._last_failure_time > recovery_timeout):
                    func._state = 'half-open'
                
                # 开路状态直接抛出异常
                if func._state == 'open':
                    raise ServiceException(
                        "Circuit breaker is open",
                        error_code="CIRCUIT_BREAKER_OPEN"
                    )
                
                try:
                    result = func(*args, **kwargs)
                    # 成功时重置计数器
                    if func._state == 'half-open':
                        func._state = 'closed'
                        func._failures = 0
                    return result
                except Exception as e:
                    func._failures += 1
                    func._last_failure_time = current_time
                    
                    if func._failures >= failure_threshold:
                        func._state = 'open'
                    
                    raise
            
            return wrapper
        return decorator
'''
        
        # 创建异常框架文件
        exceptions_dir = self.project_root / "src" / "core" / "exceptions"
        exceptions_dir.mkdir(parents=True, exist_ok=True)
        
        exceptions_file = exceptions_dir / "__init__.py"
        with open(exceptions_file, 'w', encoding='utf-8') as f:
            f.write(base_exceptions_content)
        
        logger.info(f"✅ 创建统一异常处理框架: {exceptions_file}")
        
        # 2. 创建异常处理配置
        config_content = '''"""
异常处理配置
"""

# 异常映射配置
EXCEPTION_MAPPING = {
    # 标准异常到业务异常的映射
    ValueError: "ValidationException",
    KeyError: "DataException", 
    FileNotFoundError: "ConfigurationException",
    ConnectionError: "NetworkException",
    TimeoutError: "NetworkException",
    PermissionError: "AuthorizationException",
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/exceptions.log',
            'level': 'ERROR',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'suoke_life.exceptions': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    }
}

# 重试配置
RETRY_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 1.0,
    'retryable_exceptions': [
        'NetworkException',
        'ServiceException'
    ]
}

# 断路器配置
CIRCUIT_BREAKER_CONFIG = {
    'failure_threshold': 5,
    'recovery_timeout': 60
}
'''
        
        config_file = exceptions_dir / "config.py"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        logger.info(f"✅ 创建异常处理配置: {config_file}")
        
        return exceptions_file, config_file
    
    def scan_exception_patterns(self) -> List[ExceptionPattern]:
        """扫描项目中的异常处理模式"""
        patterns = []
        
        # 扫描项目目录中的Python文件
        all_python_files = []
        for project_dir in self.project_dirs:
            dir_path = self.project_root / project_dir
            if dir_path.exists():
                all_python_files.extend(dir_path.rglob('*.py'))
        
        # 过滤文件
        filtered_files = [
            f for f in all_python_files 
            if not self.should_exclude_file(f)
        ]
        
        logger.info(f"扫描 {len(filtered_files)} 个文件中的异常处理模式...")
        
        for file_path in filtered_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    for pattern in self.problematic_patterns:
                        if re.search(pattern, line):
                            patterns.append(ExceptionPattern(
                                file_path=str(file_path),
                                line_number=line_num,
                                pattern_type=pattern,
                                original_code=line.strip(),
                                suggested_fix=self._suggest_fix(line.strip(), pattern)
                            ))
                            
            except Exception as e:
                logger.error(f"扫描文件 {file_path} 时出错: {e}")
        
        return patterns
    
    def _suggest_fix(self, original_code: str, pattern: str) -> str:
        """建议修复方案"""
        if 'except Exception:' in original_code:
            return original_code.replace(
                'except Exception:', 
                'except SpecificException:'
            ) + " # 使用具体的异常类型"
        
        elif 'except:' in original_code and 'pass' in original_code:
            return original_code.replace(
                'pass', 
                'logger.error("Unexpected error occurred", exc_info=True)'
            )
        
        elif 'except:' in original_code:
            return original_code.replace(
                'except:', 
                'except Exception as e:'
            ) + " # 至少捕获Exception并记录"
        
        return original_code + " # 需要手动检查和修复"
    
    def create_migration_script(self, patterns: List[ExceptionPattern]):
        """创建异常处理迁移脚本"""
        migration_content = f'''#!/usr/bin/env python3
"""
异常处理迁移脚本
自动修复项目中的异常处理问题
"""

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 发现的问题模式
PATTERNS_TO_FIX = {patterns}

def fix_exception_patterns():
    """修复异常处理模式"""
    fixed_count = 0
    
    for pattern in PATTERNS_TO_FIX:
        file_path = Path(pattern['file_path'])
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\\n')
            if pattern['line_number'] <= len(lines):
                original_line = lines[pattern['line_number'] - 1]
                
                # 应用建议的修复
                if pattern['suggested_fix'] != pattern['original_code']:
                    lines[pattern['line_number'] - 1] = pattern['suggested_fix']
                    
                    # 写回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\\n'.join(lines))
                    
                    logger.info(f"修复 {{file_path}}:{{pattern['line_number']}}")
                    fixed_count += 1
                    
        except Exception as e:
            logger.error(f"修复文件 {{file_path}} 时出错: {{e}}")
    
    logger.info(f"总共修复了 {{fixed_count}} 个异常处理问题")

if __name__ == "__main__":
    fix_exception_patterns()
'''
        
        # 转换模式为字典格式
        patterns_dict = [
            {
                'file_path': p.file_path,
                'line_number': p.line_number,
                'pattern_type': p.pattern_type,
                'original_code': p.original_code,
                'suggested_fix': p.suggested_fix
            }
            for p in patterns
        ]
        
        migration_script = self.project_root / "scripts" / "migrate_exception_handling.py"
        with open(migration_script, 'w', encoding='utf-8') as f:
            f.write(migration_content.format(patterns=patterns_dict))
        
        logger.info(f"✅ 创建异常处理迁移脚本: {migration_script}")
        return migration_script
    
    def generate_report(self, patterns: List[ExceptionPattern]) -> str:
        """生成异常处理分析报告"""
        pattern_counts = {}
        for pattern in patterns:
            pattern_counts[pattern.pattern_type] = pattern_counts.get(pattern.pattern_type, 0) + 1
        
        report = f"""
# 索克生活项目 - 异常处理分析报告

## 📊 统计信息
- 扫描的文件数: {len([f for d in self.project_dirs for f in (self.project_root / d).rglob('*.py') if not self.should_exclude_file(f)])}
- 发现的问题模式: {len(patterns)}
- 涉及的文件数: {len(set(p.file_path for p in patterns))}

## 🔍 问题模式分布
{chr(10).join(f"- {pattern}: {count} 次" for pattern, count in pattern_counts.items())}

## 📋 详细问题列表
{chr(10).join(f"### {i+1}. {p.file_path}:{p.line_number}" + chr(10) + f"**问题**: {p.pattern_type}" + chr(10) + f"**原代码**: `{p.original_code}`" + chr(10) + f"**建议修复**: `{p.suggested_fix}`" + chr(10) for i, p in enumerate(patterns[:20]))}

{f"... 还有 {len(patterns) - 20} 个问题" if len(patterns) > 20 else ""}

## 🚀 修复建议

### 1. 立即修复
- 使用统一异常处理框架
- 替换过于宽泛的异常捕获
- 添加适当的日志记录

### 2. 最佳实践
- 使用具体的异常类型
- 实现异常恢复策略
- 添加异常监控和告警

### 3. 使用新框架
```python
from src.core.exceptions import (
    SuokeBaseException, 
    ServiceException,
    handle_exceptions,
    ExceptionContext
)

# 使用装饰器
@handle_exceptions(reraise=True, log_errors=True)
def my_function():
    pass

# 使用上下文管理器
with ExceptionContext("database_operation"):
    # 数据库操作
    pass
```

## 📁 创建的文件
- 异常处理框架: `src/core/exceptions/__init__.py`
- 配置文件: `src/core/exceptions/config.py`
- 迁移脚本: `scripts/migrate_exception_handling.py`
"""
        return report

def main():
    """主函数"""
    project_root = os.getcwd()
    
    print("🔧 索克生活项目 - 统一异常处理机制创建工具")
    print("=" * 60)
    
    handler = UnifiedExceptionHandler(project_root)
    
    # 1. 创建异常处理框架
    print("📦 创建统一异常处理框架...")
    exceptions_file, config_file = handler.create_exception_framework()
    
    # 2. 扫描现有异常处理模式
    print("🔍 扫描现有异常处理模式...")
    patterns = handler.scan_exception_patterns()
    
    # 3. 创建迁移脚本
    if patterns:
        print("📝 创建异常处理迁移脚本...")
        migration_script = handler.create_migration_script(patterns)
    
    # 4. 生成报告
    report = handler.generate_report(patterns)
    
    # 保存报告
    report_file = Path(project_root) / "exception_handling_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("📄 异常处理框架创建完成！")
    print(f"📊 发现 {len(patterns)} 个需要改进的异常处理模式")
    print(f"📋 详细报告已保存到 exception_handling_report.md")
    print("\n🚀 下一步:")
    print("1. 查看报告了解具体问题")
    print("2. 运行迁移脚本修复问题")
    print("3. 在新代码中使用统一异常处理框架")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 