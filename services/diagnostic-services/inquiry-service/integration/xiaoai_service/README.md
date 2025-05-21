# 问诊服务与小艾服务集成

## 概述

本文档描述了问诊服务（inquiry-service）与小艾服务（xiaoai-service）的集成方式。小艾服务是索克生活APP四诊合参体系的核心协调引擎，负责整合问诊、望诊、闻诊和切诊四个方面的诊断结果，形成完整的中医辨证与健康评估。

## 集成架构

问诊服务通过gRPC协议与小艾服务通信，主要流程如下：

1. 用户完成问诊流程后，问诊服务将提取的症状和映射的中医证型提交给小艾服务
2. 小艾服务将问诊结果与其他诊断结果（如有）进行整合
3. 问诊服务可以查询集成状态和最终的四诊合参结果
4. 最终结果包括用户的体质评估、中医证型分析和健康建议

![集成架构图](../../docs/images/inquiry_xiaoai_integration.png)

## 通信协议

问诊服务与小艾服务之间的通信基于gRPC协议，相关的接口定义在`api/grpc/xiaoai_service.proto`文件中。

### 主要接口

小艾服务提供以下主要接口：

```protobuf
service XiaoaiService {
  // 提交问诊结果
  rpc SubmitInquiryResults(SubmitInquiryResultsRequest) returns (SubmitInquiryResultsResponse);
  
  // 获取四诊合参状态
  rpc GetFourDiagnosisStatus(GetFourDiagnosisStatusRequest) returns (GetFourDiagnosisStatusResponse);
  
  // 获取四诊合参结果
  rpc GetFourDiagnosisResults(GetFourDiagnosisResultsRequest) returns (GetFourDiagnosisResultsResponse);
}
```

## 集成客户端

问诊服务使用`XiaoaiClient`类与小艾服务通信，该类实现在`xiaoai_client.py`文件中。

### 客户端配置

客户端可通过环境变量或配置文件配置：

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|---------|-------|-----|
| 服务主机地址 | XIAOAI_SERVICE_HOST | xiaoai-service | 小艾服务主机名 |
| 服务端口 | XIAOAI_SERVICE_PORT | 50053 | 小艾服务端口 |
| 超时时间(毫秒) | TIMEOUT_MS | 5000 | 请求超时时间 |
| 重试次数 | RETRY_COUNT | 3 | 请求失败重试次数 |
| 重试间隔(毫秒) | RETRY_INTERVAL_MS | 1000 | 重试间隔时间 |
| TLS启用 | TLS_ENABLED | false | 是否启用TLS加密 |
| TLS证书路径 | TLS_CERT_PATH |  | TLS证书路径 |

### 使用示例

以下是使用`XiaoaiClient`的示例代码：

```python
from integration.xiaoai_service.xiaoai_client import XiaoaiClient

# 初始化客户端
client = XiaoaiClient(config={
    'XIAOAI_SERVICE_HOST': 'xiaoai-service',
    'XIAOAI_SERVICE_PORT': 50053,
    'TIMEOUT_MS': 5000
})

try:
    # 提交问诊结果
    symptoms = [
        {
            "name": "胸胁胀痛",
            "description": "肝区疼痛，伴随胀感",
            "body_part": "胸胁部",
            "severity": "moderate",
            "confidence": 0.9
        },
        # 其他症状...
    ]
    
    tcm_patterns = [
        {
            "name": "肝郁脾虚证",
            "score": 0.85,
            "description": "肝气郁结，脾失健运",
            "key_symptoms": ["胸胁胀痛", "脘腹胀满"]
        },
        # 其他证型...
    ]
    
    summary = "用户近期出现胸胁胀痛、脘腹胀满等症状，舌质淡红，苔薄白，脉弦细，考虑为肝郁脾虚证。"
    
    result = client.submit_inquiry_results(
        session_id="inquiry-session-123",
        user_id="user-456",
        symptoms=symptoms,
        tcm_patterns=tcm_patterns,
        summary=summary
    )
    
    integration_id = result.get('integration_id')
    print(f"问诊结果已提交，集成ID: {integration_id}")
    
    # 查询处理状态
    status_result = client.get_four_diagnosis_status(integration_id)
    print(f"四诊合参状态: {status_result['status']}")
    print(f"完成模块: {status_result['completed_modules']}")
    print(f"待完成模块: {status_result['pending_modules']}")
    print(f"完成百分比: {status_result['completion_percentage']}%")
    
    # 查询四诊合参结果
    if status_result['status'] == 'completed':
        diagnosis_result = client.get_four_diagnosis_results(integration_id)
        print(f"四诊合参结果:")
        print(f"用户ID: {diagnosis_result['user_id']}")
        print(f"主要体质: {diagnosis_result['constitution_types'][0]['name']}")
        print(f"主要证型: {diagnosis_result['tcm_diagnosis']['primary_pattern']['name']}")
        print(f"健康建议: {diagnosis_result['health_recommendations']}")
        
finally:
    # 关闭客户端连接
    client.close()
```

