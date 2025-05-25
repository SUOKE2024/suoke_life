# 服务注册中心配置指南

## 概述

索克生活平台采用服务注册中心来管理微服务的动态发现和健康监控。

## 推荐方案

### 1. Consul 集成

```yaml
# consul-config.yaml
service:
  name: ${SERVICE_NAME}
  id: ${SERVICE_ID}
  address: ${SERVICE_HOST}
  port: ${SERVICE_PORT}
  tags:
    - version=${SERVICE_VERSION}
    - protocol=grpc
  check:
    grpc: ${SERVICE_HOST}:${SERVICE_PORT}
    interval: 10s
    timeout: 5s
```

### 2. 服务注册代码示例

```python
import consul
from typing import Dict, Any

class ServiceRegistry:
    def __init__(self, consul_host: str, consul_port: int):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
    
    async def register_service(self, service_config: Dict[str, Any]):
        """注册服务到 Consul"""
        return self.consul.agent.service.register(
            name=service_config['name'],
            service_id=service_config['id'],
            address=service_config['address'],
            port=service_config['port'],
            tags=service_config.get('tags', []),
            check=service_config.get('check')
        )
    
    async def deregister_service(self, service_id: str):
        """注销服务"""
        return self.consul.agent.service.deregister(service_id)
```

### 3. 健康检查实现

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    """服务健康检查端点"""
    health_status = await check_service_health()
    
    if health_status['healthy']:
        return JSONResponse(
            content={"status": "healthy", "details": health_status},
            status_code=200
        )
    else:
        return JSONResponse(
            content={"status": "unhealthy", "details": health_status},
            status_code=503
        )
```

## 迁移计划

1. **第一阶段**：在测试环境部署 Consul 集群
2. **第二阶段**：逐个服务接入服务注册
3. **第三阶段**：启用服务发现和健康检查
4. **第四阶段**：生产环境部署 