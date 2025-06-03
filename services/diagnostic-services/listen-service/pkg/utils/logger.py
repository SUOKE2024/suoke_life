"""
优化的日志工具模块
支持结构化日志、性能监控、中医特色日志记录
"""
import sys
import json
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import traceback

class TCMLogFormatter(logging.Formatter):
    """中医特色日志格式化器"""
    
    def __init__(self, include_tcm_context: bool = True):
        super().__init__()
        self.include_tcm_context = include_tcm_context
        
    def format(self, record):
        # 基本日志信息
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 添加中医相关上下文
        if self.include_tcm_context and hasattr(record, 'tcm_context'):
            log_data["tcm_context"] = record.tcm_context
            
        # 添加性能指标
        if hasattr(record, 'performance'):
            log_data["performance"] = record.performance
            
        # 添加用户上下文
        if hasattr(record, 'user_context'):
            log_data["user_context"] = record.user_context
            
        # 添加音频处理上下文
        if hasattr(record, 'audio_context'):
            log_data["audio_context"] = record.audio_context
            
        return json.dumps(log_data, ensure_ascii=False, indent=None)

class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_processing_time(self, operation: str, duration: float, 
                          audio_info: Optional[Dict] = None,
                          tcm_features: Optional[Dict] = None):
        """记录处理时间"""
        performance_data = {
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": time.time()
        }
        
        if audio_info:
            performance_data["audio_info"] = audio_info
            
        if tcm_features:
            performance_data["tcm_features"] = tcm_features
            
        # 创建日志记录
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0,
            f"Performance: {operation} completed in {duration:.3f}s",
            (), None
        )
        record.performance = performance_data
        self.logger.handle(record)
        
    def log_memory_usage(self, operation: str, memory_mb: float):
        """记录内存使用"""
        performance_data = {
            "operation": operation,
            "memory_mb": memory_mb,
            "timestamp": time.time()
        }
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0,
            f"Memory: {operation} used {memory_mb:.2f}MB",
            (), None
        )
        record.performance = performance_data
        self.logger.handle(record)

