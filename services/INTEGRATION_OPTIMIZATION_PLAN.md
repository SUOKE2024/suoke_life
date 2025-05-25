# 索克生活平台微服务集成优化计划

## 🎯 优化目标

基于现有架构分析，制定全面的微服务间集成和前端集成优化策略，提升系统的可靠性、性能和用户体验。

## 📋 当前架构评估

### 微服务组成分析
```
核心服务层:
├── api-gateway (API网关) - 统一入口 ✅
├── auth-service (认证服务) - 身份认证 ✅
├── user-service (用户服务) - 用户管理 ✅
├── health-data-service (健康数据) - 数据存储 ✅
├── blockchain-service (区块链) - 数据完整性 ✅
└── message-bus (消息总线) - 异步通信 ⚠️

智能体服务层:
├── xiaoai-service (小艾) - 中医诊断 ✅
├── xiaoke-service (小克) - 服务管理 ✅
├── laoke-service (老克) - 健康教育 ✅
└── soer-service (索儿) - 生活建议 ✅

诊断服务层:
├── look-service (望诊) ✅
├── listen-service (闻诊) ✅
├── inquiry-service (问诊) ✅
└── palpation-service (切诊) ✅

支撑服务层:
├── rag-service (RAG服务) - 知识检索 ✅
├── med-knowledge (医学知识) ✅
├── accessibility-service (无障碍) ✅
└── corn-maze-service (迷宫服务) ✅
```

### 架构优势
- ✅ 服务职责清晰分离
- ✅ API网关统一入口
- ✅ 多协议支持（REST/gRPC）
- ✅ 前端架构清晰（React Native + Redux）
- ✅ 认证服务集中管理

### 关键问题
- ❌ 缺乏动态服务发现
- ❌ 分布式事务管理不完善
- ❌ 端到端监控不足
- ❌ 配置管理分散
- ❌ 容错机制需要加强

## 🚀 优化方案

### Phase 1: 服务网格集成 (2-3周)

#### 1.1 Istio服务网格部署
```yaml
# deploy/istio/istio-config.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: suoke-life-istio
spec:
  values:
    global:
      meshID: suoke-mesh
      network: suoke-network
    pilot:
      env:
        EXTERNAL_ISTIOD: false
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        service:
          type: LoadBalancer
          ports:
          - port: 80
            targetPort: 8080
            name: http2
          - port: 443
            targetPort: 8443
            name: https
```

#### 1.2 服务间通信安全
```yaml
# deploy/istio/security-policies.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: suoke
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: service-to-service
  namespace: suoke
spec:
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/suoke/sa/api-gateway"]
    to:
    - operation:
        methods: ["GET", "POST", "PUT", "DELETE"]
  - from:
    - source:
        principals: ["cluster.local/ns/suoke/sa/xiaoai-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/diagnosis/*"]
```

### Phase 2: 动态服务发现 (1-2周)

