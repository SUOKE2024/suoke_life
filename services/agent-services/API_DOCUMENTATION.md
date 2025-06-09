# 索克生活智能体服务 API 文档

## 概述

索克生活平台包含四个核心智能体服务，每个智能体都有特定的功能和专业领域：

- **小艾 (Xiaoai)**: 多模态感知与智能分析
- **小克 (Xiaoke)**: 健康服务与产品推荐  
- **老克 (Laoke)**: 知识传播与社区管理
- **索儿 (Soer)**: 营养与生活方式管理

## 服务架构

所有智能体服务都采用统一的架构模式：

- **协议**: gRPC + REST API
- **端口**: 8015-8018 (分别对应小艾、小克、老克、索儿)
- **认证**: JWT Token
- **数据格式**: Protocol Buffers + JSON

## 1. 小艾智能体服务 (Xiaoai Service)

### 服务信息
- **端口**: 8015
- **gRPC服务**: `suoke.xiaoai.v1.XiaoaiService`
- **专业领域**: 多模态感知、图像分析、语音处理

### API 接口

#### 1.1 图像分析
```protobuf
rpc AnalyzeImage(ImageRequest) returns (ImageResult);
```

**请求参数**:
```json
{
  "image_data": "base64编码的图像数据",
  "analysis_type": "face|tongue|skin|general",
  "patient_id": "患者ID",
  "session_id": "会话ID"
}
```

**响应结果**:
```json
{
  "analysis_id": "分析ID",
  "image_type": "检测到的图像类型",
  "classifications": {
    "face_analysis": {
      "complexion": "面色分析",
      "spirit": "神态分析",
      "constitution_indicators": ["体质指标"]
    },
    "tongue_analysis": {
      "tongue_color": "舌色",
      "tongue_coating": "苔质",
      "tongue_shape": "舌形"
    }
  },
  "confidence": 0.95,
  "processing_time": 1.2
}
```

#### 1.2 语音处理
```protobuf
rpc ProcessVoice(VoiceRequest) returns (VoiceResult);
```

**请求参数**:
```json
{
  "audio_data": "base64编码的音频数据",
  "audio_format": "wav|mp3|m4a",
  "analysis_type": "speech_recognition|voice_analysis",
  "patient_id": "患者ID"
}
```

**响应结果**:
```json
{
  "transcription": "语音转文字结果",
  "voice_characteristics": {
    "tone": "音调分析",
    "volume": "音量分析", 
    "rhythm": "节律分析",
    "emotional_state": "情绪状态"
  },
  "health_indicators": ["健康指标"],
  "confidence": 0.88
}
```

#### 1.3 健康建议
```protobuf
rpc GetHealthAdvice(HealthRequest) returns (HealthAdvice);
```

## 2. 小克智能体服务 (Xiaoke Service)

### 服务信息
- **端口**: 8016
- **gRPC服务**: `suoke.xiaoke.v1.XiaokeService`
- **专业领域**: 健康服务、产品推荐、预约管理

### API 接口

#### 2.1 产品推荐
```protobuf
rpc RecommendProducts(ProductRequest) returns (ProductResponse);
```

**请求参数**:
```json
{
  "user_id": "用户ID",
  "health_profile": {
    "constitution_type": "体质类型",
    "health_conditions": ["健康状况"],
    "preferences": ["偏好设置"]
  },
  "recommendation_type": "supplement|food|device|service"
}
```

**响应结果**:
```json
{
  "recommendations": [
    {
      "product_id": "产品ID",
      "product_name": "产品名称",
      "category": "产品类别",
      "match_score": 0.92,
      "reasons": ["推荐理由"],
      "usage_instructions": "使用说明",
      "price_range": "价格区间"
    }
  ],
  "total_count": 10,
  "recommendation_id": "推荐ID"
}
```

#### 2.2 专家预约
```protobuf
rpc BookAppointment(AppointmentRequest) returns (AppointmentResponse);
```

#### 2.3 服务订阅
```protobuf
rpc ManageSubscription(SubscriptionRequest) returns (SubscriptionResponse);
```

## 3. 老克智能体服务 (Laoke Service)

### 服务信息
- **端口**: 8017
- **gRPC服务**: `suoke.laoke.v1.LaokeService`
- **专业领域**: 知识传播、社区管理、教育服务

### API 接口

#### 3.1 知识查询
```protobuf
rpc QueryKnowledge(KnowledgeRequest) returns (KnowledgeResponse);
```

**请求参数**:
```json
{
  "query": "查询内容",
  "knowledge_type": "tcm|nutrition|lifestyle|disease",
  "user_level": "beginner|intermediate|advanced",
  "context": "查询上下文"
}
```

**响应结果**:
```json
{
  "knowledge_items": [
    {
      "title": "知识标题",
      "content": "知识内容",
      "source": "知识来源",
      "reliability_score": 0.95,
      "related_topics": ["相关主题"],
      "difficulty_level": "难度等级"
    }
  ],
  "total_results": 25,
  "query_id": "查询ID"
}
```

#### 3.2 社区管理
```protobuf
rpc ManageCommunity(CommunityRequest) returns (CommunityResponse);
```

#### 3.3 学习路径
```protobuf
rpc CreateLearningPath(LearningPathRequest) returns (LearningPathResponse);
```

## 4. 索儿智能体服务 (Soer Service)

### 服务信息
- **端口**: 8018
- **gRPC服务**: `suoke.soer.v1.SoerService`
- **专业领域**: 营养管理、生活方式优化、健康监测

