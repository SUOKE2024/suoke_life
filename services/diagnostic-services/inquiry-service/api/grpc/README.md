# 问诊服务gRPC接口文档

## 概述

问诊服务是索克生活APP四诊合参体系中的"问诊"部分，通过gRPC协议提供以下功能：

1. 问诊会话管理
2. 用户-AI智能问诊交互
3. 症状提取
4. 中医证型映射
5. 问诊结果汇总
6. 与小艾服务的集成

本文档详细描述了如何使用问诊服务的gRPC接口。

## 接口定义

完整的接口定义在[inquiry_service.proto](./inquiry_service.proto)文件中，包含以下主要服务接口：

```protobuf
service InquiryService {
  // 会话管理
  rpc StartInquirySession(StartInquirySessionRequest) returns (StartInquirySessionResponse);
  rpc EndInquirySession(EndInquirySessionRequest) returns (EndInquirySessionResponse);
  rpc GetInquirySession(GetInquirySessionRequest) returns (GetInquirySessionResponse);
  
  // 问诊互动
  rpc InteractWithUser(InteractWithUserRequest) returns (stream InteractWithUserResponse);
  
  // 症状与证型分析
  rpc ExtractSymptoms(ExtractSymptomsRequest) returns (ExtractSymptomsResponse);
  rpc MapToTCMPatterns(MapToTCMPatternsRequest) returns (MapToTCMPatternsResponse);
  
  // 问诊总结
  rpc GenerateSessionSummary(GenerateSessionSummaryRequest) returns (GenerateSessionSummaryResponse);
  
  // 小艾服务集成
  rpc SubmitToXiaoai(SubmitToXiaoaiRequest) returns (SubmitToXiaoaiResponse);
  rpc GetXiaoaiIntegrationStatus(GetXiaoaiIntegrationStatusRequest) returns (GetXiaoaiIntegrationStatusResponse);
  rpc GetXiaoaiIntegrationResults(GetXiaoaiIntegrationResultsRequest) returns (GetXiaoaiIntegrationResultsResponse);
}
```

## 客户端示例

### Python 客户端示例

以下是使用Python调用问诊服务的示例代码：

```python
import grpc
import inquiry_service_pb2
import inquiry_service_pb2_grpc

def run():
    # 创建gRPC通道
    channel = grpc.insecure_channel('localhost:50053')
    
    # 创建客户端存根
    stub = inquiry_service_pb2_grpc.InquiryServiceStub(channel)
    
    # 开始问诊会话
    start_request = inquiry_service_pb2.StartInquirySessionRequest(
        user_id="user-123",
        metadata={"client_version": "1.0.0"}
    )
    start_response = stub.StartInquirySession(start_request)
    
    # 获取会话ID
    session_id = start_response.session_id
    print(f"会话已创建，ID: {session_id}")
    
    # 与用户互动
    interact_request = inquiry_service_pb2.InteractWithUserRequest(
        session_id=session_id,
        message="最近胃部不舒服，饭后胀痛，持续两周了"
    )
    
    # 获取流式响应
    for response in stub.InteractWithUser(interact_request):
        print(f"AI: {response.message}")
        
        # 如果有提取的症状
        if response.extracted_symptoms:
            for symptom in response.extracted_symptoms:
                print(f"提取到症状: {symptom.name}, 置信度: {symptom.confidence}")
    
    # 分析中医证型
    pattern_request = inquiry_service_pb2.MapToTCMPatternsRequest(
        session_id=session_id
    )
    pattern_response = stub.MapToTCMPatterns(pattern_request)
    
    print(f"中医证型分析: {pattern_response.analysis}")
    if pattern_response.primary_pattern:
        print(f"主要证型: {pattern_response.primary_pattern.name}, 分数: {pattern_response.primary_pattern.score}")
    
    # 生成会话总结
    summary_request = inquiry_service_pb2.GenerateSessionSummaryRequest(
        session_id=session_id
    )
    summary_response = stub.GenerateSessionSummary(summary_request)
    
    print(f"问诊总结: {summary_response.summary}")
    
    # 提交到小艾服务
    submit_request = inquiry_service_pb2.SubmitToXiaoaiRequest(
        session_id=session_id
    )
    submit_response = stub.SubmitToXiaoai(submit_request)
    
    print(f"提交到小艾服务，集成ID: {submit_response.integration_id}")
    
    # 获取集成状态
    status_request = inquiry_service_pb2.GetXiaoaiIntegrationStatusRequest(
        integration_id=submit_response.integration_id
    )
    status_response = stub.GetXiaoaiIntegrationStatus(status_request)
    
    print(f"集成状态: {status_response.status}, 完成百分比: {status_response.completion_percentage}%")
    
    # 关闭通道
    channel.close()

if __name__ == '__main__':
    run()
```

### Go 客户端示例