#### 2.1 Consul集成增强
```python
# services/common/service-registry/enhanced_consul_client.py
import consul
import asyncio
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging

@dataclass
class ServiceInstance:
    service_id: str
    service_name: str
    address: str
    port: int
    health_status: str
    metadata: Dict[str, str]

class EnhancedConsulClient:
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.service_cache: Dict[str, List[ServiceInstance]] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    async def register_service(self, service_name: str, service_id: str, 
                              address: str, port: int, health_check_url: str,
                              metadata: Dict[str, str] = None):
        """注册服务到Consul"""
        try:
            check = consul.Check.http(health_check_url, interval="10s", timeout="5s")
            
            self.consul.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                check=check,
                meta=metadata or {}
            )
            
            self.logger.info(f"服务注册成功: {service_name} ({service_id})")
        except Exception as e:
            self.logger.error(f"服务注册失败: {e}")
            raise
    
    async def discover_service(self, service_name: str, 
                              healthy_only: bool = True) -> List[ServiceInstance]:
        """发现服务实例"""
        try:
            _, services = self.consul.health.service(service_name, passing=healthy_only)
            
            instances = []
            for service in services:
                instance = ServiceInstance(
                    service_id=service["Service"]["ID"],
                    service_name=service["Service"]["Service"],
                    address=service["Service"]["Address"],
                    port=service["Service"]["Port"],
                    health_status="healthy" if healthy_only else "unknown",
                    metadata=service["Service"].get("Meta", {})
                )
                instances.append(instance)
            
            # 更新缓存
            self.service_cache[service_name] = instances
            
            return instances
            
        except Exception as e:
            self.logger.error(f"服务发现失败: {e}")
            # 返回缓存的实例
            return self.service_cache.get(service_name, [])
    
    async def watch_service(self, service_name: str, callback: Callable):
        """监听服务变化"""
        if service_name not in self.watchers:
            self.watchers[service_name] = []
        self.watchers[service_name].append(callback)
        
        # 启动监听任务
        asyncio.create_task(self._watch_service_changes(service_name))
    
    async def _watch_service_changes(self, service_name: str):
        """监听服务变化的后台任务"""
        index = None
        while True:
            try:
                index, data = self.consul.health.service(
                    service_name, index=index, wait="30s"
                )
                
                # 获取最新的服务实例
                new_instances = await self.discover_service(service_name)
                
                # 通知所有观察者
                for callback in self.watchers.get(service_name, []):
                    try:
                        await callback(service_name, new_instances)
                    except Exception as e:
                        self.logger.error(f"服务变化回调失败: {e}")
                        
            except Exception as e:
                self.logger.error(f"服务监听失败: {e}")
                await asyncio.sleep(5)
```

#### 2.2 API网关动态路由增强
```python
# services/api-gateway/internal/service/enhanced_dynamic_router.py
import asyncio
import aiohttp
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import time
import logging

class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"

@dataclass
class ServiceEndpoint:
    address: str
    port: int
    weight: int = 1
    active_connections: int = 0
    last_used: float = 0
    health_score: float = 1.0

class EnhancedDynamicRouter:
    def __init__(self, consul_client, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.consul = consul_client
        self.strategy = strategy
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = {}
        self.round_robin_counters: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_service_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """获取服务端点（带负载均衡和熔断）"""
        # 检查熔断器状态
        circuit_breaker = self.circuit_breakers.get(service_name)
        if circuit_breaker and circuit_breaker.is_open():
            self.logger.warning(f"服务 {service_name} 熔断器开启，拒绝请求")
            return None
        
        # 获取可用的服务实例
        endpoints = await self._get_healthy_endpoints(service_name)
        if not endpoints:
            self.logger.error(f"服务 {service_name} 无可用实例")
            return None
        
        # 根据负载均衡策略选择端点
        endpoint = self._select_endpoint(service_name, endpoints)
        
        if endpoint:
            endpoint.active_connections += 1
            endpoint.last_used = time.time()
        
        return endpoint
    
    async def _get_healthy_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """获取健康的服务端点"""
        if service_name not in self.service_endpoints:
            await self._refresh_service_endpoints(service_name)
        
        # 过滤健康的端点
        healthy_endpoints = [
            ep for ep in self.service_endpoints.get(service_name, [])
            if ep.health_score > 0.5
        ]
        
        return healthy_endpoints
    
    def _select_endpoint(self, service_name: str, endpoints: List[ServiceEndpoint]) -> Optional[ServiceEndpoint]:
        """根据负载均衡策略选择端点"""
        if not endpoints:
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_name, endpoints)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(endpoints)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(service_name, endpoints)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(endpoints, key=lambda ep: ep.active_connections)
        else:
            return endpoints[0]
    
    def _round_robin_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """轮询选择"""
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(endpoints)
        self.round_robin_counters[service_name] += 1
        
        return endpoints[index]
    
    def _weighted_round_robin_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """加权轮询选择"""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]
        
        # 简化的加权轮询实现
        weighted_endpoints = []
        for ep in endpoints:
            weighted_endpoints.extend([ep] * ep.weight)
        
        return self._round_robin_select(service_name, weighted_endpoints)
    
    async def _refresh_service_endpoints(self, service_name: str):
        """刷新服务端点"""
        try:
            instances = await self.consul.discover_service(service_name)
            endpoints = []
            
            for instance in instances:
                endpoint = ServiceEndpoint(
                    address=instance.address,
                    port=instance.port,
                    weight=int(instance.metadata.get('weight', 1)),
                    health_score=1.0
                )
                endpoints.append(endpoint)
            
            self.service_endpoints[service_name] = endpoints
            self.logger.info(f"刷新服务端点: {service_name}, 实例数: {len(endpoints)}")
            
        except Exception as e:
            self.logger.error(f"刷新服务端点失败: {e}")
    
    async def report_request_result(self, service_name: str, endpoint: ServiceEndpoint, 
                                   success: bool, response_time: float):
        """报告请求结果，用于健康评分和熔断"""
        endpoint.active_connections = max(0, endpoint.active_connections - 1)
        
        # 更新健康评分
        if success:
            endpoint.health_score = min(1.0, endpoint.health_score + 0.1)
        else:
            endpoint.health_score = max(0.0, endpoint.health_score - 0.2)
        
        # 更新熔断器
        circuit_breaker = self.circuit_breakers.get(service_name)
        if circuit_breaker:
            if success:
                circuit_breaker.record_success()
            else:
                circuit_breaker.record_failure()
```