### API 接口

#### 4.1 生成健康计划
```protobuf
rpc GenerateHealthPlan(HealthPlanRequest) returns (HealthPlanResponse);
```

**请求参数**:
```json
{
  "user_id": "用户ID",
  "health_goals": ["健康目标"],
  "current_status": {
    "constitution_type": "体质类型",
    "health_metrics": {
      "bmi": 22.5,
      "blood_pressure": "120/80",
      "heart_rate": 72
    },
    "lifestyle_factors": {
      "exercise_frequency": "每周3次",
      "sleep_duration": 7.5,
      "stress_level": "中等"
    }
  },
  "preferences": {
    "diet_restrictions": ["饮食限制"],
    "exercise_preferences": ["运动偏好"],
    "time_availability": "可用时间"
  }
}
```

**响应结果**:
```json
{
  "health_plan": {
    "plan_id": "计划ID",
    "duration": "计划周期",
    "nutrition_plan": {
      "daily_calories": 2000,
      "macronutrient_ratio": {
        "carbs": 50,
        "protein": 25,
        "fat": 25
      },
      "meal_suggestions": ["餐食建议"],
      "supplements": ["营养补充"]
    },
    "exercise_plan": {
      "weekly_schedule": ["运动安排"],
      "intensity_levels": ["强度等级"],
      "duration_per_session": "每次时长"
    },
    "lifestyle_adjustments": ["生活方式调整"],
    "monitoring_metrics": ["监测指标"]
  },
  "expected_outcomes": ["预期效果"],
  "confidence": 0.89
}
```

#### 4.2 营养追踪
```protobuf
rpc TrackNutrition(NutritionRequest) returns (NutritionResponse);
```

#### 4.3 传感器数据分析
```protobuf
rpc AnalyzeSensorData(SensorDataRequest) returns (SensorDataResponse);
```

#### 4.4 异常模式检测
```protobuf
rpc DetectAbnormalPattern(AbnormalPatternRequest) returns (AbnormalPatternResponse);
```

#### 4.5 健康趋势预测
```protobuf
rpc PredictHealthTrend(HealthTrendRequest) returns (HealthTrendResponse);
```

#### 4.6 睡眠建议
```protobuf
rpc GetSleepRecommendation(SleepRequest) returns (SleepResponse);
```

#### 4.7 情绪状态分析
```protobuf
rpc AnalyzeEmotionalState(EmotionalStateRequest) returns (EmotionalStateResponse);
```

## 通用错误处理

所有服务都使用统一的错误处理机制：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细信息",
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "请求ID"
  }
}
```

### 常见错误码

- `INVALID_REQUEST`: 请求参数无效
- `AUTHENTICATION_FAILED`: 认证失败
- `AUTHORIZATION_DENIED`: 权限不足
- `RESOURCE_NOT_FOUND`: 资源不存在
- `RATE_LIMIT_EXCEEDED`: 请求频率超限
- `INTERNAL_ERROR`: 内部服务错误
- `SERVICE_UNAVAILABLE`: 服务不可用

## 认证与授权

### JWT Token 格式
```json
{
  "user_id": "用户ID",
  "roles": ["用户角色"],
  "permissions": ["权限列表"],
  "exp": 1640995200,
  "iat": 1640908800
}
```

### 请求头设置
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
X-Request-ID: <REQUEST_ID>
```

## 监控与日志

### 健康检查端点
- `GET /health` - 服务健康状态
- `GET /metrics` - Prometheus指标
- `GET /info` - 服务信息

### 日志格式
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "xiaoai-service",
  "request_id": "req-123",
  "user_id": "user-456",
  "message": "处理图像分析请求",
  "duration": 1.23,
  "metadata": {}
}
```

## 性能指标

| 服务 | 平均响应时间 | 并发处理能力 | 可用性 |
|------|-------------|-------------|--------|
| 小艾服务 | <2s | 100 req/s | 99.9% |
| 小克服务 | <1s | 200 req/s | 99.9% |
| 老克服务 | <500ms | 300 req/s | 99.9% |
| 索儿服务 | <1.5s | 150 req/s | 99.9% |

## 部署配置

### Docker 部署
```bash
# 构建镜像
docker build -t suoke/xiaoai-service:latest ./xiaoai-service

# 运行容器
docker run -d \
  --name xiaoai-service \
  -p 8015:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  suoke/xiaoai-service:latest
```

### Kubernetes 部署
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xiaoai-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xiaoai-service
  template:
    metadata:
      labels:
        app: xiaoai-service
    spec:
      containers:
      - name: xiaoai-service
        image: suoke/xiaoai-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 开发指南

### 本地开发环境设置
```bash
# 1. 克隆代码
git clone https://github.com/suoke/suoke_life.git
cd suoke_life/services/agent-services

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
cd xiaoai-service
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 测试
```bash
# 运行单元测试
pytest tests/ -v

# 运行集成测试
pytest tests/integration/ -v

# 代码覆盖率
pytest --cov=xiaoai tests/
```

## 更新日志

### v1.0.0 (2024-06-09)
- ✅ 完成四个智能体服务的核心功能
- ✅ 修复gRPC接口语法问题
- ✅ 完善API文档和错误处理
- ✅ 优化性能监控和日志记录
- ✅ 达到95%完成度，生产就绪

---

**联系方式**: dev@suokelife.com  
**文档版本**: v1.0.0  
**最后更新**: 2024-06-09 