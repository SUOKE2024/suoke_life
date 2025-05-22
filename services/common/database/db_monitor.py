"""
数据库健康检查和监控模块

提供数据库健康检查、慢查询监控、连接池监控、数据库统计信息收集等功能。
包含：
1. 定时健康检查
2. 慢查询日志和告警
3. 连接池使用情况监控
4. 数据库性能指标收集
5. 健康状态通知
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union

from opentelemetry import metrics, trace
from opentelemetry.metrics import Counter, Histogram
from prometheus_client import Counter as PrometheusCounter
from prometheus_client import Gauge, Histogram as PrometheusHistogram
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# OpenTelemetry指标
DB_QUERY_DURATION = meter.create_histogram(
    name="db_query_duration",
    description="数据库查询持续时间（毫秒）",
    unit="ms",
)

DB_CONNECTION_COUNT = meter.create_up_down_counter(
    name="db_connection_count", 
    description="数据库连接数",
)

DB_SLOW_QUERY_COUNT = meter.create_counter(
    name="db_slow_query_count",
    description="慢查询计数",
)

DB_ERROR_COUNT = meter.create_counter(
    name="db_error_count",
    description="数据库错误计数",
)

# Prometheus指标（用于导出到Prometheus）
PROM_DB_QUERY_DURATION = PrometheusHistogram(
    "db_query_duration_milliseconds",
    "数据库查询持续时间（毫秒）",
    ["database", "operation", "service"],
    buckets=[5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000],
)

PROM_DB_CONNECTION_GAUGE = Gauge(
    "db_active_connections",
    "活跃数据库连接数",
    ["database", "pool_type", "service"],
)

PROM_DB_SLOW_QUERY_COUNTER = PrometheusCounter(
    "db_slow_query_total",
    "慢查询总数",
    ["database", "service"],
)

PROM_DB_ERROR_COUNTER = PrometheusCounter(
    "db_error_total",
    "数据库错误总数",
    ["database", "error_type", "service"],
)

class DatabaseMonitor:
    """数据库监控器，负责收集和报告数据库性能和健康指标"""
    
    def __init__(
        self, 
        service_name: str, 
        config: Dict[str, Any],
        prometheus_port: Optional[int] = None,
    ):
        """
        初始化数据库监控器
        
        Args:
            service_name: 服务名称
            config: 数据库监控配置
            prometheus_port: Prometheus导出器HTTP端口
        """
        self.service_name = service_name
        self.config = config
        self.slow_query_threshold = config.get("slow_query_threshold", 500)  # 毫秒
        self.query_timeout_threshold = config.get("query_timeout_threshold", 10000)  # 毫秒
        self.check_interval = config.get("check_interval", 60)  # 秒
        self.max_slow_queries = config.get("max_slow_queries", 1000)
        self.alert_enabled = config.get("alert_enabled", True)
        self.alert_channels = config.get("alert_channels", ["log"])
        
        # 收集的慢查询
        self.slow_queries: List[Dict[str, Any]] = []
        
        # 收集的数据库错误
        self.db_errors: List[Dict[str, Any]] = []
        
        # 健康检查任务
        self.health_check_task = None
        
        # 最近一次健康检查结果
        self.last_health_check: Dict[str, Any] = {
            "status": "UNKNOWN",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        # 启动Prometheus导出器
        if prometheus_port:
            try:
                start_http_server(prometheus_port)
                logger.info(f"Started Prometheus metrics server on port {prometheus_port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {str(e)}")
    
    async def start_monitoring(self, db_engine: Any):
        """
        启动数据库监控
        
        Args:
            db_engine: 数据库引擎实例
        """
        self.db_engine = db_engine
        
        # 启动健康检查任务
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"Started database monitoring for service {self.service_name}")
    
    async def stop_monitoring(self):
        """停止数据库监控"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            
        logger.info(f"Stopped database monitoring for service {self.service_name}")
    
    async def _health_check_loop(self):
        """周期性健康检查循环"""
        while True:
            try:
                health_result = await self.db_engine.check_health()
                
                # 更新健康检查结果
                self.last_health_check = {
                    "status": health_result.get("status", "UNKNOWN"),
                    "timestamp": datetime.now().isoformat(),
                    "details": health_result.get("details", {})
                }
                
                # 检查是否需要报警
                if health_result.get("status") == "DOWN" and self.alert_enabled:
                    self._send_alert(
                        "数据库健康检查失败",
                        f"服务 {self.service_name} 数据库健康检查失败: {json.dumps(health_result)}",
                        "critical"
                    )
                
                # 导出健康状态指标
                PROM_DB_CONNECTION_GAUGE.labels(
                    database="primary",
                    pool_type="write",
                    service=self.service_name
                ).set(
                    1 if health_result.get("details", {}).get("primary", {}).get("status") == "UP" else 0
                )
                
                # 导出副本状态指标
                for i, replica in enumerate(health_result.get("details", {}).get("replicas", [])):
                    PROM_DB_CONNECTION_GAUGE.labels(
                        database=f"replica_{i}",
                        pool_type="read",
                        service=self.service_name
                    ).set(
                        1 if replica.get("status") == "UP" else 0
                    )
                
                # 记录连接池状态
                if hasattr(self.db_engine, "connection_counts"):
                    for engine_name, count in self.db_engine.connection_counts.items():
                        pool_type = "write" if engine_name == "primary" else "read"
                        PROM_DB_CONNECTION_GAUGE.labels(
                            database=engine_name,
                            pool_type=pool_type,
                            service=self.service_name
                        ).set(count)
                
                logger.debug(f"Database health check completed: {health_result.get('status')}")
            except Exception as e:
                logger.error(f"健康检查失败: {str(e)}")
                
                self.last_health_check = {
                    "status": "ERROR",
                    "timestamp": datetime.now().isoscape(),
                    "error": str(e)
                }
                
                # 记录错误
                self._record_db_error("health_check", str(e))
                
                # 发送告警
                if self.alert_enabled:
                    self._send_alert(
                        "数据库健康检查错误",
                        f"服务 {self.service_name} 数据库健康检查错误: {str(e)}",
                        "error"
                    )
            
            # 等待下一次检查
            await asyncio.sleep(self.check_interval)
    
    def track_query(self, operation: str, query: str, params: Optional[Dict[str, Any]] = None, database: str = "primary"):
        """
        创建追踪查询的装饰器
        
        Args:
            operation: 操作类型（select, insert, update, delete等）
            query: SQL查询
            params: 查询参数
            database: 数据库名称
            
        Returns:
            装饰器函数
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 开始时间
                start_time = time.time()
                
                # 创建追踪
                with tracer.start_as_current_span(f"db_{operation}") as span:
                    span.set_attribute("db.system", database)
                    span.set_attribute("db.operation", operation)
                    span.set_attribute("db.statement", query)
                    
                    if params:
                        span.set_attribute("db.params", str(params))
                    
                    try:
                        # 执行数据库操作
                        result = await func(*args, **kwargs)
                        
                        # 计算持续时间
                        duration_ms = (time.time() - start_time) * 1000
                        
                        # 记录查询持续时间
                        span.set_attribute("db.duration_ms", duration_ms)
                        
                        # 导出查询持续时间指标
                        DB_QUERY_DURATION.record(duration_ms)
                        PROM_DB_QUERY_DURATION.labels(
                            database=database,
                            operation=operation,
                            service=self.service_name
                        ).observe(duration_ms)
                        
                        # 检查是否为慢查询
                        if duration_ms > self.slow_query_threshold:
                            self._record_slow_query(operation, query, params, duration_ms, database)
                        
                        # 检查是否超时
                        if duration_ms > self.query_timeout_threshold:
                            self._send_alert(
                                "数据库查询超时",
                                f"服务 {self.service_name} 数据库查询超时 ({duration_ms:.2f}ms): {query}",
                                "warning"
                            )
                        
                        return result
                    except Exception as e:
                        # 记录错误
                        span.set_attribute("error", True)
                        span.set_attribute("error.message", str(e))
                        
                        # 记录数据库错误
                        error_type = type(e).__name__
                        self._record_db_error(error_type, str(e), query, params, database)
                        
                        # 报警
                        if self.alert_enabled:
                            self._send_alert(
                                "数据库查询错误",
                                f"服务 {self.service_name} 数据库查询错误 ({error_type}): {str(e)}\nQuery: {query}",
                                "error"
                            )
                        
                        raise
            
            return wrapper
        
        return decorator
    
    def _record_slow_query(
        self, 
        operation: str, 
        query: str, 
        params: Optional[Dict[str, Any]],
        duration_ms: float,
        database: str = "primary"
    ):
        """
        记录慢查询
        
        Args:
            operation: 操作类型
            query: SQL查询
            params: 查询参数
            duration_ms: 查询持续时间（毫秒）
            database: 数据库名称
        """
        slow_query = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "query": query,
            "params": params,
            "duration_ms": duration_ms,
            "database": database
        }
        
        # 添加到慢查询列表
        self.slow_queries.append(slow_query)
        
        # 限制慢查询列表大小
        if len(self.slow_queries) > self.max_slow_queries:
            self.slow_queries = self.slow_queries[-self.max_slow_queries:]
        
        # 更新慢查询计数
        DB_SLOW_QUERY_COUNT.add(1)
        PROM_DB_SLOW_QUERY_COUNTER.labels(
            database=database,
            service=self.service_name
        ).inc()
        
        # 记录慢查询日志
        logger.warning(
            f"慢查询 ({duration_ms:.2f}ms): {query}, "
            f"参数: {params}, 数据库: {database}, 操作: {operation}"
        )
        
        # 如果超过警告阈值，发送告警
        if duration_ms > self.slow_query_threshold * 5:  # 5倍于慢查询阈值
            self._send_alert(
                "严重的慢查询",
                f"服务 {self.service_name} 检测到严重的慢查询 ({duration_ms:.2f}ms): {query}",
                "warning"
            )
    
    def _record_db_error(
        self, 
        error_type: str, 
        error_message: str,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        database: str = "primary"
    ):
        """
        记录数据库错误
        
        Args:
            error_type: 错误类型
            error_message: 错误消息
            query: SQL查询
            params: 查询参数
            database: 数据库名称
        """
        db_error = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "query": query,
            "params": params,
            "database": database
        }
        
        # 添加到错误列表
        self.db_errors.append(db_error)
        
        # 限制错误列表大小
        max_errors = self.config.get("max_errors", 1000)
        if len(self.db_errors) > max_errors:
            self.db_errors = self.db_errors[-max_errors:]
        
        # 更新错误计数
        DB_ERROR_COUNT.add(1)
        PROM_DB_ERROR_COUNTER.labels(
            database=database,
            error_type=error_type,
            service=self.service_name
        ).inc()
        
        # 记录错误日志
        logger.error(
            f"数据库错误 ({error_type}): {error_message}, "
            f"查询: {query}, 参数: {params}, 数据库: {database}"
        )
    
    def _send_alert(self, title: str, message: str, level: str = "error"):
        """
        发送告警
        
        Args:
            title: 告警标题
            message: 告警消息
            level: 告警级别 (info, warning, error, critical)
        """
        # 记录告警日志
        log_method = getattr(logger, level, logger.error)
        log_method(f"数据库告警: {title} - {message}")
        
        # 根据配置的告警渠道发送告警
        for channel in self.alert_channels:
            if channel == "log":
                # 已经记录到日志
                pass
            elif channel == "email" and "email" in self.config:
                self._send_email_alert(title, message, level)
            elif channel == "webhook" and "webhook" in self.config:
                self._send_webhook_alert(title, message, level)
            elif channel == "slack" and "slack" in self.config:
                self._send_slack_alert(title, message, level)
    
    def _send_email_alert(self, title: str, message: str, level: str):
        """发送电子邮件告警"""
        # 在实际实现中，这里应该调用电子邮件发送库
        email_config = self.config.get("email", {})
        recipients = email_config.get("recipients", [])
        
        logger.info(f"发送电子邮件告警到 {recipients}: {title}")
    
    def _send_webhook_alert(self, title: str, message: str, level: str):
        """发送Webhook告警"""
        # 在实际实现中，这里应该调用HTTP库发送webhook请求
        webhook_config = self.config.get("webhook", {})
        url = webhook_config.get("url", "")
        
        logger.info(f"发送Webhook告警到 {url}: {title}")
    
    def _send_slack_alert(self, title: str, message: str, level: str):
        """发送Slack告警"""
        # 在实际实现中，这里应该调用Slack API库
        slack_config = self.config.get("slack", {})
        channel = slack_config.get("channel", "")
        
        logger.info(f"发送Slack告警到 {channel}: {title}")
    
    def get_slow_queries(self, limit: int = 100, skip: int = 0, 
                        start_time: Optional[datetime] = None, 
                        end_time: Optional[datetime] = None,
                        min_duration: Optional[float] = None,
                        database: Optional[str] = None,
                        operation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取慢查询列表
        
        Args:
            limit: 返回的最大结果数
            skip: 跳过的结果数
            start_time: 开始时间
            end_time: 结束时间
            min_duration: 最小持续时间（毫秒）
            database: 数据库名称过滤
            operation: 操作类型过滤
            
        Returns:
            过滤后的慢查询列表
        """
        result = self.slow_queries
        
        # 应用时间过滤
        if start_time or end_time:
            filtered = []
            for query in result:
                query_time = datetime.fromisoformat(query["timestamp"])
                if start_time and query_time < start_time:
                    continue
                if end_time and query_time > end_time:
                    continue
                filtered.append(query)
            result = filtered
        
        # 应用持续时间过滤
        if min_duration is not None:
            result = [q for q in result if q["duration_ms"] >= min_duration]
        
        # 应用数据库过滤
        if database:
            result = [q for q in result if q["database"] == database]
        
        # 应用操作类型过滤
        if operation:
            result = [q for q in result if q["operation"] == operation]
        
        # 应用分页
        result = result[skip:skip+limit]
        
        return result
    
    def get_db_errors(self, limit: int = 100, skip: int = 0,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     error_type: Optional[str] = None,
                     database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取数据库错误列表
        
        Args:
            limit: 返回的最大结果数
            skip: 跳过的结果数
            start_time: 开始时间
            end_time: 结束时间
            error_type: 错误类型过滤
            database: 数据库名称过滤
            
        Returns:
            过滤后的错误列表
        """
        result = self.db_errors
        
        # 应用时间过滤
        if start_time or end_time:
            filtered = []
            for error in result:
                error_time = datetime.fromisoformat(error["timestamp"])
                if start_time and error_time < start_time:
                    continue
                if end_time and error_time > end_time:
                    continue
                filtered.append(error)
            result = filtered
        
        # 应用错误类型过滤
        if error_type:
            result = [e for e in result if e["error_type"] == error_type]
        
        # 应用数据库过滤
        if database:
            result = [e for e in result if e["database"] == database]
        
        # 应用分页
        result = result[skip:skip+limit]
        
        return result
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        获取数据库健康状态
        
        Returns:
            健康状态信息
        """
        # 添加慢查询摘要
        slow_query_summary = {
            "count": len(self.slow_queries),
            "last_24h": len([
                q for q in self.slow_queries 
                if datetime.fromisoformat(q["timestamp"]) > datetime.now() - timedelta(days=1)
            ])
        }
        
        # 添加错误摘要
        error_summary = {
            "count": len(self.db_errors),
            "last_24h": len([
                e for e in self.db_errors
                if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(days=1)
            ])
        }
        
        # 合并健康检查结果和摘要
        health_status = {
            **self.last_health_check,
            "slow_queries": slow_query_summary,
            "errors": error_summary
        }
        
        return health_status 