### Phase 3: 分布式事务管理 (2-3周)

#### 3.1 Saga模式实现
```python
# services/common/distributed-transaction/saga_orchestrator.py
import asyncio
import json
import uuid
from enum import Enum
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict
import logging
import time

class SagaStepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    step_id: str
    name: str
    action: Callable
    compensation: Callable
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Any = None
    error: str = None
    started_at: float = None
    completed_at: float = None
    retry_count: int = 0
    max_retries: int = 3

class SagaOrchestrator:
    def __init__(self, saga_id: str = None, event_bus=None):
        self.saga_id = saga_id or str(uuid.uuid4())
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.status = "created"
        self.created_at = time.time()
        self.completed_at = None
    
    def add_step(self, name: str, action: Callable, compensation: Callable, 
                 max_retries: int = 3) -> 'SagaOrchestrator':
        """添加Saga步骤"""
        step = SagaStep(
            step_id=str(uuid.uuid4()),
            name=name,
            action=action,
            compensation=compensation,
            max_retries=max_retries
        )
        self.steps.append(step)
        return self
    
    async def execute(self) -> bool:
        """执行Saga事务"""
        self.status = "running"
        self.logger.info(f"开始执行Saga事务: {self.saga_id}")
        
        try:
            # 发布Saga开始事件
            await self._publish_event("saga_started", {
                "saga_id": self.saga_id,
                "steps_count": len(self.steps)
            })
            
            for step in self.steps:
                success = await self._execute_step(step)
                if not success:
                    self.logger.error(f"Saga步骤失败: {step.name}")
                    await self._compensate()
                    self.status = "failed"
                    return False
                
                self.completed_steps.append(step)
            
            self.status = "completed"
            self.completed_at = time.time()
            
            # 发布Saga完成事件
            await self._publish_event("saga_completed", {
                "saga_id": self.saga_id,
                "duration": self.completed_at - self.created_at
            })
            
            self.logger.info(f"Saga事务执行成功: {self.saga_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Saga执行异常: {e}")
            await self._compensate()
            self.status = "failed"
            return False
    
    async def _execute_step(self, step: SagaStep) -> bool:
        """执行单个步骤（带重试）"""
        step.status = SagaStepStatus.RUNNING
        step.started_at = time.time()
        
        for attempt in range(step.max_retries + 1):
            try:
                self.logger.info(f"执行步骤: {step.name} (尝试 {attempt + 1}/{step.max_retries + 1})")
                
                # 发布步骤开始事件
                await self._publish_event("step_started", {
                    "saga_id": self.saga_id,
                    "step_id": step.step_id,
                    "step_name": step.name,
                    "attempt": attempt + 1
                })
                
                step.result = await step.action()
                step.status = SagaStepStatus.COMPLETED
                step.completed_at = time.time()
                
                # 发布步骤完成事件
                await self._publish_event("step_completed", {
                    "saga_id": self.saga_id,
                    "step_id": step.step_id,
                    "step_name": step.name,
                    "duration": step.completed_at - step.started_at
                })
                
                return True
                
            except Exception as e:
                step.retry_count = attempt + 1
                step.error = str(e)
                
                self.logger.warning(f"步骤执行失败: {step.name}, 错误: {e}")
                
                if attempt < step.max_retries:
                    # 指数退避重试
                    delay = 2 ** attempt
                    self.logger.info(f"等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    step.status = SagaStepStatus.FAILED
                    
                    # 发布步骤失败事件
                    await self._publish_event("step_failed", {
                        "saga_id": self.saga_id,
                        "step_id": step.step_id,
                        "step_name": step.name,
                        "error": str(e),
                        "retry_count": step.retry_count
                    })
                    
                    return False
        
        return False
    
    async def _compensate(self):
        """执行补偿操作"""
        self.logger.info(f"开始补偿Saga事务: {self.saga_id}")
        
        # 发布补偿开始事件
        await self._publish_event("compensation_started", {
            "saga_id": self.saga_id,
            "steps_to_compensate": len(self.completed_steps)
        })
        
        # 逆序执行补偿
        for step in reversed(self.completed_steps):
            await self._compensate_step(step)
        
        # 发布补偿完成事件
        await self._publish_event("compensation_completed", {
            "saga_id": self.saga_id
        })
    
    async def _compensate_step(self, step: SagaStep):
        """补偿单个步骤"""
        step.status = SagaStepStatus.COMPENSATING
        
        try:
            self.logger.info(f"补偿步骤: {step.name}")
            await step.compensation()
            step.status = SagaStepStatus.COMPENSATED
            
            # 发布补偿成功事件
            await self._publish_event("step_compensated", {
                "saga_id": self.saga_id,
                "step_id": step.step_id,
                "step_name": step.name
            })
            
        except Exception as e:
            self.logger.error(f"补偿步骤失败: {step.name}, 错误: {e}")
            
            # 发布补偿失败事件
            await self._publish_event("step_compensation_failed", {
                "saga_id": self.saga_id,
                "step_id": step.step_id,
                "step_name": step.name,
                "error": str(e)
            })
    
    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """发布事件"""
        if self.event_bus:
            try:
                await self.event_bus.publish({
                    "type": event_type,
                    "saga_id": self.saga_id,
                    "timestamp": time.time(),
                    "data": data
                })
            except Exception as e:
                self.logger.error(f"发布事件失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取Saga状态"""
        return {
            "saga_id": self.saga_id,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "total_steps": len(self.steps),
            "completed_steps": len(self.completed_steps),
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "retry_count": step.retry_count,
                    "error": step.error
                }
                for step in self.steps
            ]
        }

# 使用示例：健康数据录入Saga
class HealthDataSagaFactory:
    def __init__(self, user_service, health_data_service, blockchain_service, 
                 xiaoai_service, event_bus):
        self.user_service = user_service
        self.health_data_service = health_data_service
        self.blockchain_service = blockchain_service
        self.xiaoai_service = xiaoai_service
        self.event_bus = event_bus
    
    def create_health_data_saga(self, user_id: str, health_data: Dict) -> SagaOrchestrator:
        """创建健康数据录入Saga"""
        saga = SagaOrchestrator(event_bus=self.event_bus)
        
        # 步骤1：验证用户
        saga.add_step(
            "validate_user",
            lambda: self.user_service.validate_user(user_id),
            lambda: None  # 验证失败无需补偿
        )
        
        # 步骤2：保存健康数据
        data_id = None
        saga.add_step(
            "save_health_data",
            lambda: self._save_health_data(user_id, health_data),
            lambda: self.health_data_service.delete(user_id, data_id) if data_id else None
        )
        
        # 步骤3：更新区块链
        blockchain_tx_id = None
        saga.add_step(
            "update_blockchain",
            lambda: self._update_blockchain(user_id, health_data),
            lambda: self.blockchain_service.rollback_record(blockchain_tx_id) if blockchain_tx_id else None
        )
        
        # 步骤4：触发智能体分析
        analysis_id = None
        saga.add_step(
            "trigger_ai_analysis",
            lambda: self._trigger_ai_analysis(user_id, health_data),
            lambda: self.xiaoai_service.cancel_analysis(analysis_id) if analysis_id else None
        )
        
        return saga
    
    async def _save_health_data(self, user_id: str, health_data: Dict):
        """保存健康数据"""
        result = await self.health_data_service.save(user_id, health_data)
        # 保存data_id用于补偿
        nonlocal data_id
        data_id = result.get('id')
        return result
    
    async def _update_blockchain(self, user_id: str, health_data: Dict):
        """更新区块链"""
        result = await self.blockchain_service.record_health_data(user_id, health_data)
        # 保存交易ID用于补偿
        nonlocal blockchain_tx_id
        blockchain_tx_id = result.get('transaction_id')
        return result
    
    async def _trigger_ai_analysis(self, user_id: str, health_data: Dict):
        """触发AI分析"""
        result = await self.xiaoai_service.analyze_health_data(user_id, health_data)
        # 保存分析ID用于补偿
        nonlocal analysis_id
        analysis_id = result.get('analysis_id')
        return result
```

