# 切诊服务集成指南

本文档描述切诊服务(palpation-service)与索克生活APP其他服务的集成方法。

## 与四诊合参系统的集成

切诊服务是四诊合参系统的重要组成部分，提供触诊数据分析。完整的四诊合参系统包括：

- **切诊服务** (palpation-service) - 提供脉诊、腹诊和皮肤触诊分析
- **望诊服务** (look-service) - 提供面诊、舌诊和形体分析
- **闻诊服务** (listen-service) - 提供声音和气味分析
- **问诊服务** (inquiry-service) - 提供问诊对话和症状分析

## 集成架构

切诊服务提供标准的gRPC接口，供其他服务调用。在四诊合参体系中，主要集成路径为：

1. **小艾服务(xiaoai-service)作为协调者**：
   - 调用各个诊断服务获取分析结果
   - 融合多个诊断结果生成综合分析

2. **系统间通信**：
   - 服务间使用gRPC进行同步通信
   - 使用消息队列(RabbitMQ)进行异步通信

## 如何集成

### 1. 从小艾服务调用切诊服务

```python
# xiaoai_service代码示例
import grpc
from palpation.api.grpc import palpation_service_pb2 as pb2
from palpation.api.grpc import palpation_service_pb2_grpc as pb2_grpc

# 建立gRPC连接
channel = grpc.insecure_channel('palpation-service:50053')
client = pb2_grpc.PalpationServiceStub(channel)

# 获取综合切诊分析
def get_palpation_analysis(user_id, pulse_session_id):
    request = pb2.ComprehensiveAnalysisRequest(
        user_id=user_id,
        pulse_session_id=pulse_session_id,
        include_abdominal=True,
        include_skin=True
    )
    
    try:
        response = client.GetComprehensivePalpationAnalysis(request)
        if response.success:
            return {
                'analysis_id': response.analysis_id,
                'overview': {
                    'pulse': extract_pulse_overview(response.overview.pulse),
                    'abdominal': extract_abdominal_overview(response.overview.abdominal),
                    'skin': extract_skin_overview(response.overview.skin),
                    'general_condition': response.overview.general_condition
                },
                'tcm_patterns': extract_tcm_patterns(response.tcm_patterns),
                'health_alerts': extract_health_alerts(response.health_alerts),
                'summary': response.summary
            }
        else:
            logger.error(f"切诊分析失败: {response.error_message}")
            return None
    except Exception as e:
        logger.exception(f"调用切诊服务异常: {str(e)}")
        return None
```

### 2. 切诊服务调用其他服务

切诊服务也可以主动调用其他服务获取辅助数据，例如：

```python
# palpation_service代码示例
import grpc
from inquiry.api.grpc import inquiry_service_pb2 as inq_pb2
from inquiry.api.grpc import inquiry_service_pb2_grpc as inq_pb2_grpc

# 调用问诊服务获取相关症状信息
def get_symptom_info(user_id, symptom_type):
    channel = grpc.insecure_channel('inquiry-service:50051')
    client = inq_pb2_grpc.InquiryServiceStub(channel)
    
    request = inq_pb2.SymptomInfoRequest(
        user_id=user_id,
        symptom_type=symptom_type
    )
    
    try:
        response = client.GetSymptomInfo(request)
        return response
    except Exception as e:
        logger.exception(f"调用问诊服务异常: {str(e)}")
        return None
```

## API整合策略

### 1. 数据标准化

为确保各服务间数据一致性，我们采用以下标准化策略：

- 使用统一的用户ID系统
- 采用标准化的证型命名和分类
- 使用一致的评分和置信度机制

### 2. 异步通知机制

对于长时间运行的分析任务，切诊服务会发送异步通知：

```python
# 通过消息总线发送分析完成通知
def notify_analysis_complete(analysis_id, user_id):
    message = {
        'event_type': 'palpation_analysis_complete',
        'analysis_id': analysis_id,
        'user_id': user_id,
        'timestamp': time.time()
    }
    
    message_bus.publish('diagnostic_events', message)
```

## 配置示例

在`config/config.yaml`中配置服务集成参数：

```yaml
# 服务集成配置
service_integration:
  # 小艾服务配置
  xiaoai_service:
    host: xiaoai-service
    port: 50050
    timeout_ms: 5000
    
  # 问诊服务配置
  inquiry_service:
    host: inquiry-service
    port: 50051
    timeout_ms: 3000
    
  # 望诊服务配置
  look_service:
    host: look-service
    port: 50052
    timeout_ms: 3000
    
  # 消息总线配置
  message_bus:
    host: message-bus
    port: 5672
    exchange: diagnostic_events
    user: guest
    password: guest
```

## 健康检查和服务发现

切诊服务提供健康检查端点，供服务发现系统使用：

```
GET /health
```

响应示例：

```json
{
  "status": "UP",
  "services": {
    "database": "UP",
    "message_bus": "UP"
  },
  "version": "1.0.0"
}
```

## 故障处理

1. **服务不可用时的策略**：
   - 使用断路器模式防止级联故障
   - 应用退避和重试机制
   - 降级到本地缓存数据

2. **数据不一致处理**：
   - 检测并记录跨服务数据不一致
   - 采用最近时间戳策略解决冲突
   - 提供手动校准接口

## 集成测试

在`test/integration`目录中提供了与其他服务的集成测试，包括：

- 与小艾服务的四诊合参测试
- 与问诊服务的症状关联测试
- 与望诊服务的综合分析测试

## 性能考量

- 服务间通信使用Protocol Buffers减少数据传输量
- 对频繁使用的分析结果进行缓存
- 使用异步通信减少请求阻塞
- 批量API减少网络往返次数 