#!/usr/bin/env python3

"""
实时监控仪表板
提供系统性能监控、设备状态监控、用户活动监控和健康指标监控功能
支持实时数据更新、告警通知、历史数据分析和可视化展示
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import psutil
from aiohttp import WSMsgType, web

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型枚举"""

    COUNTER = "counter"  # 计数器
    GAUGE = "gauge"  # 仪表
    HISTOGRAM = "histogram"  # 直方图
    SUMMARY = "summary"  # 摘要


class AlertLevel(Enum):
    """告警级别枚举"""

    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    ERROR = "error"  # 错误
    CRITICAL = "critical"  # 严重


class MonitoringStatus(Enum):
    """监控状态枚举"""

    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    ERROR = "error"  # 错误
    MAINTENANCE = "maintenance"  # 维护


@dataclass
class MetricData:
    """指标数据"""

    name: str
    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    unit: str = ""
    description: str = ""


@dataclass
class AlertRule:
    """告警规则"""

    name: str
    metric_name: str
    condition: str  # 条件表达式，如 "> 80"
    threshold: float
    level: AlertLevel
    duration: int = 60  # 持续时间（秒）
    enabled: bool = True
    description: str = ""
    actions: list[str] = field(default_factory=list)


@dataclass
class Alert:
    """告警信息"""

    id: str
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    level: AlertLevel
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: datetime | None = None


@dataclass
class SystemInfo:
    """系统信息"""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: dict[str, int]
    process_count: int
    uptime: float
    load_average: list[float]
    timestamp: datetime


