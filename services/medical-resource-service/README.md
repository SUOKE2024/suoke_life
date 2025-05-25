# 医疗资源微服务 (Medical Resource Service)

医疗资源微服务是索克生活平台的核心服务之一，由智能体小克（xiaoke）管理协调，专门负责医疗资源的统一管理、调度和分配。该服务整合了传统中医和现代医学资源，为用户提供个性化的医疗服务匹配和预约管理。

## 服务概述

### 核心职责

1. **医疗资源统一管理**
   - 中医师资源管理（名老中医、中医专家等）
   - 现代医疗机构资源管理（医院、诊所、体检中心等）
   - 医疗设备资源管理（检测设备、治疗设备等）
   - 药材资源管理（道地药材、中药饮片等）
   - 优质农产品资源管理（药食同源等）

2. **智能资源调度**
   - 基于用户体质和病症的资源匹配
   - 实时资源可用性监控
   - 智能预约排程算法
   - 资源负载均衡

3. **个性化医疗服务**
   - 中医辨证论治服务匹配
   - 现代医学检查项目推荐
   - 综合治疗方案制定
   - 康复资源配置

4. **质量管控**
   - 医疗资源质量评估
   - 服务效果跟踪
   - 用户满意度监控
   - 资源优化建议

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    索克生活APP前端                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   API网关                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                医疗资源微服务                                │
│  ┌─────────────────┬─────────────────┬─────────────────┐    │
│  │   小克智能体     │   资源管理器     │   调度引擎       │    │
│  │   (xiaoke)     │                │                │    │
│  └─────────────────┴─────────────────┴─────────────────┘    │
│  ┌─────────────────┬─────────────────┬─────────────────┐    │
│  │   预约管理器     │   质量监控器     │   数据分析器     │    │
│  └─────────────────┴─────────────────┴─────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   数据层                                    │
│  ┌─────────────────┬─────────────────┬─────────────────┐    │
│  │   PostgreSQL    │     Redis       │    MongoDB      │    │
│  │   (关系数据)     │   (缓存/会话)    │   (文档数据)     │    │
│  └─────────────────┴─────────────────┴─────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  外部集成                                   │
│  ┌─────────────────┬─────────────────┬─────────────────┐    │
│  │   医院HIS系统    │   支付服务       │   消息推送       │    │
│  └─────────────────┴─────────────────┴─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 核心模块

#### 1. 智能体模块 (Agent)
- **xiaoke_agent.py**: 小克智能体核心逻辑
- **decision_engine.py**: 决策引擎，基于用户需求和资源状态做出最优决策
- **learning_module.py**: 机器学习模块，持续优化资源配置策略

#### 2. 资源管理模块 (Resource Management)
- **resource_manager.py**: 资源管理器，统一管理各类医疗资源
- **doctor_manager.py**: 医生资源管理
- **facility_manager.py**: 医疗机构管理
- **equipment_manager.py**: 设备资源管理
- **medicine_manager.py**: 药材资源管理

#### 3. 调度引擎模块 (Scheduling Engine)
- **scheduler.py**: 核心调度算法
- **appointment_manager.py**: 预约管理
- **resource_allocator.py**: 资源分配器
- **load_balancer.py**: 负载均衡器

#### 4. 服务层模块 (Service Layer)
- **medical_service.py**: 医疗服务业务逻辑
- **recommendation_service.py**: 推荐服务
- **notification_service.py**: 通知服务
- **analytics_service.py**: 数据分析服务

#### 5. 数据访问层 (Repository)
- **resource_repository.py**: 资源数据访问
- **appointment_repository.py**: 预约数据访问
- **user_repository.py**: 用户数据访问
- **analytics_repository.py**: 分析数据访问

## 功能特性

### 1. 智能资源匹配

```python
# 示例：基于用户体质的医生匹配
def match_doctor_by_constitution(user_constitution, symptoms):
    """
    根据用户体质和症状匹配最适合的中医师
    """
    # 小克智能体分析用户体质
    constitution_analysis = xiaoke_agent.analyze_constitution(user_constitution)
    
    # 匹配专长医生
    suitable_doctors = resource_manager.find_doctors_by_specialty(
        constitution_type=constitution_analysis.type,
        symptoms=symptoms,
        availability=True
    )
    
    return suitable_doctors
```

### 2. 实时资源监控

```python
# 示例：实时监控资源状态
def monitor_resource_availability():
    """
    实时监控所有医疗资源的可用性
    """
    resources = resource_manager.get_all_resources()
    
    for resource in resources:
        status = resource_monitor.check_status(resource.id)
        if status.availability < 0.3:  # 可用性低于30%
            # 触发资源调度优化
            scheduler.optimize_resource_allocation(resource.id)
            
            # 通知管理员
            notification_service.send_alert(
                message=f"资源 {resource.name} 可用性较低",
                level="warning"
            )
```