class TCMLogger:
    """中医特色日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_diagnosis(self, user_id: str, audio_features: Dict, 
                     tcm_analysis: Dict, diagnosis_result: Dict):
        """记录中医诊断过程"""
        tcm_context = {
            "user_id": user_id,
            "diagnosis_type": "listen_diagnosis",
            "audio_features": {
                "qi_stability": audio_features.get("qi_stability"),
                "voice_clarity": audio_features.get("voice_clarity"),
                "voice_thickness": audio_features.get("voice_thickness"),
                "voice_strength": audio_features.get("voice_strength"),
                "rhythm_regularity": audio_features.get("rhythm_regularity")
            },
            "tcm_analysis": tcm_analysis,
            "diagnosis_result": diagnosis_result,
            "timestamp": time.time()
        }
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0,
            f"TCM Diagnosis completed for user {user_id}",
            (), None
        )
        record.tcm_context = tcm_context
        self.logger.handle(record)
        
    def log_constitution_analysis(self, user_id: str, constitution_type: str, 
                                confidence: float, features: Dict):
        """记录体质分析"""
        tcm_context = {
            "user_id": user_id,
            "analysis_type": "constitution_analysis",
            "constitution_type": constitution_type,
            "confidence": confidence,
            "features": features,
            "timestamp": time.time()
        }
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0,
            f"Constitution analysis: {constitution_type} (confidence: {confidence:.2f})",
            (), None
        )
        record.tcm_context = tcm_context
        self.logger.handle(record)
        
    def log_emotion_analysis(self, user_id: str, emotion: str, 
                           tcm_emotion: str, confidence: float):
        """记录情绪分析（五志）"""
        tcm_context = {
            "user_id": user_id,
            "analysis_type": "emotion_analysis",
            "detected_emotion": emotion,
            "tcm_emotion": tcm_emotion,  # 喜、怒、忧、思、恐
            "confidence": confidence,
            "timestamp": time.time()
        }
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0,
            f"Emotion analysis: {emotion} -> {tcm_emotion} (confidence: {confidence:.2f})",
            (), None
        )
        record.tcm_context = tcm_context
        self.logger.handle(record)

def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    设置优化的日志系统
    
    Args:
        config: 配置字典
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    # 获取日志配置
    log_config = config.get("monitoring", {}).get("logging", {})
    
    # 基本配置
    log_level = getattr(logging, log_config.get("level", "INFO").upper())
    log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file = log_config.get("file", "listen_service.log")
    max_size = log_config.get("max_size", "100MB")
    backup_count = log_config.get("backup_count", 5)
    
    # 解析文件大小
    if isinstance(max_size, str):
        if max_size.endswith("MB"):
            max_bytes = int(max_size[:-2]) * 1024 * 1024
        elif max_size.endswith("GB"):
            max_bytes = int(max_size[:-2]) * 1024 * 1024 * 1024
        else:
            max_bytes = int(max_size)
    else:
        max_bytes = max_size
    
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # 判断是否使用结构化日志
    use_structured_logging = config.get("development", {}).get("structured_logging", True)
    
    if use_structured_logging:
        # 使用中医特色格式化器
        console_formatter = TCMLogFormatter(include_tcm_context=True)
        file_formatter = TCMLogFormatter(include_tcm_context=True)
    else:
        # 使用标准格式化器
        console_formatter = logging.Formatter(log_format)
        file_formatter = logging.Formatter(log_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（轮转）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # 错误日志单独处理器
    error_log_file = log_config.get("error_file", "listen_service_error.log")
    if error_log_file:
        error_path = Path(error_log_file)
        error_path.parent.mkdir(parents=True, exist_ok=True)
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
    
    # 性能日志处理器
    perf_log_file = log_config.get("performance_file", "listen_service_performance.log")
    if perf_log_file:
        perf_path = Path(perf_log_file)
        perf_path.parent.mkdir(parents=True, exist_ok=True)
        
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(file_formatter)
        
        # 创建性能日志器
        perf_logger = logging.getLogger("performance")
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        perf_logger.propagate = False
    
    # 中医日志处理器
    tcm_log_file = log_config.get("tcm_file", "listen_service_tcm.log")
    if tcm_log_file:
        tcm_path = Path(tcm_log_file)
        tcm_path.parent.mkdir(parents=True, exist_ok=True)
        
        tcm_handler = logging.handlers.RotatingFileHandler(
            tcm_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        tcm_handler.setLevel(logging.INFO)
        tcm_handler.setFormatter(file_formatter)
        
        # 创建中医日志器
        tcm_logger = logging.getLogger("tcm")
        tcm_logger.addHandler(tcm_handler)
        tcm_logger.setLevel(logging.INFO)
        tcm_logger.propagate = False
    
    # 设置第三方库日志级别
    logging.getLogger("librosa").setLevel(logging.WARNING)
    logging.getLogger("numba").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("grpc").setLevel(logging.INFO)
    
    logger = logging.getLogger("listen_service")
    logger.info("日志系统初始化完成")
    
    return logger

def get_performance_logger() -> PerformanceLogger:
    """获取性能日志记录器"""
    logger = logging.getLogger("performance")
    return PerformanceLogger(logger)

def get_tcm_logger() -> TCMLogger:
    """获取中医日志记录器"""
    logger = logging.getLogger("tcm")
    return TCMLogger(logger)

class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.original_factory = logging.getLogRecordFactory()
        
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.original_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.original_factory)

def with_audio_context(logger: logging.Logger, audio_info: Dict):
    """音频处理上下文"""
    return LogContext(logger, audio_context=audio_info)

def with_user_context(logger: logging.Logger, user_id: str, session_id: str = None):
    """用户上下文"""
    context = {"user_id": user_id}
    if session_id:
        context["session_id"] = session_id
    return LogContext(logger, user_context=context)

def with_tcm_context(logger: logging.Logger, tcm_data: Dict):
    """中医上下文"""
    return LogContext(logger, tcm_context=tcm_data) 