@dataclass
class DeviceStatus:
    """设备状态"""

    device_id: str
    device_type: str
    status: str
    last_seen: datetime
    error_count: int = 0
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class UserActivity:
    """用户活动"""

    user_id: str
    session_id: str
    activity_type: str
    timestamp: datetime
    duration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.metrics = {}
        self.lock = threading.RLock()
        self.collectors = []

    def register_collector(self, collector: Callable[[], list[MetricData]]):
        """注册指标收集器"""
        self.collectors.append(collector)

    def collect_metric(self, metric: MetricData):
        """收集单个指标"""
        with self.lock:
            key = f"{metric.name}:{hash(frozenset(metric.labels.items()))}"
            self.metrics[key] = metric

    def collect_all_metrics(self) -> list[MetricData]:
        """收集所有指标"""
        all_metrics = []

        # 收集注册的收集器指标
        for collector in self.collectors:
            try:
                metrics = collector()
                all_metrics.extend(metrics)
            except Exception as e:
                logger.error(f"指标收集器错误: {e}")

        # 收集手动添加的指标
        with self.lock:
            all_metrics.extend(self.metrics.values())

        return all_metrics

    def get_metric(self, name: str, labels: dict[str, str] = None) -> MetricData | None:
        """获取指定指标"""
        if labels is None:
            labels = {}

        key = f"{name}:{hash(frozenset(labels.items()))}"
        with self.lock:
            return self.metrics.get(key)


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.lock = threading.RLock()
        self.handlers = []

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        with self.lock:
            self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        with self.lock:
            self.rules.pop(rule_name, None)

    def register_handler(self, handler: Callable[[Alert], None]):
        """注册告警处理器"""
        self.handlers.append(handler)

    def check_alerts(self, metrics: list[MetricData]):
        """检查告警"""
        current_time = datetime.now()

        for metric in metrics:
            self._check_metric_alerts(metric, current_time)

    def _check_metric_alerts(self, metric: MetricData, current_time: datetime):
        """检查单个指标的告警"""
        for rule in self.rules.values():
            if not rule.enabled or rule.metric_name != metric.name:
                continue

            try:
                # 评估条件
                if self._evaluate_condition(metric.value, rule.condition, rule.threshold):
                    self._trigger_alert(rule, metric, current_time)
                else:
                    self._resolve_alert(rule.name, current_time)

            except Exception as e:
                logger.error(f"告警检查错误: {rule.name}, {e}")

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估告警条件"""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 1e-6
        elif condition == "!=":
            return abs(value - threshold) >= 1e-6
        else:
            return False

    def _trigger_alert(self, rule: AlertRule, metric: MetricData, current_time: datetime):
        """触发告警"""
        alert_id = f"{rule.name}:{metric.name}"

        with self.lock:
            if alert_id in self.active_alerts:
                # 更新现有告警
                alert = self.active_alerts[alert_id]
                alert.current_value = metric.value
                alert.timestamp = current_time
            else:
                # 创建新告警
                alert = Alert(
                    id=alert_id,
                    rule_name=rule.name,
                    metric_name=metric.name,
                    current_value=metric.value,
                    threshold=rule.threshold,
                    level=rule.level,
                    message=f"{rule.description or rule.name}: {metric.value} {rule.condition} {rule.threshold}",
                    timestamp=current_time,
                )

                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)

                # 通知处理器
                for handler in self.handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"告警处理器错误: {e}")

    def _resolve_alert(self, rule_name: str, current_time: datetime):
        """解决告警"""
        alert_id_prefix = f"{rule_name}:"

        with self.lock:
            resolved_alerts = []
            for alert_id, alert in self.active_alerts.items():
                if alert_id.startswith(alert_id_prefix) and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = current_time
                    resolved_alerts.append(alert_id)

            # 移除已解决的告警
            for alert_id in resolved_alerts:
                self.active_alerts.pop(alert_id, None)

    def get_active_alerts(self) -> list[Alert]:
        """获取活跃告警"""
        with self.lock:
            return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """获取告警历史"""
        with self.lock:
            return list(self.alert_history)[-limit:]


class RealtimeDashboard:
    """实时监控仪表板"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化实时监控仪表板

        Args:
            config: 配置字典
        """
        self.config = config

        # 基础配置
        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 8080)
        self.update_interval = config.get("update_interval", 5)  # 更新间隔（秒）

        # 数据存储配置
        self.db_path = config.get("db_path", "monitoring/dashboard.db")
        self.retention_days = config.get("retention_days", 30)

        # 组件初始化
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()

        # 数据存储
        self.system_info_history = deque(maxlen=1000)
        self.device_statuses = {}
        self.user_activities = deque(maxlen=1000)
        self.connected_clients = set()

        # Web应用
        self.app = None
        self.runner = None
        self.site = None

        # 后台任务
        self.monitor_task = None
        self.cleanup_task = None

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)

        # 初始化组件
        self._initialize_components()

        logger.info("实时监控仪表板初始化完成")

    def _initialize_components(self):
        """初始化组件"""
        try:
            # 初始化数据库
            self._initialize_database()

            # 注册默认指标收集器
            self._register_default_collectors()

            # 注册默认告警规则
            self._register_default_alert_rules()

            # 注册告警处理器
            self._register_alert_handlers()

            # 创建Web应用
            self._create_web_app()

            logger.info("监控仪表板组件初始化完成")

        except Exception as e:
            logger.error(f"监控仪表板组件初始化失败: {e}")
            raise

    def _initialize_database(self):
        """初始化数据库"""
        try:
            # 创建数据库目录
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建指标表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    labels TEXT,
                    metric_type TEXT,
                    unit TEXT,
                    description TEXT
                )
            """
            )

            # 创建告警表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    rule_name TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP
                )
            """
            )

            # 创建系统信息表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS system_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_io TEXT,
                    process_count INTEGER,
                    uptime REAL,
                    load_average TEXT,
                    timestamp TIMESTAMP
                )
            """
            )

            # 创建设备状态表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS device_status (
                    device_id TEXT PRIMARY KEY,
                    device_type TEXT,
                    status TEXT,
                    last_seen TIMESTAMP,
                    error_count INTEGER DEFAULT 0,
                    metrics TEXT
                )
            """
            )

            # 创建用户活动表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    activity_type TEXT,
                    timestamp TIMESTAMP,
                    duration REAL,
                    metadata TEXT
                )
            """
            )

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_info_timestamp ON system_info(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp ON user_activities(timestamp)"
            )

            conn.commit()
            conn.close()

            logger.info("监控数据库初始化成功")

        except Exception as e:
            logger.error(f"监控数据库初始化失败: {e}")
            raise

    def _register_default_collectors(self):
        """注册默认指标收集器"""
        # 系统指标收集器
        self.metrics_collector.register_collector(self._collect_system_metrics)

        # 应用指标收集器
        self.metrics_collector.register_collector(self._collect_application_metrics)

    def _collect_system_metrics(self) -> list[MetricData]:
        """收集系统指标"""
        metrics = []
        current_time = datetime.now()

        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(
                MetricData(
                    name="system_cpu_percent",
                    value=cpu_percent,
                    timestamp=current_time,
                    unit="%",
                    description="CPU使用率",
                )
            )

            # 内存使用率
            memory = psutil.virtual_memory()
            metrics.append(
                MetricData(
                    name="system_memory_percent",
                    value=memory.percent,
                    timestamp=current_time,
                    unit="%",
                    description="内存使用率",
                )
            )

            # 磁盘使用率
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(
                MetricData(
                    name="system_disk_percent",
                    value=disk_percent,
                    timestamp=current_time,
                    unit="%",
                    description="磁盘使用率",
                )
            )

            # 网络IO
            network = psutil.net_io_counters()
            metrics.append(
                MetricData(
                    name="system_network_bytes_sent",
                    value=network.bytes_sent,
                    timestamp=current_time,
                    metric_type=MetricType.COUNTER,
                    unit="bytes",
                    description="网络发送字节数",
                )
            )

            metrics.append(
                MetricData(
                    name="system_network_bytes_recv",
                    value=network.bytes_recv,
                    timestamp=current_time,
                    metric_type=MetricType.COUNTER,
                    unit="bytes",
                    description="网络接收字节数",
                )
            )

            # 进程数量
            process_count = len(psutil.pids())
            metrics.append(
                MetricData(
                    name="system_process_count",
                    value=process_count,
                    timestamp=current_time,
                    description="系统进程数量",
                )
            )

            # 系统负载
            load_avg = psutil.getloadavg()
            for i, load in enumerate(load_avg):
                metrics.append(
                    MetricData(
                        name=f"system_load_avg_{i+1}m",
                        value=load,
                        timestamp=current_time,
                        description=f"系统{i+1}分钟平均负载",
                    )
                )

            # 存储系统信息历史
            system_info = SystemInfo(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk_percent,
                network_io={"bytes_sent": network.bytes_sent, "bytes_recv": network.bytes_recv},
                process_count=process_count,
                uptime=time.time() - psutil.boot_time(),
                load_average=list(load_avg),
                timestamp=current_time,
            )

            self.system_info_history.append(system_info)

        except Exception as e:
            logger.error(f"系统指标收集失败: {e}")

        return metrics

    def _collect_application_metrics(self) -> list[MetricData]:
        """收集应用指标"""
        metrics = []
        current_time = datetime.now()

        try:
            # 连接的客户端数量
            metrics.append(
                MetricData(
                    name="dashboard_connected_clients",
                    value=len(self.connected_clients),
                    timestamp=current_time,
                    description="连接的客户端数量",
                )
            )

            # 活跃告警数量
            active_alerts = self.alert_manager.get_active_alerts()
            metrics.append(
                MetricData(
                    name="dashboard_active_alerts",
                    value=len(active_alerts),
                    timestamp=current_time,
                    description="活跃告警数量",
                )
            )

            # 按级别统计告警
            alert_counts = defaultdict(int)
            for alert in active_alerts:
                alert_counts[alert.level.value] += 1

            for level, count in alert_counts.items():
                metrics.append(
                    MetricData(
                        name="dashboard_alerts_by_level",
                        value=count,
                        timestamp=current_time,
                        labels={"level": level},
                        description=f"{level}级别告警数量",
                    )
                )

            # 设备状态统计
            device_counts = defaultdict(int)
            for device in self.device_statuses.values():
                device_counts[device.status] += 1

            for status, count in device_counts.items():
                metrics.append(
                    MetricData(
                        name="dashboard_devices_by_status",
                        value=count,
                        timestamp=current_time,
                        labels={"status": status},
                        description=f"{status}状态设备数量",
                    )
                )

        except Exception as e:
            logger.error(f"应用指标收集失败: {e}")

        return metrics

    def _register_default_alert_rules(self):
        """注册默认告警规则"""
        # CPU使用率告警
        self.alert_manager.add_rule(
            AlertRule(
                name="high_cpu_usage",
                metric_name="system_cpu_percent",
                condition=">",
                threshold=80.0,
                level=AlertLevel.WARNING,
                description="CPU使用率过高",
            )
        )

        self.alert_manager.add_rule(
            AlertRule(
                name="critical_cpu_usage",
                metric_name="system_cpu_percent",
                condition=">",
                threshold=95.0,
                level=AlertLevel.CRITICAL,
                description="CPU使用率严重过高",
            )
        )

        # 内存使用率告警
        self.alert_manager.add_rule(
            AlertRule(
                name="high_memory_usage",
                metric_name="system_memory_percent",
                condition=">",
                threshold=85.0,
                level=AlertLevel.WARNING,
                description="内存使用率过高",
            )
        )

        self.alert_manager.add_rule(
            AlertRule(
                name="critical_memory_usage",
                metric_name="system_memory_percent",
                condition=">",
                threshold=95.0,
                level=AlertLevel.CRITICAL,
                description="内存使用率严重过高",
            )
        )

        # 磁盘使用率告警
        self.alert_manager.add_rule(
            AlertRule(
                name="high_disk_usage",
                metric_name="system_disk_percent",
                condition=">",
                threshold=90.0,
                level=AlertLevel.WARNING,
                description="磁盘使用率过高",
            )
        )

        self.alert_manager.add_rule(
            AlertRule(
                name="critical_disk_usage",
                metric_name="system_disk_percent",
                condition=">",
                threshold=98.0,
                level=AlertLevel.CRITICAL,
                description="磁盘使用率严重过高",
            )
        )

    def _register_alert_handlers(self):
        """注册告警处理器"""
        self.alert_manager.register_handler(self._log_alert_handler)
        self.alert_manager.register_handler(self._websocket_alert_handler)

    def _log_alert_handler(self, alert: Alert):
        """日志告警处理器"""
        level_map = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL,
        }

        logger.log(level_map.get(alert.level, logging.INFO), f"告警: {alert.message}")

    def _websocket_alert_handler(self, alert: Alert):
        """WebSocket告警处理器"""
        if self.connected_clients:
            alert_data = {"type": "alert", "data": asdict(alert)}

            # 异步发送给所有连接的客户端
            asyncio.create_task(self._broadcast_to_clients(alert_data))

    def _create_web_app(self):
        """创建Web应用"""
        self.app = web.Application()

        # 添加路由
        self.app.router.add_get("/", self._handle_index)
        self.app.router.add_get("/ws", self._handle_websocket)
        self.app.router.add_get("/api/metrics", self._handle_api_metrics)
        self.app.router.add_get("/api/alerts", self._handle_api_alerts)
        self.app.router.add_get("/api/system", self._handle_api_system)
        self.app.router.add_get("/api/devices", self._handle_api_devices)
        self.app.router.add_get("/api/activities", self._handle_api_activities)

        # 添加静态文件路由
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.router.add_static("/", static_dir, name="static")

    async def _handle_index(self, request):
        """处理首页请求"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>索克生活 - 触诊服务监控仪表板</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
                .alert { padding: 10px; margin: 5px 0; border-radius: 4px; }
                .alert-warning { background: #f39c12; color: white; }
                .alert-error { background: #e74c3c; color: white; }
                .alert-critical { background: #c0392b; color: white; }
                .status-online { color: #27ae60; }
                .status-offline { color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>索克生活 - 触诊服务监控仪表板</h1>
                    <p>实时监控系统性能、设备状态和用户活动</p>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>系统状态</h3>
                        <div id="system-status">加载中...</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>活跃告警</h3>
                        <div id="active-alerts">加载中...</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>设备状态</h3>
                        <div id="device-status">加载中...</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>用户活动</h3>
                        <div id="user-activity">加载中...</div>
                    </div>
                </div>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8080/ws');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                function updateDashboard(data) {
                    if (data.type === 'metrics') {
                        updateMetrics(data.data);
                    } else if (data.type === 'alert') {
                        showAlert(data.data);
                    }
                }
                
                function updateMetrics(metrics) {
                    // 更新系统状态
                    const systemMetrics = metrics.filter(m => m.name.startsWith('system_'));
                    const systemHtml = systemMetrics.map(m => 
                        `<div>${m.description}: <span class="metric-value">${m.value.toFixed(1)}${m.unit}</span></div>`
                    ).join('');
                    document.getElementById('system-status').innerHTML = systemHtml;
                }
                
                function showAlert(alert) {
                    const alertsDiv = document.getElementById('active-alerts');
                    const alertHtml = `<div class="alert alert-${alert.level}">${alert.message}</div>`;
                    alertsDiv.innerHTML = alertHtml + alertsDiv.innerHTML;
                }
                
                // 定期获取数据
                setInterval(async () => {
                    try {
                        const response = await fetch('/api/metrics');
                        const metrics = await response.json();
                        updateMetrics(metrics);
                    } catch (error) {
                        console.error('获取指标失败:', error);
                    }
                }, 5000);
            </script>
        </body>
        </html>
        """

        return web.Response(text=html_content, content_type="text/html")

    async def _handle_websocket(self, request):
        """处理WebSocket连接"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.connected_clients.add(ws)
        logger.info(f"新的WebSocket连接，当前连接数: {len(self.connected_clients)}")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(
                            json.dumps({"type": "error", "message": "无效的JSON格式"})
                        )
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket错误: {ws.exception()}")
        except Exception as e:
            logger.error(f"WebSocket处理错误: {e}")
        finally:
            self.connected_clients.discard(ws)
            logger.info(f"WebSocket连接断开，当前连接数: {len(self.connected_clients)}")

        return ws

    async def _handle_websocket_message(self, ws, data):
        """处理WebSocket消息"""
        message_type = data.get("type")

        if message_type == "subscribe":
            # 发送当前状态
            await self._send_current_status(ws)
        elif message_type == "ping":
            await ws.send_str(json.dumps({"type": "pong"}))

    async def _send_current_status(self, ws):
        """发送当前状态"""
        try:
            # 发送当前指标
            metrics = self.metrics_collector.collect_all_metrics()
            await ws.send_str(json.dumps({"type": "metrics", "data": [asdict(m) for m in metrics]}))

            # 发送活跃告警
            alerts = self.alert_manager.get_active_alerts()
            await ws.send_str(json.dumps({"type": "alerts", "data": [asdict(a) for a in alerts]}))

        except Exception as e:
            logger.error(f"发送当前状态失败: {e}")

    async def _handle_api_metrics(self, request):
        """处理指标API请求"""
        try:
            metrics = self.metrics_collector.collect_all_metrics()
            return web.json_response([asdict(m) for m in metrics])
        except Exception as e:
            logger.error(f"获取指标失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_api_alerts(self, request):
        """处理告警API请求"""
        try:
            alerts = self.alert_manager.get_active_alerts()
            return web.json_response([asdict(a) for a in alerts])
        except Exception as e:
            logger.error(f"获取告警失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_api_system(self, request):
        """处理系统信息API请求"""
        try:
            if self.system_info_history:
                latest_info = self.system_info_history[-1]
                return web.json_response(asdict(latest_info))
            else:
                return web.json_response({"error": "暂无系统信息"}, status=404)
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_api_devices(self, request):
        """处理设备状态API请求"""
        try:
            devices = [asdict(device) for device in self.device_statuses.values()]
            return web.json_response(devices)
        except Exception as e:
            logger.error(f"获取设备状态失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_api_activities(self, request):
        """处理用户活动API请求"""
        try:
            activities = [asdict(activity) for activity in list(self.user_activities)[-100:]]
            return web.json_response(activities)
        except Exception as e:
            logger.error(f"获取用户活动失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _broadcast_to_clients(self, data):
        """广播数据到所有客户端"""
        if not self.connected_clients:
            return

        message = json.dumps(data)
        disconnected_clients = set()

        for client in self.connected_clients:
            try:
                await client.send_str(message)
            except Exception as e:
                logger.warning(f"发送消息到客户端失败: {e}")
                disconnected_clients.add(client)

        # 移除断开的客户端
        self.connected_clients -= disconnected_clients

    async def start(self):
        """启动监控仪表板"""
        try:
            # 启动Web服务器
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            # 启动后台任务
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

            logger.info(f"监控仪表板启动成功: http://{self.host}:{self.port}")

        except Exception as e:
            logger.error(f"监控仪表板启动失败: {e}")
            raise

    async def stop(self):
        """停止监控仪表板"""
        try:
            # 停止后台任务
            if self.monitor_task:
                self.monitor_task.cancel()
            if self.cleanup_task:
                self.cleanup_task.cancel()

            # 关闭WebSocket连接
            for client in list(self.connected_clients):
                await client.close()

            # 停止Web服务器
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()

            # 关闭线程池
            self.executor.shutdown(wait=True)

            logger.info("监控仪表板停止完成")

        except Exception as e:
            logger.error(f"监控仪表板停止失败: {e}")

    async def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                # 收集指标
                metrics = self.metrics_collector.collect_all_metrics()

                # 检查告警
                self.alert_manager.check_alerts(metrics)

                # 保存指标到数据库
                await self._save_metrics_to_db(metrics)

                # 广播指标到客户端
                if self.connected_clients:
                    await self._broadcast_to_clients(
                        {"type": "metrics", "data": [asdict(m) for m in metrics]}
                    )

                await asyncio.sleep(self.update_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(self.update_interval)

    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时执行一次
                await self._cleanup_old_data()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环错误: {e}")

    async def _save_metrics_to_db(self, metrics: list[MetricData]):
        """保存指标到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for metric in metrics:
                cursor.execute(
                    """
                    INSERT INTO metrics 
                    (name, value, timestamp, labels, metric_type, unit, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric.name,
                        metric.value,
                        metric.timestamp.isoformat(),
                        json.dumps(metric.labels),
                        metric.metric_type.value,
                        metric.unit,
                        metric.description,
                    ),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"保存指标到数据库失败: {e}")

    async def _cleanup_old_data(self):
        """清理旧数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 清理旧指标
            cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date.isoformat(),))

            # 清理旧告警
            cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (cutoff_date.isoformat(),))

            # 清理旧系统信息
            cursor.execute(
                "DELETE FROM system_info WHERE timestamp < ?", (cutoff_date.isoformat(),)
            )

            # 清理旧用户活动
            cursor.execute(
                "DELETE FROM user_activities WHERE timestamp < ?", (cutoff_date.isoformat(),)
            )

            conn.commit()
            conn.close()

            logger.info(f"清理{self.retention_days}天前的旧数据完成")

        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")

    def update_device_status(self, device_status: DeviceStatus):
        """更新设备状态"""
        self.device_statuses[device_status.device_id] = device_status

        # 保存到数据库
        asyncio.create_task(self._save_device_status_to_db(device_status))

    async def _save_device_status_to_db(self, device_status: DeviceStatus):
        """保存设备状态到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO device_status 
                (device_id, device_type, status, last_seen, error_count, metrics)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    device_status.device_id,
                    device_status.device_type,
                    device_status.status,
                    device_status.last_seen.isoformat(),
                    device_status.error_count,
                    json.dumps(device_status.metrics),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"保存设备状态到数据库失败: {e}")

    def add_user_activity(self, activity: UserActivity):
        """添加用户活动"""
        self.user_activities.append(activity)

        # 保存到数据库
        asyncio.create_task(self._save_user_activity_to_db(activity))

    async def _save_user_activity_to_db(self, activity: UserActivity):
        """保存用户活动到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO user_activities 
                (user_id, session_id, activity_type, timestamp, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    activity.user_id,
                    activity.session_id,
                    activity.activity_type,
                    activity.timestamp.isoformat(),
                    activity.duration,
                    json.dumps(activity.metadata),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"保存用户活动到数据库失败: {e}")

    def add_custom_metric(self, metric: MetricData):
        """添加自定义指标"""
        self.metrics_collector.collect_metric(metric)

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_manager.add_rule(rule)

    def get_dashboard_stats(self) -> dict[str, Any]:
        """获取仪表板统计"""
        return {
            "connected_clients": len(self.connected_clients),
            "active_alerts": len(self.alert_manager.get_active_alerts()),
            "device_count": len(self.device_statuses),
            "recent_activities": len(self.user_activities),
            "system_info_history_size": len(self.system_info_history),
            "uptime": time.time() - psutil.boot_time(),
        }
