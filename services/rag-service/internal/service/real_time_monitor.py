#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实时监控和预警系统 - 提供全面的健康数据监控、系统性能监控和智能预警
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from collections import deque, defaultdict
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import websockets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"          # 信息
    WARNING = "warning"    # 警告
    CRITICAL = "critical"  # 严重
    EMERGENCY = "emergency" # 紧急

class AlertType(Enum):
    """预警类型"""
    HEALTH_ANOMALY = "health_anomaly"        # 健康异常
    SYSTEM_PERFORMANCE = "system_performance" # 系统性能
    DATA_QUALITY = "data_quality"            # 数据质量
    USER_BEHAVIOR = "user_behavior"          # 用户行为
    SECURITY = "security"                    # 安全
    BUSINESS = "business"                    # 业务

class MonitorStatus(Enum):
    """监控状态"""
    ACTIVE = "active"      # 活跃
    PAUSED = "paused"      # 暂停
    STOPPED = "stopped"    # 停止
    ERROR = "error"        # 错误

@dataclass
class Alert:
    """预警信息"""
    id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[str] = None
    metric_name: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class MonitorRule:
    """监控规则"""
    id: str
    name: str
    description: str
    metric_name: str
    condition: str  # 条件表达式，如 "> 140" 或 "< 60"
    threshold: float
    alert_level: AlertLevel
    alert_type: AlertType
    enabled: bool = True
    user_id: Optional[str] = None
    cooldown_minutes: int = 60  # 冷却时间（分钟）
    consecutive_violations: int = 1  # 连续违规次数
    context_filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthDataPoint:
    """健康数据点"""
    user_id: str
    metric_name: str
    value: float
    timestamp: datetime
    unit: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetric:
    """系统指标"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

class RealTimeMonitor:
    """实时监控和预警系统"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化实时监控系统
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # Redis连接
        self.redis_client = None
        
        # 监控规则
        self.monitor_rules: Dict[str, MonitorRule] = {}
        
        # 活跃预警
        self.active_alerts: Dict[str, Alert] = {}
        
        # 数据缓存
        self.data_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # 违规计数器
        self.violation_counters: Dict[str, int] = defaultdict(int)
        
        # 最后预警时间
        self.last_alert_time: Dict[str, datetime] = {}
        
        # 监控状态
        self.status = MonitorStatus.STOPPED
        
        # 事件回调
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # WebSocket连接
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Prometheus指标
        self.metrics_registry = CollectorRegistry()
        self._init_prometheus_metrics()
        
        # 异常检测器
        self.anomaly_detectors: Dict[str, Any] = {}
        
        # 统计信息
        self.stats = {
            "total_alerts": 0,
            "alerts_by_level": defaultdict(int),
            "alerts_by_type": defaultdict(int),
            "data_points_processed": 0,
            "rules_evaluated": 0
        }
    
    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        self.alert_counter = Counter(
            'rag_monitor_alerts_total',
            'Total number of alerts generated',
            ['level', 'type', 'user_id'],
            registry=self.metrics_registry
        )
        
        self.data_processing_time = Histogram(
            'rag_monitor_data_processing_seconds',
            'Time spent processing health data',
            registry=self.metrics_registry
        )
        
        self.active_alerts_gauge = Gauge(
            'rag_monitor_active_alerts',
            'Number of active alerts',
            ['level'],
            registry=self.metrics_registry
        )
        
        self.rule_evaluation_time = Histogram(
            'rag_monitor_rule_evaluation_seconds',
            'Time spent evaluating monitoring rules',
            registry=self.metrics_registry
        )
    
    async def initialize(self):
        """初始化监控系统"""
        logger.info("Initializing real-time monitor")
        
        # 初始化Redis连接
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0),
            decode_responses=True
        )
        
        # 加载监控规则
        await self._load_monitor_rules()
        
        # 初始化异常检测器
        await self._init_anomaly_detectors()
        
        # 启动监控任务
        self.status = MonitorStatus.ACTIVE
        
        # 启动后台任务
        asyncio.create_task(self._monitor_loop())
        asyncio.create_task(self._cleanup_loop())
        asyncio.create_task(self._stats_update_loop())
        
        logger.info("Real-time monitor initialized successfully")
    
    async def _load_monitor_rules(self):
        """加载监控规则"""
        # 默认健康监控规则
        default_rules = [
            MonitorRule(
                id="bp_systolic_high",
                name="收缩压过高",
                description="收缩压超过140mmHg",
                metric_name="blood_pressure_systolic",
                condition="> 140",
                threshold=140.0,
                alert_level=AlertLevel.WARNING,
                alert_type=AlertType.HEALTH_ANOMALY,
                consecutive_violations=2
            ),
            MonitorRule(
                id="bp_systolic_critical",
                name="收缩压危险",
                description="收缩压超过180mmHg",
                metric_name="blood_pressure_systolic",
                condition="> 180",
                threshold=180.0,
                alert_level=AlertLevel.CRITICAL,
                alert_type=AlertType.HEALTH_ANOMALY,
                consecutive_violations=1
            ),
            MonitorRule(
                id="heart_rate_high",
                name="心率过快",
                description="心率超过100次/分钟",
                metric_name="heart_rate",
                condition="> 100",
                threshold=100.0,
                alert_level=AlertLevel.WARNING,
                alert_type=AlertType.HEALTH_ANOMALY,
                consecutive_violations=3
            ),
            MonitorRule(
                id="heart_rate_low",
                name="心率过慢",
                description="心率低于60次/分钟",
                metric_name="heart_rate",
                condition="< 60",
                threshold=60.0,
                alert_level=AlertLevel.WARNING,
                alert_type=AlertType.HEALTH_ANOMALY,
                consecutive_violations=3
            ),
            MonitorRule(
                id="blood_glucose_high",
                name="血糖过高",
                description="血糖超过7.0mmol/L",
                metric_name="blood_glucose",
                condition="> 7.0",
                threshold=7.0,
                alert_level=AlertLevel.WARNING,
                alert_type=AlertType.HEALTH_ANOMALY,
                consecutive_violations=2
            ),
            MonitorRule(
                id="body_temperature_fever",
                name="发热",
                description="体温超过37.5°C",
                metric_name="body_temperature",
                condition="> 37.5",
                threshold=37.5,
                alert_level=AlertLevel.WARNING,
                alert_type=AlertType.HEALTH_ANOMALY,
                consecutive_violations=1
            )
        ]
        
        for rule in default_rules:
            self.monitor_rules[rule.id] = rule
        
        # 从Redis加载自定义规则
        try:
            custom_rules_data = await self.redis_client.get("monitor_rules")
            if custom_rules_data:
                custom_rules = json.loads(custom_rules_data)
                for rule_data in custom_rules:
                    rule = MonitorRule(**rule_data)
                    self.monitor_rules[rule.id] = rule
        except Exception as e:
            logger.warning(f"Failed to load custom monitor rules: {e}")
    
    async def _init_anomaly_detectors(self):
        """初始化异常检测器"""
        from sklearn.ensemble import IsolationForest
        from sklearn.svm import OneClassSVM
        
        # 为每个指标创建异常检测器
        metrics = [
            "blood_pressure_systolic", "blood_pressure_diastolic",
            "heart_rate", "blood_glucose", "body_temperature"
        ]
        
        for metric in metrics:
            self.anomaly_detectors[metric] = {
                "isolation_forest": IsolationForest(contamination=0.1, random_state=42),
                "one_class_svm": OneClassSVM(gamma='scale', nu=0.1),
                "data_buffer": deque(maxlen=100),
                "trained": False
            }
    
    async def process_health_data(self, data_point: HealthDataPoint):
        """
        处理健康数据点
        
        Args:
            data_point: 健康数据点
        """
        start_time = time.time()
        
        try:
            # 添加到数据缓存
            key = f"{data_point.user_id}:{data_point.metric_name}"
            self.data_buffer[key].append(data_point)
            
            # 更新异常检测器
            await self._update_anomaly_detector(data_point)
            
            # 评估监控规则
            await self._evaluate_rules(data_point)
            
            # 异常检测
            await self._detect_anomalies(data_point)
            
            # 更新统计信息
            self.stats["data_points_processed"] += 1
            
            # 记录处理时间
            processing_time = time.time() - start_time
            self.data_processing_time.observe(processing_time)
            
            logger.debug(f"Processed health data: {data_point.metric_name} = {data_point.value}")
            
        except Exception as e:
            logger.error(f"Error processing health data: {e}")
    
    async def _update_anomaly_detector(self, data_point: HealthDataPoint):
        """更新异常检测器"""
        detector_info = self.anomaly_detectors.get(data_point.metric_name)
        if not detector_info:
            return
        
        # 添加数据到缓冲区
        detector_info["data_buffer"].append(data_point.value)
        
        # 如果有足够的数据，训练检测器
        if len(detector_info["data_buffer"]) >= 20 and not detector_info["trained"]:
            data = np.array(detector_info["data_buffer"]).reshape(-1, 1)
            
            try:
                detector_info["isolation_forest"].fit(data)
                detector_info["one_class_svm"].fit(data)
                detector_info["trained"] = True
                logger.info(f"Trained anomaly detector for {data_point.metric_name}")
            except Exception as e:
                logger.warning(f"Failed to train anomaly detector for {data_point.metric_name}: {e}")
    
    async def _evaluate_rules(self, data_point: HealthDataPoint):
        """评估监控规则"""
        start_time = time.time()
        
        # 查找适用的规则
        applicable_rules = [
            rule for rule in self.monitor_rules.values()
            if rule.enabled and rule.metric_name == data_point.metric_name
            and (rule.user_id is None or rule.user_id == data_point.user_id)
        ]
        
        for rule in applicable_rules:
            try:
                # 评估条件
                violated = self._evaluate_condition(data_point.value, rule.condition, rule.threshold)
                
                rule_key = f"{rule.id}:{data_point.user_id}"
                
                if violated:
                    # 增加违规计数
                    self.violation_counters[rule_key] += 1
                    
                    # 检查是否达到连续违规次数
                    if self.violation_counters[rule_key] >= rule.consecutive_violations:
                        # 检查冷却时间
                        if await self._check_cooldown(rule_key, rule.cooldown_minutes):
                            await self._trigger_alert(rule, data_point)
                            self.violation_counters[rule_key] = 0
                            self.last_alert_time[rule_key] = datetime.now()
                else:
                    # 重置违规计数
                    self.violation_counters[rule_key] = 0
                
                self.stats["rules_evaluated"] += 1
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")
        
        # 记录评估时间
        evaluation_time = time.time() - start_time
        self.rule_evaluation_time.observe(evaluation_time)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估条件"""
        condition = condition.strip()
        
        if condition.startswith(">"):
            return value > threshold
        elif condition.startswith("<"):
            return value < threshold
        elif condition.startswith(">="):
            return value >= threshold
        elif condition.startswith("<="):
            return value <= threshold
        elif condition.startswith("=="):
            return abs(value - threshold) < 1e-6
        elif condition.startswith("!="):
            return abs(value - threshold) >= 1e-6
        else:
            return False
    
    async def _check_cooldown(self, rule_key: str, cooldown_minutes: int) -> bool:
        """检查冷却时间"""
        last_alert = self.last_alert_time.get(rule_key)
        if last_alert is None:
            return True
        
        cooldown_period = timedelta(minutes=cooldown_minutes)
        return datetime.now() - last_alert >= cooldown_period
    
    async def _trigger_alert(self, rule: MonitorRule, data_point: HealthDataPoint):
        """触发预警"""
        alert = Alert(
            id=str(uuid.uuid4()),
            alert_type=rule.alert_type,
            level=rule.alert_level,
            title=rule.name,
            description=f"{rule.description}。当前值：{data_point.value}{data_point.unit}",
            timestamp=datetime.now(),
            user_id=data_point.user_id,
            metric_name=data_point.metric_name,
            current_value=data_point.value,
            threshold_value=rule.threshold,
            context={
                "rule_id": rule.id,
                "source": data_point.source,
                "metadata": data_point.metadata
            }
        )
        
        # 添加到活跃预警
        self.active_alerts[alert.id] = alert
        
        # 更新统计信息
        self.stats["total_alerts"] += 1
        self.stats["alerts_by_level"][alert.level.value] += 1
        self.stats["alerts_by_type"][alert.alert_type.value] += 1
        
        # 更新Prometheus指标
        self.alert_counter.labels(
            level=alert.level.value,
            type=alert.alert_type.value,
            user_id=alert.user_id or "unknown"
        ).inc()
        
        self.active_alerts_gauge.labels(level=alert.level.value).inc()
        
        # 存储到Redis
        await self._store_alert(alert)
        
        # 发送通知
        await self._send_notifications(alert)
        
        # 调用回调函数
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        logger.warning(f"Alert triggered: {alert.title} for user {alert.user_id}")
    
    async def _detect_anomalies(self, data_point: HealthDataPoint):
        """异常检测"""
        detector_info = self.anomaly_detectors.get(data_point.metric_name)
        if not detector_info or not detector_info["trained"]:
            return
        
        try:
            value_array = np.array([[data_point.value]])
            
            # 使用Isolation Forest检测
            if_prediction = detector_info["isolation_forest"].predict(value_array)[0]
            
            # 使用One-Class SVM检测
            svm_prediction = detector_info["one_class_svm"].predict(value_array)[0]
            
            # 如果两个检测器都认为是异常
            if if_prediction == -1 and svm_prediction == -1:
                await self._trigger_anomaly_alert(data_point)
                
        except Exception as e:
            logger.error(f"Error in anomaly detection for {data_point.metric_name}: {e}")
    
    async def _trigger_anomaly_alert(self, data_point: HealthDataPoint):
        """触发异常预警"""
        alert = Alert(
            id=str(uuid.uuid4()),
            alert_type=AlertType.HEALTH_ANOMALY,
            level=AlertLevel.WARNING,
            title=f"{data_point.metric_name}异常值检测",
            description=f"检测到{data_point.metric_name}异常值：{data_point.value}{data_point.unit}",
            timestamp=datetime.now(),
            user_id=data_point.user_id,
            metric_name=data_point.metric_name,
            current_value=data_point.value,
            context={
                "detection_method": "anomaly_detection",
                "source": data_point.source,
                "metadata": data_point.metadata
            }
        )
        
        # 检查是否已有类似的异常预警
        similar_alerts = [
            a for a in self.active_alerts.values()
            if (a.user_id == alert.user_id and 
                a.metric_name == alert.metric_name and
                a.context.get("detection_method") == "anomaly_detection" and
                not a.resolved)
        ]
        
        if not similar_alerts:
            self.active_alerts[alert.id] = alert
            await self._store_alert(alert)
            await self._send_notifications(alert)
            
            logger.info(f"Anomaly alert triggered: {alert.title}")
    
    async def _store_alert(self, alert: Alert):
        """存储预警到Redis"""
        try:
            alert_data = {
                "id": alert.id,
                "alert_type": alert.alert_type.value,
                "level": alert.level.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "user_id": alert.user_id,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "context": alert.context,
                "resolved": alert.resolved
            }
            
            # 存储单个预警
            await self.redis_client.hset(f"alert:{alert.id}", mapping=alert_data)
            
            # 添加到用户预警列表
            if alert.user_id:
                await self.redis_client.lpush(f"user_alerts:{alert.user_id}", alert.id)
                await self.redis_client.expire(f"user_alerts:{alert.user_id}", 86400 * 30)  # 30天过期
            
            # 添加到全局预警列表
            await self.redis_client.lpush("all_alerts", alert.id)
            await self.redis_client.ltrim("all_alerts", 0, 9999)  # 保留最近10000条
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
    
    async def _send_notifications(self, alert: Alert):
        """发送通知"""
        # WebSocket实时通知
        await self._send_websocket_notification(alert)
        
        # 邮件通知（对于严重和紧急预警）
        if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            await self._send_email_notification(alert)
        
        # 短信通知（对于紧急预警）
        if alert.level == AlertLevel.EMERGENCY:
            await self._send_sms_notification(alert)
    
    async def _send_websocket_notification(self, alert: Alert):
        """发送WebSocket通知"""
        if not self.websocket_clients:
            return
        
        notification = {
            "type": "alert",
            "data": {
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "user_id": alert.user_id,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value
            }
        }
        
        # 发送给所有连接的客户端
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(notification))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {e}")
                disconnected_clients.add(client)
        
        # 移除断开的连接
        self.websocket_clients -= disconnected_clients
    
    async def _send_email_notification(self, alert: Alert):
        """发送邮件通知"""
        try:
            email_config = self.config.get('email', {})
            if not email_config.get('enabled', False):
                return
            
            # 获取用户邮箱
            user_email = await self._get_user_email(alert.user_id)
            if not user_email:
                return
            
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = email_config['from_address']
            msg['To'] = user_email
            msg['Subject'] = f"健康预警：{alert.title}"
            
            body = f"""
            尊敬的用户，
            
            我们检测到您的健康数据出现异常：
            
            预警类型：{alert.title}
            详细描述：{alert.description}
            发生时间：{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            当前值：{alert.current_value}
            
            请及时关注您的健康状况，如有需要请咨询医生。
            
            苏柯生活健康管理平台
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_sms_notification(self, alert: Alert):
        """发送短信通知"""
        try:
            sms_config = self.config.get('sms', {})
            if not sms_config.get('enabled', False):
                return
            
            # 获取用户手机号
            user_phone = await self._get_user_phone(alert.user_id)
            if not user_phone:
                return
            
            # 发送短信（这里需要集成具体的短信服务提供商）
            message = f"【苏柯生活】健康预警：{alert.title}，当前值：{alert.current_value}，请及时关注。"
            
            # TODO: 集成短信服务API
            logger.info(f"SMS notification would be sent to {user_phone}: {message}")
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """获取用户邮箱"""
        try:
            # 从Redis或数据库获取用户邮箱
            user_data = await self.redis_client.hget(f"user:{user_id}", "email")
            return user_data
        except Exception:
            return None
    
    async def _get_user_phone(self, user_id: str) -> Optional[str]:
        """获取用户手机号"""
        try:
            # 从Redis或数据库获取用户手机号
            user_data = await self.redis_client.hget(f"user:{user_id}", "phone")
            return user_data
        except Exception:
            return None
    
    async def add_monitor_rule(self, rule: MonitorRule) -> bool:
        """
        添加监控规则
        
        Args:
            rule: 监控规则
            
        Returns:
            是否添加成功
        """
        try:
            self.monitor_rules[rule.id] = rule
            
            # 保存到Redis
            await self._save_custom_rules()
            
            logger.info(f"Added monitor rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding monitor rule: {e}")
            return False
    
    async def remove_monitor_rule(self, rule_id: str) -> bool:
        """
        移除监控规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            是否移除成功
        """
        try:
            if rule_id in self.monitor_rules:
                del self.monitor_rules[rule_id]
                await self._save_custom_rules()
                logger.info(f"Removed monitor rule: {rule_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing monitor rule: {e}")
            return False
    
    async def _save_custom_rules(self):
        """保存自定义规则到Redis"""
        try:
            # 只保存非默认规则
            default_rule_ids = {
                "bp_systolic_high", "bp_systolic_critical", "heart_rate_high",
                "heart_rate_low", "blood_glucose_high", "body_temperature_fever"
            }
            
            custom_rules = [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "metric_name": rule.metric_name,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "alert_level": rule.alert_level.value,
                    "alert_type": rule.alert_type.value,
                    "enabled": rule.enabled,
                    "user_id": rule.user_id,
                    "cooldown_minutes": rule.cooldown_minutes,
                    "consecutive_violations": rule.consecutive_violations,
                    "context_filters": rule.context_filters
                }
                for rule in self.monitor_rules.values()
                if rule.id not in default_rule_ids
            ]
            
            await self.redis_client.set("monitor_rules", json.dumps(custom_rules))
            
        except Exception as e:
            logger.error(f"Error saving custom rules: {e}")
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """
        解决预警
        
        Args:
            alert_id: 预警ID
            resolution_note: 解决说明
            
        Returns:
            是否解决成功
        """
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                alert.actions_taken.append(f"手动解决: {resolution_note}")
                
                # 从活跃预警中移除
                del self.active_alerts[alert_id]
                
                # 更新Redis
                await self.redis_client.hset(f"alert:{alert_id}", mapping={
                    "resolved": True,
                    "resolved_at": alert.resolved_at.isoformat(),
                    "actions_taken": json.dumps(alert.actions_taken)
                })
                
                # 更新Prometheus指标
                self.active_alerts_gauge.labels(level=alert.level.value).dec()
                
                logger.info(f"Alert resolved: {alert_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    async def get_active_alerts(
        self,
        user_id: Optional[str] = None,
        alert_type: Optional[AlertType] = None,
        level: Optional[AlertLevel] = None
    ) -> List[Alert]:
        """
        获取活跃预警
        
        Args:
            user_id: 用户ID过滤
            alert_type: 预警类型过滤
            level: 预警级别过滤
            
        Returns:
            活跃预警列表
        """
        alerts = list(self.active_alerts.values())
        
        # 应用过滤条件
        if user_id:
            alerts = [a for a in alerts if a.user_id == user_id]
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # 按时间排序（最新的在前）
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return alerts
    
    async def get_alert_history(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Alert]:
        """
        获取预警历史
        
        Args:
            user_id: 用户ID过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制数量
            
        Returns:
            预警历史列表
        """
        try:
            # 从Redis获取预警ID列表
            if user_id:
                alert_ids = await self.redis_client.lrange(f"user_alerts:{user_id}", 0, limit - 1)
            else:
                alert_ids = await self.redis_client.lrange("all_alerts", 0, limit - 1)
            
            alerts = []
            for alert_id in alert_ids:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                if alert_data:
                    # 重构Alert对象
                    alert = Alert(
                        id=alert_data["id"],
                        alert_type=AlertType(alert_data["alert_type"]),
                        level=AlertLevel(alert_data["level"]),
                        title=alert_data["title"],
                        description=alert_data["description"],
                        timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                        user_id=alert_data.get("user_id"),
                        metric_name=alert_data.get("metric_name"),
                        current_value=float(alert_data["current_value"]) if alert_data.get("current_value") else None,
                        threshold_value=float(alert_data["threshold_value"]) if alert_data.get("threshold_value") else None,
                        context=json.loads(alert_data.get("context", "{}")),
                        resolved=alert_data.get("resolved", "false").lower() == "true",
                        resolved_at=datetime.fromisoformat(alert_data["resolved_at"]) if alert_data.get("resolved_at") else None,
                        actions_taken=json.loads(alert_data.get("actions_taken", "[]"))
                    )
                    
                    # 应用时间过滤
                    if start_time and alert.timestamp < start_time:
                        continue
                    if end_time and alert.timestamp > end_time:
                        continue
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        return {
            "status": self.status.value,
            "total_alerts": self.stats["total_alerts"],
            "active_alerts": len(self.active_alerts),
            "alerts_by_level": dict(self.stats["alerts_by_level"]),
            "alerts_by_type": dict(self.stats["alerts_by_type"]),
            "data_points_processed": self.stats["data_points_processed"],
            "rules_evaluated": self.stats["rules_evaluated"],
            "monitor_rules_count": len(self.monitor_rules),
            "websocket_clients": len(self.websocket_clients)
        }
    
    async def _monitor_loop(self):
        """监控主循环"""
        while self.status == MonitorStatus.ACTIVE:
            try:
                # 系统性能监控
                await self._monitor_system_performance()
                
                # 数据质量监控
                await self._monitor_data_quality()
                
                # 用户行为监控
                await self._monitor_user_behavior()
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_system_performance(self):
        """监控系统性能"""
        try:
            # 监控内存使用
            import psutil
            memory_usage = psutil.virtual_memory().percent
            
            if memory_usage > 90:
                alert = Alert(
                    id=str(uuid.uuid4()),
                    alert_type=AlertType.SYSTEM_PERFORMANCE,
                    level=AlertLevel.CRITICAL,
                    title="系统内存使用率过高",
                    description=f"系统内存使用率达到{memory_usage:.1f}%",
                    timestamp=datetime.now(),
                    current_value=memory_usage,
                    threshold_value=90.0,
                    context={"metric": "memory_usage"}
                )
                
                await self._trigger_system_alert(alert)
            
            # 监控CPU使用
            cpu_usage = psutil.cpu_percent(interval=1)
            
            if cpu_usage > 95:
                alert = Alert(
                    id=str(uuid.uuid4()),
                    alert_type=AlertType.SYSTEM_PERFORMANCE,
                    level=AlertLevel.CRITICAL,
                    title="系统CPU使用率过高",
                    description=f"系统CPU使用率达到{cpu_usage:.1f}%",
                    timestamp=datetime.now(),
                    current_value=cpu_usage,
                    threshold_value=95.0,
                    context={"metric": "cpu_usage"}
                )
                
                await self._trigger_system_alert(alert)
                
        except Exception as e:
            logger.error(f"Error monitoring system performance: {e}")
    
    async def _monitor_data_quality(self):
        """监控数据质量"""
        try:
            # 检查数据接收频率
            current_time = datetime.now()
            for key, buffer in self.data_buffer.items():
                if not buffer:
                    continue
                
                # 检查最后一次数据接收时间
                last_data_time = buffer[-1].timestamp
                time_since_last = current_time - last_data_time
                
                # 如果超过1小时没有数据
                if time_since_last > timedelta(hours=1):
                    user_id, metric_name = key.split(":", 1)
                    
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        alert_type=AlertType.DATA_QUALITY,
                        level=AlertLevel.WARNING,
                        title="数据接收中断",
                        description=f"用户{user_id}的{metric_name}数据已超过1小时未更新",
                        timestamp=datetime.now(),
                        user_id=user_id,
                        metric_name=metric_name,
                        context={
                            "last_data_time": last_data_time.isoformat(),
                            "time_since_last": str(time_since_last)
                        }
                    )
                    
                    await self._trigger_system_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error monitoring data quality: {e}")
    
    async def _monitor_user_behavior(self):
        """监控用户行为"""
        try:
            # 检查异常登录行为
            # 检查数据上传异常
            # 检查查询模式异常
            # 这里可以添加更多用户行为分析逻辑
            pass
            
        except Exception as e:
            logger.error(f"Error monitoring user behavior: {e}")
    
    async def _trigger_system_alert(self, alert: Alert):
        """触发系统预警"""
        # 检查是否已有相同的系统预警
        similar_alerts = [
            a for a in self.active_alerts.values()
            if (a.alert_type == alert.alert_type and
                a.context.get("metric") == alert.context.get("metric") and
                not a.resolved)
        ]
        
        if not similar_alerts:
            self.active_alerts[alert.id] = alert
            await self._store_alert(alert)
            await self._send_notifications(alert)
            
            logger.warning(f"System alert triggered: {alert.title}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.status == MonitorStatus.ACTIVE:
            try:
                # 清理过期的数据缓存
                await self._cleanup_data_buffer()
                
                # 清理已解决的预警
                await self._cleanup_resolved_alerts()
                
                await asyncio.sleep(3600)  # 每小时清理一次
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_data_buffer(self):
        """清理数据缓存"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)  # 保留24小时的数据
        
        for key, buffer in self.data_buffer.items():
            # 移除过期数据
            while buffer and buffer[0].timestamp < cutoff_time:
                buffer.popleft()
    
    async def _cleanup_resolved_alerts(self):
        """清理已解决的预警"""
        # 从Redis中删除超过30天的已解决预警
        cutoff_time = datetime.now() - timedelta(days=30)
        
        try:
            # 获取所有预警ID
            all_alert_ids = await self.redis_client.lrange("all_alerts", 0, -1)
            
            for alert_id in all_alert_ids:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                if alert_data and alert_data.get("resolved", "false").lower() == "true":
                    resolved_at = datetime.fromisoformat(alert_data.get("resolved_at", ""))
                    if resolved_at < cutoff_time:
                        # 删除过期的已解决预警
                        await self.redis_client.delete(f"alert:{alert_id}")
                        await self.redis_client.lrem("all_alerts", 0, alert_id)
                        
                        # 从用户预警列表中移除
                        user_id = alert_data.get("user_id")
                        if user_id:
                            await self.redis_client.lrem(f"user_alerts:{user_id}", 0, alert_id)
                            
        except Exception as e:
            logger.error(f"Error cleaning up resolved alerts: {e}")
    
    async def _stats_update_loop(self):
        """统计信息更新循环"""
        while self.status == MonitorStatus.ACTIVE:
            try:
                # 更新Prometheus指标
                for level in AlertLevel:
                    count = len([a for a in self.active_alerts.values() if a.level == level])
                    self.active_alerts_gauge.labels(level=level.value).set(count)
                
                await asyncio.sleep(30)  # 每30秒更新一次
                
            except Exception as e:
                logger.error(f"Error updating stats: {e}")
                await asyncio.sleep(30)
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """添加预警回调函数"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[Alert], None]):
        """移除预警回调函数"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    async def add_websocket_client(self, websocket: websockets.WebSocketServerProtocol):
        """添加WebSocket客户端"""
        self.websocket_clients.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.websocket_clients)}")
    
    async def remove_websocket_client(self, websocket: websockets.WebSocketServerProtocol):
        """移除WebSocket客户端"""
        self.websocket_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.websocket_clients)}")
    
    async def pause_monitoring(self):
        """暂停监控"""
        self.status = MonitorStatus.PAUSED
        logger.info("Monitoring paused")
    
    async def resume_monitoring(self):
        """恢复监控"""
        self.status = MonitorStatus.ACTIVE
        logger.info("Monitoring resumed")
    
    async def stop_monitoring(self):
        """停止监控"""
        self.status = MonitorStatus.STOPPED
        
        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()
        
        # 关闭WebSocket连接
        for client in self.websocket_clients:
            await client.close()
        
        logger.info("Monitoring stopped") 