### 3. 个性化服务推荐

```python
# 示例：个性化医疗服务推荐
def recommend_medical_services(user_id, health_data):
    """
    基于用户健康数据推荐个性化医疗服务
    """
    # 小克智能体分析健康数据
    health_analysis = xiaoke_agent.analyze_health_data(health_data)
    
    # 生成推荐服务
    recommendations = recommendation_service.generate_recommendations(
        user_id=user_id,
        health_status=health_analysis,
        preferences=user_preferences
    )
    
    return recommendations
```

## API接口

### gRPC服务接口

```protobuf
service MedicalResourceService {
    // 资源管理
    rpc GetAvailableResources(ResourceRequest) returns (ResourceResponse);
    rpc BookResource(BookingRequest) returns (BookingResponse);
    rpc CancelBooking(CancelRequest) returns (CancelResponse);
    
    // 智能推荐
    rpc GetRecommendations(RecommendationRequest) returns (RecommendationResponse);
    rpc MatchDoctor(DoctorMatchRequest) returns (DoctorMatchResponse);
    
    // 预约管理
    rpc CreateAppointment(AppointmentRequest) returns (AppointmentResponse);
    rpc UpdateAppointment(UpdateAppointmentRequest) returns (AppointmentResponse);
    rpc GetAppointments(GetAppointmentsRequest) returns (AppointmentsResponse);
    
    // 资源监控
    rpc GetResourceStatus(StatusRequest) returns (StatusResponse);
    rpc GetAnalytics(AnalyticsRequest) returns (AnalyticsResponse);
}
```

### REST API接口

```yaml
paths:
  /api/v1/resources:
    get:
      summary: 获取可用医疗资源
      parameters:
        - name: type
          in: query
          description: 资源类型 (doctor|facility|equipment|medicine)
        - name: location
          in: query
          description: 地理位置
        - name: specialty
          in: query
          description: 专科类型
      responses:
        200:
          description: 成功返回资源列表
          
  /api/v1/appointments:
    post:
      summary: 创建预约
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AppointmentRequest'
      responses:
        201:
          description: 预约创建成功
          
  /api/v1/recommendations:
    get:
      summary: 获取个性化推荐
      parameters:
        - name: user_id
          in: query
          required: true
          description: 用户ID
      responses:
        200:
          description: 成功返回推荐列表
```

## 部署配置

### 环境要求

- Python 3.9+
- PostgreSQL 13+
- Redis 6.0+
- MongoDB 4.4+
- Docker & Docker Compose

### 配置文件

```yaml
# config/config.yaml
service:
  name: medical-resource-service
  version: 1.0.0
  port: 9084

xiaoke_agent:
  model_path: "/models/xiaoke_v1.0"
  learning_rate: 0.001
  decision_threshold: 0.8

database:
  postgres:
    host: ${POSTGRES_HOST:-localhost}
    port: ${POSTGRES_PORT:-5432}
    database: ${POSTGRES_DB:-medical_resources}
    username: ${POSTGRES_USER:-postgres}
    password: ${POSTGRES_PASSWORD:-password}
    
  redis:
    host: ${REDIS_HOST:-localhost}
    port: ${REDIS_PORT:-6379}
    database: ${REDIS_DB:-0}
    
  mongodb:
    host: ${MONGODB_HOST:-localhost}
    port: ${MONGODB_PORT:-27017}
    database: ${MONGODB_DB:-medical_analytics}

external_services:
  payment_service: ${PAYMENT_SERVICE_URL}
  notification_service: ${NOTIFICATION_SERVICE_URL}
  his_systems:
    - name: "hospital_a"
      endpoint: ${HOSPITAL_A_HIS_URL}
      auth_token: ${HOSPITAL_A_TOKEN}
```

### Docker部署

```bash
# 构建镜像
docker build -t medical-resource-service:latest .

# 启动服务
docker-compose up -d
```

## 监控与运维

### 健康检查

- `/health`: 服务健康状态
- `/metrics`: Prometheus指标
- `/ready`: 服务就绪状态

### 关键指标

- 资源利用率
- 预约成功率
- 响应时间
- 用户满意度
- 智能体决策准确率

### 日志管理

- 结构化日志输出
- 分级日志记录
- 日志聚合和分析
- 异常告警机制

## 开发指南

### 本地开发环境搭建

```bash
# 1. 克隆项目
git clone <repository-url>
cd medical-resource-service

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 初始化数据库
python scripts/init_db.py

# 6. 启动服务
python -m cmd.server
```

### 测试

```bash
# 单元测试
pytest test/unit/

# 集成测试
pytest test/integration/

# 端到端测试
pytest test/e2e/

# 性能测试
pytest test/performance/
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。 