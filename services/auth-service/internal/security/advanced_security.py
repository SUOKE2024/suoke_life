"""
高级安全模块
包含威胁检测、IP白名单、设备指纹识别和异常行为检测
"""

import asyncio
import hashlib
import json
import logging
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
from collections import defaultdict, deque
import geoip2.database
import geoip2.errors
from redis.asyncio import Redis
import user_agents
from cryptography.fernet import Fernet
import hmac
import secrets

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """威胁级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """安全动作"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    CAPTCHA = "captcha"
    MFA_REQUIRED = "mfa_required"


@dataclass
class SecurityEvent:
    """安全事件"""
    event_type: str
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    action_taken: Optional[SecurityAction] = None


@dataclass
class DeviceFingerprint:
    """设备指纹"""
    fingerprint_hash: str
    user_agent: str
    screen_resolution: Optional[str]
    timezone: Optional[str]
    language: str
    platform: str
    browser: str
    browser_version: str
    os: str
    os_version: str
    created_at: datetime
    last_seen: datetime
    trust_score: float = 0.0


@dataclass
class IPInfo:
    """IP信息"""
    ip_address: str
    country: Optional[str]
    city: Optional[str]
    isp: Optional[str]
    is_proxy: bool = False
    is_tor: bool = False
    is_vpn: bool = False
    risk_score: float = 0.0
    first_seen: datetime
    last_seen: datetime


