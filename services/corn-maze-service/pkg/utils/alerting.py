#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
监控告警系统 - 支持多种告警渠道和规则配置
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from pkg.utils.cache import CacheManager
from pkg.utils.metrics import get_metric_value, errors_total

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """告警状态"""
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """告警对象"""
    id: str
    name: str
    level: AlertLevel
    status: AlertStatus
    message: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: Optional[datetime] = None
    generator_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "status": self.status.value,
            "message": self.message,
            "labels": self.labels,
            "annotations": self.annotations,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
            "generator_url": self.generator_url
        }

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: str  # 条件表达式
    threshold: float
    duration: int  # 持续时间（秒）
    level: AlertLevel
    message_template: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    def evaluate(self, metric_value: float) -> bool:
        """评估规则"""
        if not self.enabled:
            return False
        
        if self.condition == "gt":  # 大于
            return metric_value > self.threshold
        elif self.condition == "lt":  # 小于
            return metric_value < self.threshold
        elif self.condition == "eq":  # 等于
            return metric_value == self.threshold
        elif self.condition == "gte":  # 大于等于
            return metric_value >= self.threshold
        elif self.condition == "lte":  # 小于等于
            return metric_value <= self.threshold
        else:
            return False
    
    def format_message(self, metric_value: float, **kwargs) -> str:
        """格式化告警消息"""
        return self.message_template.format(
            value=metric_value,
            threshold=self.threshold,
            **kwargs
        )

class AlertChannel(ABC):
    """告警渠道抽象基类"""
    
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """发送告警"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接"""
        pass