```go
package main

import (
    "context"
    "fmt"
    "io"
    "log"
    "time"

    "google.golang.org/grpc"
    pb "path/to/inquiry_service"
)

func main() {
    // 创建连接
    conn, err := grpc.Dial("localhost:50053", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("连接失败: %v", err)
    }
    defer conn.Close()

    // 创建客户端
    client := pb.NewInquiryServiceClient(conn)
    ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
    defer cancel()

    // 开始问诊会话
    startResp, err := client.StartInquirySession(ctx, &pb.StartInquirySessionRequest{
        UserId: "user-456",
        Metadata: map[string]string{
            "client_version": "1.0.0",
        },
    })
    if err != nil {
        log.Fatalf("开始会话失败: %v", err)
    }

    sessionId := startResp.SessionId
    fmt.Printf("会话已创建，ID: %s\n", sessionId)

    // 与用户互动
    stream, err := client.InteractWithUser(ctx, &pb.InteractWithUserRequest{
        SessionId: sessionId,
        Message:   "最近胃部不舒服，饭后胀痛，持续两周了",
    })
    if err != nil {
        log.Fatalf("交互失败: %v", err)
    }

    for {
        resp, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            log.Fatalf("接收响应失败: %v", err)
        }

        fmt.Printf("AI: %s\n", resp.Message)

        // 打印提取的症状
        for _, symptom := range resp.ExtractedSymptoms {
            fmt.Printf("提取到症状: %s, 置信度: %f\n", symptom.Name, symptom.Confidence)
        }
    }

    // 生成总结
    summaryResp, err := client.GenerateSessionSummary(ctx, &pb.GenerateSessionSummaryRequest{
        SessionId: sessionId,
    })
    if err != nil {
        log.Fatalf("生成总结失败: %v", err)
    }

    fmt.Printf("问诊总结: %s\n", summaryResp.Summary)
}
```

## 消息字段说明

### 症状（Symptom）

症状对象包含以下字段：

- `name`: 症状名称
- `description`: 症状描述（可选）
- `body_part`: 身体部位（可选）
- `severity`: 严重程度（mild/moderate/severe）
- `duration`: 持续时间类型（acute/subacute/chronic）
- `duration_value`: 持续时间值（天/周/月数）
- `frequency`: 频率描述
- `confidence`: 提取置信度（0-1）
- `source_text`: 来源文本

### 中医证型（TCMPattern）

证型对象包含以下字段：

- `name`: 证型名称
- `score`: 证型匹配分数（0-1）
- `key_symptoms`: 关键症状列表
- `description`: 证型描述
- `recommendations`: 建议列表

## 错误处理

服务使用标准gRPC错误码：

- `INVALID_ARGUMENT`: 请求参数无效
- `NOT_FOUND`: 会话或资源不存在
- `UNAVAILABLE`: 服务暂时不可用
- `INTERNAL`: 内部服务错误

错误消息将包含详细说明。

## 安全认证

生产环境下，服务需要使用TLS和令牌认证：

```python
# TLS加密通道
with open('server.crt', 'rb') as f:
    trusted_certs = f.read()
credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

# 添加令牌认证
call_credentials = grpc.access_token_call_credentials("my-token")
combined_credentials = grpc.composite_channel_credentials(credentials, call_credentials)

# 创建安全通道
channel = grpc.secure_channel('api.suoke.life:443', combined_credentials)
```

## 断点续传

问诊服务支持断点续传功能，客户端可以在会话断开后重新连接并继续之前的问诊：

```python
# 恢复之前的会话
get_request = inquiry_service_pb2.GetInquirySessionRequest(
    session_id=previous_session_id
)
get_response = stub.GetInquirySession(get_request)

if get_response.session.status == "active":
    # 继续之前的会话
    interact_request = inquiry_service_pb2.InteractWithUserRequest(
        session_id=previous_session_id,
        message="还有一个问题..."
    )
    # ...
```

## 流量控制

客户端应实现合理的重试和退避策略以防止服务过载：

```python
def with_retry(func, max_retries=3, backoff_factor=1.5):
    retries = 0
    delay = 1.0
    
    while retries < max_retries:
        try:
            return func()
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.UNAVAILABLE:
                raise
                
            retries += 1
            if retries >= max_retries:
                raise
                
            time.sleep(delay)
            delay *= backoff_factor
```

## 版本兼容性

客户端应在元数据中包含版本信息：

```python
metadata = [
    ('client-version', '1.0.0'),
]
response = stub.StartInquirySession(start_request, metadata=metadata)
```

## 更多信息

有关更多信息，请参阅：

- [完整API定义](./inquiry_service.proto)
- [问诊服务实现](../../internal/delivery/inquiry_service_impl.py)
- [小艾服务集成文档](../../integration/xiaoai_service/README.md) 