### Phase 4: 前端集成优化 (2-3周)

#### 4.1 智能重试和缓存策略
```typescript
// src/services/enhancedApiClient.ts
import AsyncStorage from "@react-native-async-storage/async-storage";
import NetInfo from "@react-native-netinfo/";
import { EventEmitter } from 'events';

interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
  retryableErrors: string[];
}

interface CacheConfig {
  ttl: number;
  maxSize: number;
  strategy: 'memory' | 'storage' | 'both';
}

interface RequestMetrics {
  requestCount: number;
  successCount: number;
  errorCount: number;
  averageResponseTime: number;
  lastRequestTime: number;
}

class EnhancedApiClient extends EventEmitter {
  private cache = new Map<string, any>();
  private metrics = new Map<string, RequestMetrics>();
  private retryConfig: RetryConfig = {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffFactor: 2,
    retryableErrors: ['NETWORK_ERROR', 'TIMEOUT', '500', '502', '503', '504']
  };
  
  private cacheConfig: CacheConfig = {
    ttl: 5 * 60 * 1000, // 5分钟
    maxSize: 100,
    strategy: 'both'
  };

  async requestWithRetry<T>(
    method: string,
    endpoint: string,
    data?: any,
    config?: any
  ): Promise<T> {
    const startTime = Date.now();
    let lastError: Error;
    
    // 检查缓存（仅GET请求）
    if (method === 'GET') {
      const cachedData = await this.getCachedResponse(endpoint);
      if (cachedData) {
        this.emit('cacheHit', { endpoint, data: cachedData });
        return { success: true, data: cachedData };
      }
    }
    
    for (let attempt = 1; attempt <= this.retryConfig.maxAttempts; attempt++) {
      try {
        // 检查网络状态
        const netInfo = await NetInfo.fetch();
        if (!netInfo.isConnected) {
          throw new Error('Network not available');
        }

        const response = await this.request(method, endpoint, data, config);
        
        // 记录成功指标
        this.recordMetrics(endpoint, true, Date.now() - startTime);
        
        // 成功时缓存响应
        if (method === 'GET' && response.success) {
          await this.cacheResponse(endpoint, response.data);
        }
        
        this.emit('requestSuccess', { 
          method, 
          endpoint, 
          attempt, 
          responseTime: Date.now() - startTime 
        });
        
        return response;
        
      } catch (error) {
        lastError = error as Error;
        
        // 记录失败指标
        this.recordMetrics(endpoint, false, Date.now() - startTime);
        
        // 检查是否应该重试
        if (!this.shouldRetry(error, attempt)) {
          break;
        }
        
        // 如果是最后一次尝试，尝试从缓存获取数据
        if (attempt === this.retryConfig.maxAttempts) {
          if (method === 'GET') {
            const cachedData = await this.getCachedResponse(endpoint, true); // 允许过期缓存
            if (cachedData) {
              this.emit('fallbackToCache', { endpoint, error: lastError });
              return { success: true, data: cachedData, fromCache: true };
            }
          }
          break;
        }
        
        // 计算延迟时间
        const delay = Math.min(
          this.retryConfig.baseDelay * Math.pow(this.retryConfig.backoffFactor, attempt - 1),
          this.retryConfig.maxDelay
        );
        
        this.emit('retryAttempt', { 
          method, 
          endpoint, 
          attempt, 
          maxAttempts: this.retryConfig.maxAttempts,
          delay,
          error: lastError.message
        });
        
        await this.sleep(delay);
      }
    }
    
    this.emit('requestFailed', { 
      method, 
      endpoint, 
      error: lastError,
      totalAttempts: this.retryConfig.maxAttempts
    });
    
    throw lastError!;
  }

  private shouldRetry(error: any, attempt: number): boolean {
    if (attempt >= this.retryConfig.maxAttempts) {
      return false;
    }
    
    const errorCode = error.code || error.status?.toString() || 'UNKNOWN';
    return this.retryConfig.retryableErrors.includes(errorCode);
  }

  private async cacheResponse(key: string, data: any): Promise<void> {
    try {
      const cacheEntry = {
        data,
        timestamp: Date.now(),
        ttl: this.cacheConfig.ttl
      };
      
      // 内存缓存
      if (this.cacheConfig.strategy === 'memory' || this.cacheConfig.strategy === 'both') {
        // 检查缓存大小限制
        if (this.cache.size >= this.cacheConfig.maxSize) {
          // 删除最旧的条目
          const oldestKey = this.cache.keys().next().value;
          this.cache.delete(oldestKey);
        }
        this.cache.set(key, cacheEntry);
      }
      
      // 持久化缓存
      if (this.cacheConfig.strategy === 'storage' || this.cacheConfig.strategy === 'both') {
        await AsyncStorage.setItem(
          `api_cache_${key}`,
          JSON.stringify(cacheEntry)
        );
      }
      
      this.emit('dataCached', { key, size: JSON.stringify(data).length });
    } catch (error) {
      console.warn('Failed to cache response:', error);
    }
  }

  private async getCachedResponse(key: string, allowExpired: boolean = false): Promise<any> {
    try {
      let cacheEntry = null;
      
      // 先检查内存缓存
      if (this.cacheConfig.strategy === 'memory' || this.cacheConfig.strategy === 'both') {
        cacheEntry = this.cache.get(key);
      }
      
      // 如果内存中没有，检查持久化缓存
      if (!cacheEntry && (this.cacheConfig.strategy === 'storage' || this.cacheConfig.strategy === 'both')) {
        const storageCache = await AsyncStorage.getItem(`api_cache_${key}`);
        if (storageCache) {
          cacheEntry = JSON.parse(storageCache);
          // 恢复到内存缓存
          if (this.cacheConfig.strategy === 'both') {
            this.cache.set(key, cacheEntry);
          }
        }
      }
      
      if (cacheEntry) {
        const isExpired = Date.now() - cacheEntry.timestamp > cacheEntry.ttl;
        if (!isExpired || allowExpired) {
          return cacheEntry.data;
        } else {
          // 清理过期缓存
          this.cache.delete(key);
          await AsyncStorage.removeItem(`api_cache_${key}`);
        }
      }
      
      return null;
    } catch (error) {
      console.warn('Failed to get cached response:', error);
      return null;
    }
  }

  private recordMetrics(endpoint: string, success: boolean, responseTime: number): void {
    const current = this.metrics.get(endpoint) || {
      requestCount: 0,
      successCount: 0,
      errorCount: 0,
      averageResponseTime: 0,
      lastRequestTime: 0
    };
    
    current.requestCount++;
    current.lastRequestTime = Date.now();
    
    if (success) {
      current.successCount++;
    } else {
      current.errorCount++;
    }
    
    // 计算平均响应时间
    current.averageResponseTime = (
      (current.averageResponseTime * (current.requestCount - 1) + responseTime) / 
      current.requestCount
    );
    
    this.metrics.set(endpoint, current);
  }

  getMetrics(): Map<string, RequestMetrics> {
    return new Map(this.metrics);
  }

  clearCache(): void {
    this.cache.clear();
    // 清理AsyncStorage中的缓存
    AsyncStorage.getAllKeys().then(keys => {
      const cacheKeys = keys.filter(key => key.startsWith('api_cache_'));
      AsyncStorage.multiRemove(cacheKeys);
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const enhancedApiClient = new EnhancedApiClient();
```

