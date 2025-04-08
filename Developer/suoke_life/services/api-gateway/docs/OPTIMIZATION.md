# API网关优化实现说明

本文档描述了索克生活API网关的优化实现，包括新增的各项高级功能和服务质量改进。

## 目录

1. [JWT认证优化](#1-jwt认证优化)
2. [请求限流](#2-请求限流)
3. [请求重试](#3-请求重试)
4. [响应缓存](#4-响应缓存)
5. [服务发现集成](#5-服务发现集成)
6. [配置文件扩展](#6-配置文件扩展)
7. [使用指南](#7-使用指南)

## 1. JWT认证优化

### 实现内容

- 创建了专用的认证服务客户端，通过HTTP请求与认证服务通信
- 实现令牌验证的完整流程，包括错误处理和状态码管理
- 提取用户信息并添加到请求上下文和请求头中
- 支持安全的公开路径配置

### 文件位置

- `internal/middleware/auth.go`

### 主要接口

```go
// JWT 中间件验证认证令牌
func JWT(cfg config.ServiceConfig, log logger.Logger) gin.HandlerFunc

// 认证服务客户端
type AuthService struct {
    // ...
}

// 验证令牌
func (s *AuthService) VerifyToken(token string) (*TokenValidationResponse, error)
```

## 2. 请求限流

### 实现内容

- 基于滑动窗口的限流算法
- 支持按客户端IP进行限流
- 支持burst流量处理
- 阻止过于频繁的请求并返回适当的429状态码
- 提供标准的限流头部信息
- 自动清理过期的限流数据

### 文件位置

- `internal/middleware/ratelimit.go`

### 主要接口

```go
// RateLimit 中间件实现请求限流
func RateLimit(limit int, window time.Duration) gin.HandlerFunc

// RateLimiter 限流器
type RateLimiter struct {
    // ...
}
```

## 3. 请求重试

### 实现内容

- 根据配置支持请求自动重试
- 指数退避算法和随机抖动，避免雪崩效应
- 只对服务端错误(5xx)进行重试，客户端错误(4xx)不重试
- 重试过程中保持请求体完整性
- 详细的重试日志记录

### 文件位置

- `internal/proxy/proxy.go`

### 主要方法

```go
// 发送请求，支持重试
func (p *ServiceProxy) sendRequestWithRetries(req *http.Request, originalBody []byte) (*http.Response, error)
```

## 4. 响应缓存

### 实现内容

- 实现HTTP响应缓存机制
- 支持按路径和方法进行缓存控制
- 缓存键生成算法考虑请求路径、查询参数和相关头部
- 只缓存GET请求和成功响应
- 自动清理过期缓存和内存管理
- 缓存命中/未命中头部

### 文件位置

- `internal/middleware/cache.go` 

### 主要接口

```go
// Cache 中间件实现响应缓存
func Cache(ttl time.Duration, maxSize int, log logger.Logger) gin.HandlerFunc

// CacheManager 缓存管理器
type CacheManager struct {
    // ...
}
```

## 5. 服务发现集成

### 实现内容

- 抽象服务发现接口，支持不同的服务发现后端
- 实现基于HTTP服务注册中心的服务发现
- 支持服务端点定期刷新
- 负载均衡策略（简单随机选择）
- 从静态配置到服务发现的平滑过渡
- 失败时降级到静态配置

### 文件位置

- `internal/discovery/discovery.go`
- `internal/proxy/discovery_proxy.go`

### 主要接口

```go
// ServiceDiscovery 服务发现接口
type ServiceDiscovery interface {
    GetService(name string) ([]string, error)
    GetAllServices() (map[string]ServiceInfo, error)
    Start() error
    Stop()
}

// DiscoveryProxyManager 扩展ProxyManager，集成服务发现
type DiscoveryProxyManager struct {
    // ...
}
```

## 6. 配置文件扩展

### 实现内容

- 扩展配置结构，支持所有新增功能
- 默认配置安全可用
- 为所有新功能提供环境变量支持
- 详细的配置示例

### 文件位置

- `internal/config/config.go`
- `internal/configs/config-example.yaml`

### 新增配置部分

```yaml
cache:
  enabled: true
  default_ttl: 300
  max_cache_size: 1000
  exclude_paths:
    - "/health"
    - "/metrics"

rate_limit:
  enabled: true
  requests_per_minute: 100
  burst_size: 20
  time_window: 60

service_discovery:
  enabled: false
  url: "http://localhost:8500"
  refresh_interval: 300
  timeout: 5
  fallback_to_static: true

circuit_breaker:
  enabled: true
  max_failures: 5
  timeout: 10
  reset_timeout: 60
```

## 7. 使用指南

### 启用功能

所有新功能默认都是启用的，但可以通过配置文件或环境变量个别禁用或启用。

### 环境变量

以下是一些关键环境变量：

```bash
# 限流
SUOKE_GATEWAY_RATE_LIMIT_ENABLED=true
SUOKE_GATEWAY_RATE_LIMIT_REQUESTS_PER_MINUTE=100

# 缓存
SUOKE_GATEWAY_CACHE_ENABLED=true
SUOKE_GATEWAY_CACHE_DEFAULT_TTL=300

# 服务发现
SUOKE_GATEWAY_SERVICE_DISCOVERY_ENABLED=false
SUOKE_GATEWAY_SERVICE_DISCOVERY_URL="http://consul:8500"
```

### 健康检查

健康检查端点现在包含更详细的信息，包括各个特性的启用状态：

```json
{
  "status": "ok",
  "time": "2023-04-08T16:45:30Z",
  "version": "v1.0.0",
  "service_discovery": false,
  "cache_enabled": true,
  "rate_limit_enabled": true
}
```