class EmailChannel(AlertChannel):
    """邮件告警渠道"""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.use_tls = use_tls
    
    async def send_alert(self, alert: Alert) -> bool:
        """发送邮件告警"""
        try:
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.name}"
            
            # 邮件正文
            body = self._format_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            # 发送邮件
            await asyncio.get_event_loop().run_in_executor(
                None, self._send_email, msg
            )
            
            logger.info(f"邮件告警发送成功: {alert.name}")
            return True
            
        except Exception as e:
            logger.error(f"邮件告警发送失败: {str(e)}")
            return False
    
    def _send_email(self, msg: MIMEMultipart):
        """同步发送邮件"""
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        
        if self.use_tls:
            server.starttls()
        
        server.login(self.username, self.password)
        server.send_message(msg)
        server.quit()
    
    def _format_email_body(self, alert: Alert) -> str:
        """格式化邮件正文"""
        return f"""
        <html>
        <body>
            <h2>告警通知</h2>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><b>告警名称</b></td><td>{alert.name}</td></tr>
                <tr><td><b>告警级别</b></td><td>{alert.level.value.upper()}</td></tr>
                <tr><td><b>告警状态</b></td><td>{alert.status.value.upper()}</td></tr>
                <tr><td><b>告警消息</b></td><td>{alert.message}</td></tr>
                <tr><td><b>开始时间</b></td><td>{alert.starts_at.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                {f'<tr><td><b>结束时间</b></td><td>{alert.ends_at.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>' if alert.ends_at else ''}
            </table>
            
            {self._format_labels_table(alert.labels) if alert.labels else ''}
            {self._format_annotations_table(alert.annotations) if alert.annotations else ''}
            
            <p><small>此邮件由索克生活监控系统自动发送</small></p>
        </body>
        </html>
        """
    
    def _format_labels_table(self, labels: Dict[str, str]) -> str:
        """格式化标签表格"""
        rows = ''.join([f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in labels.items()])
        return f"""
        <h3>标签</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            {rows}
        </table>
        """
    
    def _format_annotations_table(self, annotations: Dict[str, str]) -> str:
        """格式化注释表格"""
        rows = ''.join([f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in annotations.items()])
        return f"""
        <h3>注释</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            {rows}
        </table>
        """
    
    async def test_connection(self) -> bool:
        """测试邮件连接"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self._test_smtp_connection
            )
            return True
        except Exception as e:
            logger.error(f"邮件连接测试失败: {str(e)}")
            return False
    
    def _test_smtp_connection(self):
        """测试SMTP连接"""
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        if self.use_tls:
            server.starttls()
        server.login(self.username, self.password)
        server.quit()

class WebhookChannel(AlertChannel):
    """Webhook告警渠道"""
    
    def __init__(
        self,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ):
        self.url = url
        self.method = method.upper()
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
    
    async def send_alert(self, alert: Alert) -> bool:
        """发送Webhook告警"""
        try:
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.now().isoformat(),
                "source": "corn-maze-service"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.method,
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status < 400:
                        logger.info(f"Webhook告警发送成功: {alert.name}")
                        return True
                    else:
                        logger.error(f"Webhook告警发送失败: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Webhook告警发送失败: {str(e)}")
            return False
    
    async def test_connection(self) -> bool:
        """测试Webhook连接"""
        try:
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "source": "corn-maze-service"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.method,
                    self.url,
                    json=test_payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    return response.status < 400
                    
        except Exception as e:
            logger.error(f"Webhook连接测试失败: {str(e)}")
            return False

class SlackChannel(AlertChannel):
    """Slack告警渠道"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_alert(self, alert: Alert) -> bool:
        """发送Slack告警"""
        try:
            # 根据告警级别选择颜色
            color_map = {
                AlertLevel.INFO: "#36a64f",      # 绿色
                AlertLevel.WARNING: "#ff9900",   # 橙色
                AlertLevel.ERROR: "#ff0000",     # 红色
                AlertLevel.CRITICAL: "#8b0000"   # 深红色
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.level, "#36a64f"),
                        "title": f"{alert.level.value.upper()}: {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "状态",
                                "value": alert.status.value.upper(),
                                "short": True
                            },
                            {
                                "title": "开始时间",
                                "value": alert.starts_at.strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            }
                        ],
                        "footer": "索克生活监控系统",
                        "ts": int(alert.starts_at.timestamp())
                    }
                ]
            }
            
            # 添加标签字段
            if alert.labels:
                for key, value in alert.labels.items():
                    payload["attachments"][0]["fields"].append({
                        "title": key,
                        "value": value,
                        "short": True
                    })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Slack告警发送成功: {alert.name}")
                        return True
                    else:
                        logger.error(f"Slack告警发送失败: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Slack告警发送失败: {str(e)}")
            return False
    
    async def test_connection(self) -> bool:
        """测试Slack连接"""
        try:
            test_payload = {
                "text": "测试消息 - 索克生活监控系统连接正常"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Slack连接测试失败: {str(e)}")
            return False

class AlertManager:
    """告警管理器"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager()
        self.rules: Dict[str, AlertRule] = {}
        self.channels: Dict[str, AlertChannel] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.rule_states: Dict[str, Dict[str, Any]] = {}
        
        # 告警抑制规则
        self.suppression_rules: List[Dict[str, Any]] = []
        
        # 运行状态
        self._running = False
        self._evaluation_task: Optional[asyncio.Task] = None
        
        logger.info("告警管理器初始化完成")
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.name] = rule
        self.rule_states[rule.name] = {
            "last_evaluation": None,
            "consecutive_violations": 0,
            "alert_fired": False
        }
        logger.info(f"添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            del self.rule_states[rule_name]
            logger.info(f"移除告警规则: {rule_name}")
    
    def add_channel(self, name: str, channel: AlertChannel):
        """添加告警渠道"""
        self.channels[name] = channel
        logger.info(f"添加告警渠道: {name}")
    
    def remove_channel(self, name: str):
        """移除告警渠道"""
        if name in self.channels:
            del self.channels[name]
            logger.info(f"移除告警渠道: {name}")
    
    async def start(self, evaluation_interval: int = 30):
        """启动告警管理器"""
        if self._running:
            logger.warning("告警管理器已在运行")
            return
        
        self._running = True
        self._evaluation_task = asyncio.create_task(
            self._evaluation_loop(evaluation_interval)
        )
        logger.info(f"告警管理器已启动，评估间隔: {evaluation_interval}秒")
    
    async def stop(self):
        """停止告警管理器"""
        self._running = False
        
        if self._evaluation_task:
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("告警管理器已停止")
    
    async def _evaluation_loop(self, interval: int):
        """评估循环"""
        while self._running:
            try:
                await self._evaluate_rules()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"告警规则评估失败: {str(e)}")
                await asyncio.sleep(interval)
    
    async def _evaluate_rules(self):
        """评估所有告警规则"""
        for rule_name, rule in self.rules.items():
            try:
                await self._evaluate_rule(rule_name, rule)
            except Exception as e:
                logger.error(f"评估规则 {rule_name} 失败: {str(e)}")
    
    async def _evaluate_rule(self, rule_name: str, rule: AlertRule):
        """评估单个告警规则"""
        if not rule.enabled:
            return
        
        # 获取指标值（这里需要根据实际的指标系统实现）
        metric_value = await self._get_metric_value(rule_name)
        if metric_value is None:
            return
        
        state = self.rule_states[rule_name]
        current_time = time.time()
        
        # 评估条件
        condition_met = rule.evaluate(metric_value)
        
        if condition_met:
            state["consecutive_violations"] += 1
            
            # 检查是否达到持续时间要求
            if (state["consecutive_violations"] * 30 >= rule.duration and  # 假设评估间隔30秒
                not state["alert_fired"]):
                
                # 触发告警
                alert = Alert(
                    id=f"{rule_name}_{int(current_time)}",
                    name=rule.name,
                    level=rule.level,
                    status=AlertStatus.FIRING,
                    message=rule.format_message(metric_value),
                    labels=rule.labels.copy(),
                    annotations=rule.annotations.copy(),
                    starts_at=datetime.now()
                )
                
                await self._fire_alert(alert)
                state["alert_fired"] = True
                
        else:
            # 条件不满足，重置计数器
            if state["alert_fired"]:
                # 解决告警
                await self._resolve_alert(rule_name)
                state["alert_fired"] = False
            
            state["consecutive_violations"] = 0
        
        state["last_evaluation"] = current_time
    
    async def _get_metric_value(self, rule_name: str) -> Optional[float]:
        """获取指标值"""
        # 这里应该根据实际的指标系统实现
        # 例如从Prometheus、自定义指标等获取
        try:
            # 示例：从内存指标获取
            if "error_rate" in rule_name:
                return await get_metric_value("errors_total")
            elif "response_time" in rule_name:
                return await get_metric_value("response_time_seconds")
            elif "memory_usage" in rule_name:
                return await get_metric_value("memory_usage_bytes")
            else:
                return 0.0
        except Exception as e:
            logger.error(f"获取指标值失败: {str(e)}")
            return None
    
    async def _fire_alert(self, alert: Alert):
        """触发告警"""
        # 检查告警抑制
        if await self._is_suppressed(alert):
            alert.status = AlertStatus.SUPPRESSED
            logger.info(f"告警被抑制: {alert.name}")
            return
        
        # 存储活跃告警
        self.active_alerts[alert.id] = alert
        
        # 发送到所有渠道
        for channel_name, channel in self.channels.items():
            try:
                success = await channel.send_alert(alert)
                if success:
                    logger.info(f"告警发送成功 [{channel_name}]: {alert.name}")
                else:
                    logger.error(f"告警发送失败 [{channel_name}]: {alert.name}")
            except Exception as e:
                logger.error(f"告警发送异常 [{channel_name}]: {str(e)}")
        
        # 缓存告警
        await self.cache_manager.set(
            f"alert:{alert.id}",
            alert.to_dict(),
            ttl=86400  # 24小时
        )
        
        logger.info(f"告警已触发: {alert.name}")
    
    async def _resolve_alert(self, rule_name: str):
        """解决告警"""
        # 查找对应的活跃告警
        alert_to_resolve = None
        for alert_id, alert in self.active_alerts.items():
            if alert.name == rule_name:
                alert_to_resolve = alert
                break
        
        if alert_to_resolve:
            alert_to_resolve.status = AlertStatus.RESOLVED
            alert_to_resolve.ends_at = datetime.now()
            
            # 发送解决通知
            for channel_name, channel in self.channels.items():
                try:
                    await channel.send_alert(alert_to_resolve)
                except Exception as e:
                    logger.error(f"告警解决通知发送失败 [{channel_name}]: {str(e)}")
            
            # 从活跃告警中移除
            del self.active_alerts[alert_to_resolve.id]
            
            logger.info(f"告警已解决: {rule_name}")
    
    async def _is_suppressed(self, alert: Alert) -> bool:
        """检查告警是否被抑制"""
        for rule in self.suppression_rules:
            if self._match_suppression_rule(alert, rule):
                return True
        return False
    
    def _match_suppression_rule(self, alert: Alert, rule: Dict[str, Any]) -> bool:
        """匹配抑制规则"""
        # 简单的标签匹配实现
        for key, value in rule.get("matchers", {}).items():
            if alert.labels.get(key) != value:
                return False
        return True
    
    async def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取告警历史"""
        # 从缓存中获取历史告警
        history = []
        # 这里应该实现从缓存或数据库获取历史告警的逻辑
        return history
    
    async def test_channels(self) -> Dict[str, bool]:
        """测试所有告警渠道"""
        results = {}
        for name, channel in self.channels.items():
            try:
                results[name] = await channel.test_connection()
            except Exception as e:
                logger.error(f"测试渠道 {name} 失败: {str(e)}")
                results[name] = False
        return results

# 预定义的告警规则
def get_default_alert_rules() -> List[AlertRule]:
    """获取默认告警规则"""
    return [
        AlertRule(
            name="high_error_rate",
            condition="gt",
            threshold=0.05,  # 5%错误率
            duration=300,    # 5分钟
            level=AlertLevel.WARNING,
            message_template="错误率过高: {value:.2%} (阈值: {threshold:.2%})",
            labels={"service": "corn-maze-service", "type": "error_rate"},
            annotations={"description": "服务错误率超过阈值"}
        ),
        AlertRule(
            name="high_response_time",
            condition="gt",
            threshold=2.0,   # 2秒
            duration=180,    # 3分钟
            level=AlertLevel.WARNING,
            message_template="响应时间过长: {value:.2f}s (阈值: {threshold:.2f}s)",
            labels={"service": "corn-maze-service", "type": "response_time"},
            annotations={"description": "服务响应时间超过阈值"}
        ),
        AlertRule(
            name="high_memory_usage",
            condition="gt",
            threshold=0.8,   # 80%内存使用率
            duration=600,    # 10分钟
            level=AlertLevel.ERROR,
            message_template="内存使用率过高: {value:.2%} (阈值: {threshold:.2%})",
            labels={"service": "corn-maze-service", "type": "memory_usage"},
            annotations={"description": "服务内存使用率超过阈值"}
        ),
        AlertRule(
            name="service_down",
            condition="eq",
            threshold=0,     # 服务不可用
            duration=60,     # 1分钟
            level=AlertLevel.CRITICAL,
            message_template="服务不可用",
            labels={"service": "corn-maze-service", "type": "availability"},
            annotations={"description": "服务完全不可用"}
        )
    ]

# 全局告警管理器
_alert_manager: Optional[AlertManager] = None

def get_alert_manager() -> AlertManager:
    """获取全局告警管理器"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager 