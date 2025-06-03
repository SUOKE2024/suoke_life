#!/usr/bin/env python3
"""
智能体服务注册发现机制
为四智能体（小艾、小克、老克、索儿）提供动态服务发现和能力匹配
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """智能体类型"""
    XIAOAI = "xiaoai"      # 小艾 - 健康监测与预警
    XIAOKE = "xiaoke"      # 小克 - 症状分析与初诊
    LAOKE = "laoke"        # 老克 - 深度诊断与治疗
    SOER = "soer"          # 索儿 - 生活方式与养生

class CapabilityType(Enum):
    """智能体能力类型"""
    HEALTH_MONITORING = "health_monitoring"        # 健康监测
    SYMPTOM_ANALYSIS = "symptom_analysis"          # 症状分析
    DIAGNOSIS = "diagnosis"                        # 诊断
    TREATMENT_PLAN = "treatment_plan"              # 治疗方案
    LIFESTYLE_ADVICE = "lifestyle_advice"          # 生活方式建议
    EMERGENCY_RESPONSE = "emergency_response"      # 应急响应
    DATA_ANALYSIS = "data_analysis"                # 数据分析
    KNOWLEDGE_QUERY = "knowledge_query"            # 知识查询

class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"

@dataclass
class AgentCapability:
    """智能体能力定义"""
    capability_type: CapabilityType
    confidence_level: float  # 置信度 0.0-1.0
    processing_time_ms: int  # 平均处理时间（毫秒）
    success_rate: float      # 成功率 0.0-1.0
    specializations: List[str] = field(default_factory=list)  # 专业领域
    constraints: Dict[str, Any] = field(default_factory=dict)  # 约束条件

@dataclass
class AgentServiceInfo:
    """智能体服务信息"""
    service_id: str
    agent_type: AgentType
    service_name: str
    host: str
    port: int
    version: str
    capabilities: List[AgentCapability]
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_heartbeat: Optional[datetime] = None
    registration_time: Optional[datetime] = None
    load_factor: float = 0.0  # 负载因子 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'service_id': self.service_id,
            'agent_type': self.agent_type.value,
            'service_name': self.service_name,
            'host': self.host,
            'port': self.port,
            'version': self.version,
            'capabilities': [
                {
                    'capability_type': cap.capability_type.value,
                    'confidence_level': cap.confidence_level,
                    'processing_time_ms': cap.processing_time_ms,
                    'success_rate': cap.success_rate,
                    'specializations': cap.specializations,
                    'constraints': cap.constraints
                }
                for cap in self.capabilities
            ],
            'metadata': self.metadata,
            'status': self.status.value,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'registration_time': self.registration_time.isoformat() if self.registration_time else None,
            'load_factor': self.load_factor
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentServiceInfo':
        """从字典创建"""
        capabilities = []
        for cap_data in data.get('capabilities', []):
            capability = AgentCapability(
                capability_type=CapabilityType(cap_data['capability_type']),
                confidence_level=cap_data['confidence_level'],
                processing_time_ms=cap_data['processing_time_ms'],
                success_rate=cap_data['success_rate'],
                specializations=cap_data.get('specializations', []),
                constraints=cap_data.get('constraints', {})
            )
            capabilities.append(capability)
        
        return cls(
            service_id=data['service_id'],
            agent_type=AgentType(data['agent_type']),
            service_name=data['service_name'],
            host=data['host'],
            port=data['port'],
            version=data['version'],
            capabilities=capabilities,
            metadata=data.get('metadata', {}),
            status=ServiceStatus(data['status']),
            last_heartbeat=datetime.fromisoformat(data['last_heartbeat']) if data.get('last_heartbeat') else None,
            registration_time=datetime.fromisoformat(data['registration_time']) if data.get('registration_time') else None,
            load_factor=data.get('load_factor', 0.0)
        )

@dataclass
class ServiceDiscoveryQuery:
    """服务发现查询"""
    required_capabilities: List[CapabilityType]
    agent_types: Optional[List[AgentType]] = None
    min_confidence: float = 0.7
    max_processing_time: Optional[int] = None  # 毫秒
    min_success_rate: float = 0.8
    specializations: Optional[List[str]] = None
    exclude_services: Optional[Set[str]] = None
    max_load_factor: float = 0.8
    prefer_local: bool = False
    locality_preference: Optional[str] = None

class AgentServiceRegistry:
    """智能体服务注册中心"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.service_ttl = 90  # 服务TTL（秒）
        self.cleanup_interval = 60  # 清理间隔（秒）
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Redis键前缀
        self.service_key_prefix = "suoke:agent:service:"
        self.capability_index_prefix = "suoke:agent:capability:"
        self.agent_type_index_prefix = "suoke:agent:type:"
        self.heartbeat_key_prefix = "suoke:agent:heartbeat:"
    
    async def initialize(self):
        """初始化注册中心"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # 启动清理任务
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_services())
            
            logger.info("智能体服务注册中心初始化成功")
            
        except Exception as e:
            logger.error(f"智能体服务注册中心初始化失败: {e}")
            raise
    
    async def close(self):
        """关闭注册中心"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
    
    async def register_service(self, service_info: AgentServiceInfo) -> bool:
        """注册智能体服务"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            # 设置注册时间和心跳时间
            now = datetime.now()
            service_info.registration_time = now
            service_info.last_heartbeat = now
            
            # 生成服务ID（如果未提供）
            if not service_info.service_id:
                service_info.service_id = self._generate_service_id(service_info)
            
            # 存储服务信息
            service_key = f"{self.service_key_prefix}{service_info.service_id}"
            await self.redis_client.setex(
                service_key,
                self.service_ttl,
                json.dumps(service_info.to_dict())
            )
            
            # 更新索引
            await self._update_indexes(service_info)
            
            # 设置心跳
            await self._update_heartbeat(service_info.service_id)
            
            logger.info(f"智能体服务注册成功: {service_info.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"智能体服务注册失败: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """注销智能体服务"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            # 获取服务信息
            service_info = await self.get_service(service_id)
            if not service_info:
                return True  # 服务不存在，视为成功
            
            # 删除服务信息
            service_key = f"{self.service_key_prefix}{service_id}"
            await self.redis_client.delete(service_key)
            
            # 删除索引
            await self._remove_from_indexes(service_info)
            
            # 删除心跳
            heartbeat_key = f"{self.heartbeat_key_prefix}{service_id}"
            await self.redis_client.delete(heartbeat_key)
            
            logger.info(f"智能体服务注销成功: {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"智能体服务注销失败: {e}")
            return False
    
    async def update_heartbeat(self, service_id: str) -> bool:
        """更新服务心跳"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            # 检查服务是否存在
            service_info = await self.get_service(service_id)
            if not service_info:
                return False
            
            # 更新心跳时间
            service_info.last_heartbeat = datetime.now()
            
            # 更新服务信息
            service_key = f"{self.service_key_prefix}{service_id}"
            await self.redis_client.setex(
                service_key,
                self.service_ttl,
                json.dumps(service_info.to_dict())
            )
            
            # 更新心跳记录
            await self._update_heartbeat(service_id)
            
            return True
            
        except Exception as e:
            logger.error(f"更新服务心跳失败: {e}")
            return False
    
    async def get_service(self, service_id: str) -> Optional[AgentServiceInfo]:
        """获取服务信息"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            service_key = f"{self.service_key_prefix}{service_id}"
            data = await self.redis_client.get(service_key)
            
            if not data:
                return None
            
            service_data = json.loads(data)
            return AgentServiceInfo.from_dict(service_data)
            
        except Exception as e:
            logger.error(f"获取服务信息失败: {e}")
            return None
    
    async def discover_services(self, query: ServiceDiscoveryQuery) -> List[AgentServiceInfo]:
        """发现智能体服务"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            # 获取候选服务
            candidates = await self._get_candidate_services(query)
            
            # 过滤和排序
            filtered_services = self._filter_services(candidates, query)
            sorted_services = self._sort_services(filtered_services, query)
            
            return sorted_services
            
        except Exception as e:
            logger.error(f"服务发现失败: {e}")
            return []
    
    async def get_services_by_agent_type(self, agent_type: AgentType) -> List[AgentServiceInfo]:
        """根据智能体类型获取服务"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            index_key = f"{self.agent_type_index_prefix}{agent_type.value}"
            service_ids = await self.redis_client.smembers(index_key)
            
            services = []
            for service_id in service_ids:
                service_info = await self.get_service(service_id.decode())
                if service_info and service_info.status != ServiceStatus.OFFLINE:
                    services.append(service_info)
            
            return services
            
        except Exception as e:
            logger.error(f"根据智能体类型获取服务失败: {e}")
            return []
    
    async def get_services_by_capability(self, capability: CapabilityType) -> List[AgentServiceInfo]:
        """根据能力类型获取服务"""
        try:
            if not self.redis_client:
                raise RuntimeError("注册中心未初始化")
            
            index_key = f"{self.capability_index_prefix}{capability.value}"
            service_ids = await self.redis_client.smembers(index_key)
            
            services = []
            for service_id in service_ids:
                service_info = await self.get_service(service_id.decode())
                if service_info and service_info.status != ServiceStatus.OFFLINE:
                    services.append(service_info)
            
            return services
            
        except Exception as e:
            logger.error(f"根据能力类型获取服务失败: {e}")
            return []
    
    async def update_service_status(self, service_id: str, status: ServiceStatus, load_factor: Optional[float] = None) -> bool:
        """更新服务状态"""
        try:
            service_info = await self.get_service(service_id)
            if not service_info:
                return False
            
            service_info.status = status
            if load_factor is not None:
                service_info.load_factor = load_factor
            
            # 更新服务信息
            service_key = f"{self.service_key_prefix}{service_id}"
            await self.redis_client.setex(
                service_key,
                self.service_ttl,
                json.dumps(service_info.to_dict())
            )
            
            return True
            
        except Exception as e:
            logger.error(f"更新服务状态失败: {e}")
            return False
    
    def _generate_service_id(self, service_info: AgentServiceInfo) -> str:
        """生成服务ID"""
        unique_str = f"{service_info.agent_type.value}:{service_info.host}:{service_info.port}:{service_info.service_name}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
    
    async def _update_indexes(self, service_info: AgentServiceInfo):
        """更新索引"""
        # 智能体类型索引
        agent_type_key = f"{self.agent_type_index_prefix}{service_info.agent_type.value}"
        await self.redis_client.sadd(agent_type_key, service_info.service_id)
        
        # 能力索引
        for capability in service_info.capabilities:
            capability_key = f"{self.capability_index_prefix}{capability.capability_type.value}"
            await self.redis_client.sadd(capability_key, service_info.service_id)
    
    async def _remove_from_indexes(self, service_info: AgentServiceInfo):
        """从索引中移除"""
        # 智能体类型索引
        agent_type_key = f"{self.agent_type_index_prefix}{service_info.agent_type.value}"
        await self.redis_client.srem(agent_type_key, service_info.service_id)
        
        # 能力索引
        for capability in service_info.capabilities:
            capability_key = f"{self.capability_index_prefix}{capability.capability_type.value}"
            await self.redis_client.srem(capability_key, service_info.service_id)
    
    async def _update_heartbeat(self, service_id: str):
        """更新心跳记录"""
        heartbeat_key = f"{self.heartbeat_key_prefix}{service_id}"
        await self.redis_client.setex(heartbeat_key, self.service_ttl, int(time.time()))
    
    async def _get_candidate_services(self, query: ServiceDiscoveryQuery) -> List[AgentServiceInfo]:
        """获取候选服务"""
        candidate_ids = set()
        
        # 根据智能体类型筛选
        if query.agent_types:
            for agent_type in query.agent_types:
                index_key = f"{self.agent_type_index_prefix}{agent_type.value}"
                type_service_ids = await self.redis_client.smembers(index_key)
                candidate_ids.update(sid.decode() for sid in type_service_ids)
        
        # 根据能力筛选
        capability_candidates = set()
        for capability in query.required_capabilities:
            index_key = f"{self.capability_index_prefix}{capability.value}"
            cap_service_ids = await self.redis_client.smembers(index_key)
            cap_candidates = set(sid.decode() for sid in cap_service_ids)
            
            if not capability_candidates:
                capability_candidates = cap_candidates
            else:
                capability_candidates &= cap_candidates
        
        # 取交集
        if query.agent_types and capability_candidates:
            candidate_ids &= capability_candidates
        elif capability_candidates:
            candidate_ids = capability_candidates
        
        # 排除指定服务
        if query.exclude_services:
            candidate_ids -= query.exclude_services
        
        # 获取服务信息
        candidates = []
        for service_id in candidate_ids:
            service_info = await self.get_service(service_id)
            if service_info and service_info.status != ServiceStatus.OFFLINE:
                candidates.append(service_info)
        
        return candidates
    
    def _filter_services(self, services: List[AgentServiceInfo], query: ServiceDiscoveryQuery) -> List[AgentServiceInfo]:
        """过滤服务"""
        filtered = []
        
        for service in services:
            # 检查负载因子
            if service.load_factor > query.max_load_factor:
                continue
            
            # 检查能力要求
            service_capabilities = {cap.capability_type for cap in service.capabilities}
            if not all(req_cap in service_capabilities for req_cap in query.required_capabilities):
                continue
            
            # 检查置信度和成功率
            valid_capabilities = []
            for capability in service.capabilities:
                if capability.capability_type in query.required_capabilities:
                    if (capability.confidence_level >= query.min_confidence and
                        capability.success_rate >= query.min_success_rate):
                        
                        # 检查处理时间
                        if (query.max_processing_time is None or
                            capability.processing_time_ms <= query.max_processing_time):
                            
                            # 检查专业领域
                            if (query.specializations is None or
                                any(spec in capability.specializations for spec in query.specializations)):
                                valid_capabilities.append(capability)
            
            # 确保所有必需能力都满足条件
            valid_capability_types = {cap.capability_type for cap in valid_capabilities}
            if all(req_cap in valid_capability_types for req_cap in query.required_capabilities):
                filtered.append(service)
        
        return filtered
    
    def _sort_services(self, services: List[AgentServiceInfo], query: ServiceDiscoveryQuery) -> List[AgentServiceInfo]:
        """排序服务"""
        def calculate_score(service: AgentServiceInfo) -> float:
            score = 0.0
            
            # 能力匹配度评分
            for capability in service.capabilities:
                if capability.capability_type in query.required_capabilities:
                    # 置信度权重 40%
                    score += capability.confidence_level * 0.4
                    # 成功率权重 30%
                    score += capability.success_rate * 0.3
                    # 处理时间权重 20%（越快越好）
                    if query.max_processing_time:
                        time_score = max(0, 1 - capability.processing_time_ms / query.max_processing_time)
                        score += time_score * 0.2
                    # 专业领域匹配权重 10%
                    if query.specializations:
                        spec_match = len(set(capability.specializations) & set(query.specializations))
                        spec_score = min(1.0, spec_match / len(query.specializations))
                        score += spec_score * 0.1
            
            # 负载因子惩罚
            score *= (1 - service.load_factor * 0.5)
            
            # 服务状态加权
            if service.status == ServiceStatus.HEALTHY:
                score *= 1.0
            elif service.status == ServiceStatus.DEGRADED:
                score *= 0.7
            else:
                score *= 0.3
            
            return score
        
        # 按评分降序排序
        return sorted(services, key=calculate_score, reverse=True)
    
    async def _cleanup_expired_services(self):
        """清理过期服务"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                if not self.redis_client:
                    continue
                
                # 获取所有心跳记录
                heartbeat_pattern = f"{self.heartbeat_key_prefix}*"
                heartbeat_keys = await self.redis_client.keys(heartbeat_pattern)
                
                current_time = int(time.time())
                expired_services = []
                
                for heartbeat_key in heartbeat_keys:
                    last_heartbeat = await self.redis_client.get(heartbeat_key)
                    if last_heartbeat:
                        last_time = int(last_heartbeat)
                        if current_time - last_time > self.service_ttl:
                            # 提取服务ID
                            service_id = heartbeat_key.decode().replace(self.heartbeat_key_prefix, '')
                            expired_services.append(service_id)
                
                # 清理过期服务
                for service_id in expired_services:
                    await self.unregister_service(service_id)
                    logger.info(f"清理过期服务: {service_id}")
                
            except Exception as e:
                logger.error(f"清理过期服务失败: {e}")

# 预定义的智能体能力配置
AGENT_CAPABILITIES = {
    AgentType.XIAOAI: [
        AgentCapability(
            capability_type=CapabilityType.HEALTH_MONITORING,
            confidence_level=0.95,
            processing_time_ms=100,
            success_rate=0.98,
            specializations=["生命体征监测", "异常检测", "预警系统"]
        ),
        AgentCapability(
            capability_type=CapabilityType.DATA_ANALYSIS,
            confidence_level=0.90,
            processing_time_ms=200,
            success_rate=0.95,
            specializations=["健康数据分析", "趋势预测"]
        ),
        AgentCapability(
            capability_type=CapabilityType.EMERGENCY_RESPONSE,
            confidence_level=0.85,
            processing_time_ms=50,
            success_rate=0.92,
            specializations=["紧急情况识别", "快速响应"]
        )
    ],
    AgentType.XIAOKE: [
        AgentCapability(
            capability_type=CapabilityType.SYMPTOM_ANALYSIS,
            confidence_level=0.92,
            processing_time_ms=300,
            success_rate=0.94,
            specializations=["症状识别", "初步诊断", "中医望闻问切"]
        ),
        AgentCapability(
            capability_type=CapabilityType.KNOWLEDGE_QUERY,
            confidence_level=0.88,
            processing_time_ms=150,
            success_rate=0.96,
            specializations=["医学知识库", "症状匹配"]
        )
    ],
    AgentType.LAOKE: [
        AgentCapability(
            capability_type=CapabilityType.DIAGNOSIS,
            confidence_level=0.96,
            processing_time_ms=500,
            success_rate=0.97,
            specializations=["深度诊断", "疾病确诊", "中医辨证论治"]
        ),
        AgentCapability(
            capability_type=CapabilityType.TREATMENT_PLAN,
            confidence_level=0.94,
            processing_time_ms=800,
            success_rate=0.95,
            specializations=["治疗方案制定", "药物配伍", "中医处方"]
        )
    ],
    AgentType.SOER: [
        AgentCapability(
            capability_type=CapabilityType.LIFESTYLE_ADVICE,
            confidence_level=0.90,
            processing_time_ms=250,
            success_rate=0.93,
            specializations=["生活方式指导", "养生建议", "饮食调理"]
        ),
        AgentCapability(
            capability_type=CapabilityType.KNOWLEDGE_QUERY,
            confidence_level=0.85,
            processing_time_ms=180,
            success_rate=0.91,
            specializations=["养生知识", "食疗方案"]
        )
    ]
}

def create_agent_service_info(
    agent_type: AgentType,
    host: str,
    port: int,
    service_name: Optional[str] = None,
    version: str = "1.0.0",
    custom_capabilities: Optional[List[AgentCapability]] = None
) -> AgentServiceInfo:
    """创建智能体服务信息"""
    if not service_name:
        service_name = f"{agent_type.value}-service"
    
    capabilities = custom_capabilities or AGENT_CAPABILITIES.get(agent_type, [])
    
    return AgentServiceInfo(
        service_id="",  # 将在注册时生成
        agent_type=agent_type,
        service_name=service_name,
        host=host,
        port=port,
        version=version,
        capabilities=capabilities,
        metadata={
            "created_at": datetime.now().isoformat(),
            "agent_description": f"{agent_type.value}智能体服务"
        }
    ) 