class AdvancedSecurityManager:
    """高级安全管理器"""
    
    def __init__(self, redis: Redis, geoip_db_path: Optional[str] = None):
        self.redis = redis
        self.geoip_reader = None
        
        # 初始化GeoIP数据库
        if geoip_db_path:
            try:
                self.geoip_reader = geoip2.database.Reader(geoip_db_path)
            except Exception as e:
                logger.warning(f"无法加载GeoIP数据库: {e}")
        
        # 安全配置
        self.config = {
            'max_login_attempts': 5,
            'lockout_duration': 900,  # 15分钟
            'suspicious_ip_threshold': 10,
            'rate_limit_window': 300,  # 5分钟
            'rate_limit_max_requests': 100,
            'device_trust_threshold': 0.7,
            'geo_anomaly_threshold': 1000,  # 公里
            'password_breach_check': True,
            'enable_device_tracking': True
        }
        
        # 内存缓存
        self._ip_whitelist: Set[str] = set()
        self._ip_blacklist: Set[str] = set()
        self._suspicious_ips: Dict[str, int] = defaultdict(int)
        self._rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._security_events: deque = deque(maxlen=10000)
        self._device_fingerprints: Dict[str, DeviceFingerprint] = {}
        
        # 威胁检测规则
        self._threat_patterns = {
            'sql_injection': [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(\b(or|and)\s+\d+\s*=\s*\d+)",
                r"(\b(or|and)\s+['\"].*['\"])",
                r"(--|#|/\*|\*/)"
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>"
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c"
            ],
            'command_injection': [
                r"[;&|`$]",
                r"\b(cat|ls|pwd|whoami|id|uname)\b",
                r"\$\([^)]*\)",
                r"`[^`]*`"
            ]
        }
        
        # 编译正则表达式
        self._compiled_patterns = {}
        for threat_type, patterns in self._threat_patterns.items():
            self._compiled_patterns[threat_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        
        # 启动后台任务
        asyncio.create_task(self._load_security_data())
        asyncio.create_task(self._cleanup_expired_data())
    
    async def _load_security_data(self):
        """加载安全数据"""
        try:
            # 加载IP白名单
            whitelist_data = await self.redis.smembers("security:ip_whitelist")
            self._ip_whitelist = {ip.decode() for ip in whitelist_data}
            
            # 加载IP黑名单
            blacklist_data = await self.redis.smembers("security:ip_blacklist")
            self._ip_blacklist = {ip.decode() for ip in blacklist_data}
            
            logger.info(f"加载安全数据完成: 白名单{len(self._ip_whitelist)}个IP, 黑名单{len(self._ip_blacklist)}个IP")
            
        except Exception as e:
            logger.error(f"加载安全数据失败: {e}")
    
    async def _cleanup_expired_data(self):
        """清理过期数据"""
        while True:
            try:
                # 清理过期的速率限制数据
                current_time = datetime.now()
                for ip, requests in list(self._rate_limits.items()):
                    # 移除5分钟前的请求记录
                    cutoff_time = current_time - timedelta(seconds=self.config['rate_limit_window'])
                    while requests and requests[0] < cutoff_time:
                        requests.popleft()
                    
                    # 如果队列为空，删除该IP的记录
                    if not requests:
                        del self._rate_limits[ip]
                
                # 清理过期的可疑IP记录
                expired_keys = []
                for ip in self._suspicious_ips:
                    key = f"security:suspicious_ip:{ip}"
                    if not await self.redis.exists(key):
                        expired_keys.append(ip)
                
                for ip in expired_keys:
                    del self._suspicious_ips[ip]
                
                # 每5分钟清理一次
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"清理过期数据失败: {e}")
                await asyncio.sleep(60)
    
    async def check_request_security(
        self,
        ip_address: str,
        user_agent: str,
        request_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Tuple[SecurityAction, List[SecurityEvent]]:
        """检查请求安全性"""
        events = []
        max_action = SecurityAction.ALLOW
        
        # 1. IP检查
        ip_action, ip_events = await self._check_ip_security(ip_address, user_id)
        events.extend(ip_events)
        max_action = self._get_max_action(max_action, ip_action)
        
        # 2. 速率限制检查
        rate_action, rate_events = await self._check_rate_limit(ip_address, user_id)
        events.extend(rate_events)
        max_action = self._get_max_action(max_action, rate_action)
        
        # 3. 威胁检测
        threat_action, threat_events = await self._detect_threats(request_data, ip_address, user_id)
        events.extend(threat_events)
        max_action = self._get_max_action(max_action, threat_action)
        
        # 4. 设备指纹检查
        if self.config['enable_device_tracking']:
            device_action, device_events = await self._check_device_fingerprint(
                user_agent, ip_address, user_id
            )
            events.extend(device_events)
            max_action = self._get_max_action(max_action, device_action)
        
        # 记录安全事件
        for event in events:
            await self._record_security_event(event)
        
        return max_action, events
    
    async def _check_ip_security(
        self,
        ip_address: str,
        user_id: Optional[str] = None
    ) -> Tuple[SecurityAction, List[SecurityEvent]]:
        """检查IP安全性"""
        events = []
        
        # 检查IP白名单
        if ip_address in self._ip_whitelist:
            return SecurityAction.ALLOW, events
        
        # 检查IP黑名单
        if ip_address in self._ip_blacklist:
            event = SecurityEvent(
                event_type="ip_blacklisted",
                threat_level=ThreatLevel.HIGH,
                source_ip=ip_address,
                user_id=user_id,
                timestamp=datetime.now(),
                details={"reason": "IP在黑名单中"}
            )
            events.append(event)
            return SecurityAction.BLOCK, events
        
        # 检查可疑IP
        if ip_address in self._suspicious_ips:
            suspicious_count = self._suspicious_ips[ip_address]
            if suspicious_count >= self.config['suspicious_ip_threshold']:
                event = SecurityEvent(
                    event_type="suspicious_ip",
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=ip_address,
                    user_id=user_id,
                    timestamp=datetime.now(),
                    details={"suspicious_count": suspicious_count}
                )
                events.append(event)
                return SecurityAction.CAPTCHA, events
        
        # 获取IP地理信息
        ip_info = await self._get_ip_info(ip_address)
        
        # 检查代理/VPN/Tor
        if ip_info and (ip_info.is_proxy or ip_info.is_vpn or ip_info.is_tor):
            event = SecurityEvent(
                event_type="proxy_detected",
                threat_level=ThreatLevel.MEDIUM,
                source_ip=ip_address,
                user_id=user_id,
                timestamp=datetime.now(),
                details={
                    "is_proxy": ip_info.is_proxy,
                    "is_vpn": ip_info.is_vpn,
                    "is_tor": ip_info.is_tor
                }
            )
            events.append(event)
            return SecurityAction.WARN, events
        
        return SecurityAction.ALLOW, events
    
    async def _check_rate_limit(
        self,
        ip_address: str,
        user_id: Optional[str] = None
    ) -> Tuple[SecurityAction, List[SecurityEvent]]:
        """检查速率限制"""
        current_time = datetime.now()
        
        # 记录当前请求
        self._rate_limits[ip_address].append(current_time)
        
        # 计算时间窗口内的请求数
        window_start = current_time - timedelta(seconds=self.config['rate_limit_window'])
        recent_requests = sum(
            1 for req_time in self._rate_limits[ip_address]
            if req_time >= window_start
        )
        
        if recent_requests > self.config['rate_limit_max_requests']:
            event = SecurityEvent(
                event_type="rate_limit_exceeded",
                threat_level=ThreatLevel.MEDIUM,
                source_ip=ip_address,
                user_id=user_id,
                timestamp=current_time,
                details={
                    "requests_count": recent_requests,
                    "limit": self.config['rate_limit_max_requests'],
                    "window_seconds": self.config['rate_limit_window']
                }
            )
            
            # 标记为可疑IP
            self._suspicious_ips[ip_address] += 1
            await self.redis.setex(
                f"security:suspicious_ip:{ip_address}",
                3600,  # 1小时
                self._suspicious_ips[ip_address]
            )
            
            return SecurityAction.BLOCK, [event]
        
        return SecurityAction.ALLOW, []
    
    async def _detect_threats(
        self,
        request_data: Dict[str, Any],
        ip_address: str,
        user_id: Optional[str] = None
    ) -> Tuple[SecurityAction, List[SecurityEvent]]:
        """威胁检测"""
        events = []
        max_threat_level = ThreatLevel.LOW
        
        # 将请求数据转换为字符串进行检测
        request_str = json.dumps(request_data, default=str).lower()
        
        for threat_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(request_str):
                    threat_level = self._get_threat_level_for_type(threat_type)
                    max_threat_level = max(max_threat_level, threat_level, key=lambda x: x.value)
                    
                    event = SecurityEvent(
                        event_type=f"threat_detected_{threat_type}",
                        threat_level=threat_level,
                        source_ip=ip_address,
                        user_id=user_id,
                        timestamp=datetime.now(),
                        details={
                            "threat_type": threat_type,
                            "pattern_matched": pattern.pattern,
                            "request_data": request_data
                        }
                    )
                    events.append(event)
                    break  # 每种威胁类型只记录一次
        
        # 根据威胁级别决定动作
        if max_threat_level == ThreatLevel.CRITICAL:
            return SecurityAction.BLOCK, events
        elif max_threat_level == ThreatLevel.HIGH:
            return SecurityAction.CAPTCHA, events
        elif max_threat_level == ThreatLevel.MEDIUM:
            return SecurityAction.WARN, events
        
        return SecurityAction.ALLOW, events
    
    async def _check_device_fingerprint(
        self,
        user_agent: str,
        ip_address: str,
        user_id: Optional[str] = None
    ) -> Tuple[SecurityAction, List[SecurityEvent]]:
        """检查设备指纹"""
        events = []
        
        # 解析User-Agent
        ua = user_agents.parse(user_agent)
        
        # 生成设备指纹
        fingerprint_data = {
            'user_agent': user_agent,
            'browser': ua.browser.family,
            'browser_version': ua.browser.version_string,
            'os': ua.os.family,
            'os_version': ua.os.version_string,
            'device': ua.device.family
        }
        
        fingerprint_hash = hashlib.sha256(
            json.dumps(fingerprint_data, sort_keys=True).encode()
        ).hexdigest()
        
        # 检查是否为已知设备
        if user_id:
            known_devices = await self._get_user_devices(user_id)
            
            if fingerprint_hash not in known_devices:
                # 新设备检测
                event = SecurityEvent(
                    event_type="new_device_detected",
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=ip_address,
                    user_id=user_id,
                    timestamp=datetime.now(),
                    details={
                        "fingerprint_hash": fingerprint_hash,
                        "device_info": fingerprint_data
                    }
                )
                events.append(event)
                
                # 要求MFA验证
                return SecurityAction.MFA_REQUIRED, events
            else:
                # 更新设备最后使用时间
                await self._update_device_last_seen(user_id, fingerprint_hash)
        
        return SecurityAction.ALLOW, events
    
    async def _get_ip_info(self, ip_address: str) -> Optional[IPInfo]:
        """获取IP信息"""
        try:
            # 尝试从缓存获取
            cache_key = f"security:ip_info:{ip_address}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return IPInfo(**data)
            
            # 使用GeoIP数据库查询
            if self.geoip_reader:
                try:
                    response = self.geoip_reader.city(ip_address)
                    
                    ip_info = IPInfo(
                        ip_address=ip_address,
                        country=response.country.name,
                        city=response.city.name,
                        isp=response.traits.isp if hasattr(response.traits, 'isp') else None,
                        first_seen=datetime.now(),
                        last_seen=datetime.now()
                    )
                    
                    # 缓存结果
                    await self.redis.setex(
                        cache_key,
                        86400,  # 24小时
                        json.dumps(ip_info.__dict__, default=str)
                    )
                    
                    return ip_info
                    
                except geoip2.errors.AddressNotFoundError:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"获取IP信息失败: {e}")
            return None
    
    async def _get_user_devices(self, user_id: str) -> Set[str]:
        """获取用户已知设备"""
        try:
            devices_data = await self.redis.smembers(f"security:user_devices:{user_id}")
            return {device.decode() for device in devices_data}
        except Exception as e:
            logger.error(f"获取用户设备失败: {e}")
            return set()
    
    async def _update_device_last_seen(self, user_id: str, fingerprint_hash: str):
        """更新设备最后使用时间"""
        try:
            # 添加到用户设备列表
            await self.redis.sadd(f"security:user_devices:{user_id}", fingerprint_hash)
            
            # 更新设备信息
            device_key = f"security:device:{fingerprint_hash}"
            await self.redis.hset(device_key, "last_seen", datetime.now().isoformat())
            await self.redis.expire(device_key, 86400 * 90)  # 90天过期
            
        except Exception as e:
            logger.error(f"更新设备信息失败: {e}")
    
    async def _record_security_event(self, event: SecurityEvent):
        """记录安全事件"""
        try:
            # 存储到内存
            self._security_events.append(event)
            
            # 存储到Redis
            event_data = {
                'event_type': event.event_type,
                'threat_level': event.threat_level.value,
                'source_ip': event.source_ip,
                'user_id': event.user_id,
                'timestamp': event.timestamp.isoformat(),
                'details': event.details,
                'action_taken': event.action_taken.value if event.action_taken else None
            }
            
            # 按日期分组存储
            date_key = event.timestamp.strftime('%Y%m%d')
            await self.redis.lpush(f"security:events:{date_key}", json.dumps(event_data))
            await self.redis.expire(f"security:events:{date_key}", 86400 * 30)  # 保留30天
            
            # 如果是高危事件，发送告警
            if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._send_security_alert(event)
                
        except Exception as e:
            logger.error(f"记录安全事件失败: {e}")
    
    async def _send_security_alert(self, event: SecurityEvent):
        """发送安全告警"""
        try:
            # 这里可以集成邮件、短信、Slack等告警渠道
            alert_data = {
                'event_type': event.event_type,
                'threat_level': event.threat_level.value,
                'source_ip': event.source_ip,
                'user_id': event.user_id,
                'timestamp': event.timestamp.isoformat(),
                'details': event.details
            }
            
            # 存储到告警队列
            await self.redis.lpush("security:alerts", json.dumps(alert_data))
            
            logger.warning(f"安全告警: {event.event_type} - {event.threat_level.value} - {event.source_ip}")
            
        except Exception as e:
            logger.error(f"发送安全告警失败: {e}")
    
    def _get_threat_level_for_type(self, threat_type: str) -> ThreatLevel:
        """根据威胁类型获取威胁级别"""
        threat_levels = {
            'sql_injection': ThreatLevel.CRITICAL,
            'xss': ThreatLevel.HIGH,
            'path_traversal': ThreatLevel.HIGH,
            'command_injection': ThreatLevel.CRITICAL
        }
        return threat_levels.get(threat_type, ThreatLevel.MEDIUM)
    
    def _get_max_action(self, action1: SecurityAction, action2: SecurityAction) -> SecurityAction:
        """获取更严格的安全动作"""
        action_priority = {
            SecurityAction.ALLOW: 0,
            SecurityAction.WARN: 1,
            SecurityAction.CAPTCHA: 2,
            SecurityAction.MFA_REQUIRED: 3,
            SecurityAction.BLOCK: 4
        }
        
        if action_priority[action1] >= action_priority[action2]:
            return action1
        return action2
    
    # 管理接口
    async def add_ip_to_whitelist(self, ip_address: str):
        """添加IP到白名单"""
        self._ip_whitelist.add(ip_address)
        await self.redis.sadd("security:ip_whitelist", ip_address)
    
    async def add_ip_to_blacklist(self, ip_address: str):
        """添加IP到黑名单"""
        self._ip_blacklist.add(ip_address)
        await self.redis.sadd("security:ip_blacklist", ip_address)
    
    async def remove_ip_from_whitelist(self, ip_address: str):
        """从白名单移除IP"""
        self._ip_whitelist.discard(ip_address)
        await self.redis.srem("security:ip_whitelist", ip_address)
    
    async def remove_ip_from_blacklist(self, ip_address: str):
        """从黑名单移除IP"""
        self._ip_blacklist.discard(ip_address)
        await self.redis.srem("security:ip_blacklist", ip_address)
    
    async def get_security_summary(
        self,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """获取安全摘要"""
        cutoff_time = datetime.now() - time_range
        
        # 过滤时间范围内的事件
        recent_events = [
            event for event in self._security_events
            if event.timestamp >= cutoff_time
        ]
        
        # 统计各类事件
        event_stats = defaultdict(int)
        threat_level_stats = defaultdict(int)
        
        for event in recent_events:
            event_stats[event.event_type] += 1
            threat_level_stats[event.threat_level.value] += 1
        
        return {
            'time_range_hours': time_range.total_seconds() / 3600,
            'total_events': len(recent_events),
            'event_types': dict(event_stats),
            'threat_levels': dict(threat_level_stats),
            'ip_whitelist_count': len(self._ip_whitelist),
            'ip_blacklist_count': len(self._ip_blacklist),
            'suspicious_ips_count': len(self._suspicious_ips)
        } 