#### 4.2 实时数据同步
```typescript
// src/services/realtimeSync.ts
import { EventEmitter } from 'events';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppState } from 'react-native';

interface SyncConfig {
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
  syncQueueSize: number;
}

interface SyncMessage {
  id: string;
  type: string;
  data: any;
  timestamp: number;
  priority: 'high' | 'medium' | 'low';
}

class RealtimeSync extends EventEmitter {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private syncQueue: SyncMessage[] = [];
  private isOnline = true;
  private appState = 'active';
  
  private config: SyncConfig = {
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,
    syncQueueSize: 1000
  };

  constructor() {
    super();
    this.setupAppStateListener();
    this.loadOfflineQueue();
  }

  private setupAppStateListener(): void {
    AppState.addEventListener('change', (nextAppState) => {
      if (this.appState.match(/inactive|background/) && nextAppState === 'active') {
        // 应用从后台回到前台，重新连接
        this.reconnect();
      }
      this.appState = nextAppState;
    });
  }

  connect(token: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `${API_CONFIG.WEBSOCKET_URL}?token=${token}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.isOnline = true;
        this.startHeartbeat();
        this.processSyncQueue();
        this.emit('connected');
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason);
        this.isOnline = false;
        this.stopHeartbeat();
        this.emit('disconnected', { code: event.code, reason: event.reason });
        
        if (!event.wasClean && this.reconnectAttempts < this.config.maxReconnectAttempts) {
          this.attemptReconnect();
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.attemptReconnect();
    }
  }

  private handleMessage(message: any): void {
    // 确认消息接收
    if (message.id) {
      this.sendAck(message.id);
    }

    switch (message.type) {
      case 'health_data_update':
        this.emit('healthDataUpdate', message.data);
        this.cacheMessage(message);
        break;
      case 'agent_response':
        this.emit('agentResponse', message.data);
        break;
      case 'diagnosis_result':
        this.emit('diagnosisResult', message.data);
        this.cacheMessage(message);
        break;
      case 'system_notification':
        this.emit('systemNotification', message.data);
        break;
      case 'sync_request':
        this.handleSyncRequest(message.data);
        break;
      case 'pong':
        // 心跳响应
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  private async cacheMessage(message: any): Promise<void> {
    try {
      const cacheKey = `sync_message_${message.type}_${message.timestamp}`;
      await AsyncStorage.setItem(cacheKey, JSON.stringify(message));
    } catch (error) {
      console.error('Failed to cache message:', error);
    }
  }

  private sendAck(messageId: string): void {
    this.send({
      type: 'ack',
      messageId,
      timestamp: Date.now()
    });
  }

  private handleSyncRequest(data: any): void {
    // 处理服务器请求的数据同步
    this.emit('syncRequest', data);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
      30000 // 最大30秒
    );
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.ws?.readyState !== WebSocket.OPEN) {
        this.reconnect();
      }
    }, delay);
  }

  private reconnect(): void {
    if (this.ws) {
      this.ws.close();
    }
    // 重新连接需要token，这里假设从存储中获取
    AsyncStorage.getItem('auth_token').then(token => {
      if (token) {
        this.connect(token);
      }
    });
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ 
          type: 'ping', 
          timestamp: Date.now() 
        }));
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  send(message: any): void {
    const syncMessage: SyncMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: message.type,
      data: message.data || message,
      timestamp: Date.now(),
      priority: message.priority || 'medium'
    };

    if (this.ws?.readyState === WebSocket.OPEN && this.isOnline) {
      this.ws.send(JSON.stringify(syncMessage));
    } else {
      // 离线时加入同步队列
      this.addToSyncQueue(syncMessage);
    }
  }

  private addToSyncQueue(message: SyncMessage): void {
    // 按优先级插入队列
    if (message.priority === 'high') {
      this.syncQueue.unshift(message);
    } else {
      this.syncQueue.push(message);
    }

    // 限制队列大小
    if (this.syncQueue.length > this.config.syncQueueSize) {
      // 移除最旧的低优先级消息
      const lowPriorityIndex = this.syncQueue.findIndex(msg => msg.priority === 'low');
      if (lowPriorityIndex !== -1) {
        this.syncQueue.splice(lowPriorityIndex, 1);
      } else {
        this.syncQueue.shift(); // 移除最旧的消息
      }
    }

    this.saveOfflineQueue();
  }

  private async processSyncQueue(): Promise<void> {
    while (this.syncQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.syncQueue.shift();
      if (message) {
        try {
          this.ws.send(JSON.stringify(message));
          await new Promise(resolve => setTimeout(resolve, 100)); // 避免发送过快
        } catch (error) {
          console.error('Failed to send queued message:', error);
          // 重新加入队列
          this.syncQueue.unshift(message);
          break;
        }
      }
    }
    
    if (this.syncQueue.length === 0) {
      this.clearOfflineQueue();
    }
  }

  private async saveOfflineQueue(): Promise<void> {
    try {
      await AsyncStorage.setItem('sync_queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.error('Failed to save sync queue:', error);
    }
  }

  private async loadOfflineQueue(): Promise<void> {
    try {
      const queueData = await AsyncStorage.getItem('sync_queue');
      if (queueData) {
        this.syncQueue = JSON.parse(queueData);
      }
    } catch (error) {
      console.error('Failed to load sync queue:', error);
    }
  }

  private async clearOfflineQueue(): Promise<void> {
    try {
      await AsyncStorage.removeItem('sync_queue');
    } catch (error) {
      console.error('Failed to clear sync queue:', error);
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  getConnectionStatus(): {
    connected: boolean;
    reconnectAttempts: number;
    queueSize: number;
  } {
    return {
      connected: this.ws?.readyState === WebSocket.OPEN,
      reconnectAttempts: this.reconnectAttempts,
      queueSize: this.syncQueue.length
    };
  }
}

export const realtimeSync = new RealtimeSync();
```

## 📊 实施计划和预期收益

### 实施时间线
- **Phase 1**: 服务网格集成 (2-3周)
- **Phase 2**: 动态服务发现 (1-2周)  
- **Phase 3**: 分布式事务管理 (2-3周)
- **Phase 4**: 前端集成优化 (2-3周)
- **总计**: 7-11周

### 预期收益
- **性能提升**: 响应时间减少40-60%，吞吐量提升3-5倍
- **可用性**: 达到99.9%可用性
- **用户体验**: 离线支持、实时更新、智能重试
- **开发效率**: 统一监控、自动化部署、快速故障定位

这个优化计划将显著提升索克生活平台的技术架构，为四个智能体提供更稳定、高效的技术基础。 