"""
日志配置模块
提供结构化日志和统一的日志管理
"""
import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import structlog
from pythonjsonlogger import jsonlogger

def configure_logging(
    level: str = "INFO",
    structured: bool = True,
    file_path: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    配置应用日志
    
    Args:
        level: 日志级别
        structured: 是否使用结构化日志
        file_path: 日志文件路径
        max_file_size: 日志文件最大大小
        backup_count: 日志文件备份数量
    """
    # 确保日志目录存在
    if file_path:
        log_dir = Path(file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # 基础配置
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "handlers": {},
        "loggers": {},
        "root": {
            "level": level,
            "handlers": []
        }
    }
    
    if structured:
        # 结构化日志格式
        config["formatters"]["structured"] = {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": [
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.ExtraAdder(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
            ],
        }
        
        config["formatters"]["json"] = {
            "()": jsonlogger.JsonFormatter,
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
        }
    else:
        # 传统日志格式
        config["formatters"]["standard"] = {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    
    # 控制台处理器
    config["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "level": level,
        "formatter": "structured" if structured else "standard",
        "stream": sys.stdout
    }
    config["root"]["handlers"].append("console")
    
    # 文件处理器
    if file_path:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "json" if structured else "standard",
            "filename": file_path,
            "maxBytes": max_file_size,
            "backupCount": backup_count,
            "encoding": "utf-8"
        }
        config["root"]["handlers"].append("file")
    
    # 错误文件处理器
    if file_path:
        error_file_path = str(Path(file_path).with_suffix('.error.log'))
        config["handlers"]["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json" if structured else "standard",
            "filename": error_file_path,
            "maxBytes": max_file_size,
            "backupCount": backup_count,
            "encoding": "utf-8"
        }
        config["root"]["handlers"].append("error_file")
    
    # 特定库的日志级别
    config["loggers"].update({
        "uvicorn": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO"},
        "fastapi": {"level": "INFO"},
        "sqlalchemy": {"level": "WARNING"},
        "sqlalchemy.engine": {"level": "WARNING"},
        "aiosqlite": {"level": "WARNING"},
        "asyncpg": {"level": "WARNING"},
        "grpc": {"level": "INFO"},
        "prometheus_client": {"level": "WARNING"},
    })
    
    # 应用配置
    logging.config.dictConfig(config)
    
    # 配置structlog
    if structured:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self, logger_name: str = "user_service.requests"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ):
        """记录请求日志"""
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if request_id:
            log_data["request_id"] = request_id
        if user_id:
            log_data["user_id"] = user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        if user_agent:
            log_data["user_agent"] = user_agent
        
        # 添加额外的上下文信息
        log_data.update(kwargs)
        
        # 根据状态码选择日志级别
        if status_code >= 500:
            self.logger.error("HTTP请求处理", **log_data)
        elif status_code >= 400:
            self.logger.warning("HTTP请求处理", **log_data)
        else:
            self.logger.info("HTTP请求处理", **log_data)

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, logger_name: str = "user_service.audit"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_user_action(
        self,
        action: str,
        user_id: str,
        target_user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """记录用户操作审计日志"""
        log_data = {
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if target_user_id:
            log_data["target_user_id"] = target_user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        if user_agent:
            log_data["user_agent"] = user_agent
        if changes:
            log_data["changes"] = changes
        if metadata:
            log_data["metadata"] = metadata
        
        log_data.update(kwargs)
        
        self.logger.info("用户操作审计", **log_data)
    
    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ):
        """记录安全事件日志"""
        log_data = {
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if user_id:
            log_data["user_id"] = user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        
        log_data.update(kwargs)
        
        # 根据严重程度选择日志级别
        if severity.lower() in ["critical", "high"]:
            self.logger.error("安全事件", **log_data)
        elif severity.lower() == "medium":
            self.logger.warning("安全事件", **log_data)
        else:
            self.logger.info("安全事件", **log_data)

class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger_name: str = "user_service.performance"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_slow_query(
        self,
        query: str,
        duration: float,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """记录慢查询日志"""
        log_data = {
            "query": query,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if parameters:
            log_data["parameters"] = parameters
        
        log_data.update(kwargs)
        
        self.logger.warning("慢查询检测", **log_data)
    
    async def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """记录性能指标日志"""
        log_data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if tags:
            log_data["tags"] = tags
        
        log_data.update(kwargs)
        
        self.logger.info("性能指标", **log_data)

def get_logger(name: str) -> structlog.BoundLogger:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)

def setup_logging_from_config(config: Dict[str, Any]) -> None:
    """从配置字典设置日志"""
    logging_config = config.get("logging", {})
    
    configure_logging(
        level=logging_config.get("level", "INFO"),
        structured=logging_config.get("structured", True),
        file_path=logging_config.get("file_path"),
        max_file_size=logging_config.get("max_file_size", 10 * 1024 * 1024),
        backup_count=logging_config.get("backup_count", 5)
    ) 