## 错误处理

客户端实现了以下错误处理：

1. 网络错误重试：当遇到临时网络问题时，自动按配置的次数和间隔进行重试
2. 超时处理：请求超时时抛出异常，可由调用者捕获并处理
3. gRPC错误码：将小艾服务返回的gRPC错误码转换为异常，包含详细的错误信息

### 常见错误及处理

| 错误类型 | 错误代码 | 处理方式 |
|---------|---------|---------|
| 连接失败 | UNAVAILABLE | 检查网络连接和小艾服务状态，稍后重试 |
| 超时错误 | DEADLINE_EXCEEDED | 考虑增加超时时间，或稍后重试 |
| 认证错误 | UNAUTHENTICATED | 检查认证凭据是否正确 |
| 参数错误 | INVALID_ARGUMENT | 检查提交的症状和证型数据格式是否正确 |
| 服务内部错误 | INTERNAL | 联系小艾服务运维团队 |

## 数据同步和一致性

为确保数据一致性，问诊服务和小艾服务之间的数据同步遵循以下原则：

1. **幂等性**：重复提交相同的问诊结果会返回相同的集成ID，不会创建重复记录
2. **事务性**：提交问诊结果是原子操作，要么完全成功，要么完全失败
3. **状态追踪**：通过集成ID可以随时查询处理状态，确保数据处理的透明度
4. **结果不可变**：一旦四诊合参完成，结果不可修改

## 监控与可观测性

集成链路的监控包括：

1. gRPC请求耗时统计
2. 请求成功/失败率
3. 重试次数统计
4. 错误类型分布

所有监控指标通过Prometheus收集，可在Grafana仪表板查看。

## 版本兼容性

为确保版本兼容性，遵循以下规则：

1. 小艾服务的API遵循语义化版本控制
2. 问诊服务检测到不兼容的API版本时会记录错误日志
3. 在请求头中包含客户端版本信息，以便服务端做兼容性处理

## 部署和运维

问诊服务与小艾服务应部署在同一Kubernetes命名空间内，以确保网络连接可靠性和安全性。两个服务之间的通信应通过服务网格（如Istio）进行管理。

## 故障排除

常见问题及解决方案：

1. **连接失败**：检查网络连接、服务名称解析和防火墙设置
2. **请求超时**：检查小艾服务负载情况，考虑增加超时时间或实现断路器
3. **数据不一致**：对比问诊服务和小艾服务的日志，确认数据传输完整性
4. **证型映射不准确**：检查症状提取和证型映射逻辑，考虑更新知识库

## 更多资源

- [小艾服务API文档](../../docs/api/xiaoai_service.md)
- [四诊合参技术白皮书](../../docs/whitepapers/four_diagnosis_integration.pdf)
- [问诊服务与小艾服务集成测试计划](../../docs/testing/inquiry_xiaoai_integration.md) 