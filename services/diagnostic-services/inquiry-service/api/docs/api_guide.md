# 问诊服务API文档

## 概述
问诊服务(inquiry-service)提供中医问诊功能，包括会话管理、症状提取、证型匹配等功能。

## 基础信息
- 基础URL: `inquiry-service:50053`
- 协议: gRPC
- 版本: v1

## 接口说明

### 1. 开始问诊会话

#### 请求
```protobuf
message StartSessionRequest {
  string user_id = 1;           // 用户ID
  string session_type = 2;      // 会话类型 (GENERAL, FOLLOW_UP)
  map<string, string> context = 3; // 上下文信息
}
```

#### 响应
```protobuf
message SessionResponse {
  string session_id = 1;        // 会话ID
  string status = 2;            // 会话状态
  int64 created_at = 3;         // 创建时间戳
  string greeting_message = 4;  // 问候语
}
```

### 2. 问诊互动

#### 请求
```protobuf
message InteractionRequest {
  string session_id = 1;        // 会话ID
  string user_input = 2;        // 用户输入
  map<string, string> context = 3; // 上下文信息
}
```

#### 响应
```protobuf
message InteractionResponse {
  string response_text = 1;     // 响应文本
  string response_type = 2;     // 响应类型
  repeated string detected_symptoms = 3; // 检测到的症状
  repeated string follow_up_questions = 4; // 跟进问题
  float confidence = 5;         // 置信度
  map<string, string> metadata = 6; // 元数据
}
```

### 3. 结束问诊会话

#### 请求
```protobuf
message EndSessionRequest {
  string session_id = 1;        // 会话ID
  bool generate_summary = 2;    // 是否生成摘要
}
```

#### 响应
```protobuf
message InquirySummary {
  string session_id = 1;        // 会话ID
  string user_id = 2;           // 用户ID
  repeated Symptom symptoms = 3; // 症状列表
  repeated TCMPattern patterns = 4; // 证型列表
  repeated string recommendations = 5; // 建议列表
  repeated string potential_risks = 6; // 潜在风险
  float confidence = 7;         // 置信度
  int64 created_at = 8;         // 创建时间戳
}
```

### 4. 分析病史

#### 请求
```protobuf
message MedicalHistoryRequest {
  string user_id = 1;           // 用户ID
  string medical_history_text = 2; // 病史文本
}
```

#### 响应
```protobuf
message MedicalHistoryAnalysis {
  repeated Symptom chronic_symptoms = 1; // 慢性症状
  repeated Symptom acute_symptoms = 2;   // 急性症状
  repeated string key_conditions = 3;    // 关键病症
  float analysis_confidence = 4;        // 分析置信度
  map<string, string> metadata = 5;     // 元数据
}
```

### 5. 提取症状

#### 请求
```protobuf
message SymptomsExtractionRequest {
  string text = 1;              // 文本内容
  float min_confidence = 2;     // 最小置信度
}
```

#### 响应
```protobuf
message SymptomsResponse {
  repeated Symptom symptoms = 1;         // 症状列表
  repeated BodyLocation body_locations = 2; // 身体部位
  repeated TemporalFactor temporal_factors = 3; // 时间因素
  float confidence_score = 4;            // 总体置信度
}
```

### 6. 中医证型匹配

#### 请求
```protobuf
message TCMPatternMappingRequest {
  repeated string symptoms = 1;          // 症状列表
  repeated string tongue_features = 2;   // 舌象特征
  repeated string pulse_features = 3;    // 脉象特征
}
```

#### 响应
```protobuf
message TCMPatternResponse {
  repeated TCMPattern patterns = 1;      // 证型列表
  float overall_confidence = 2;          // 总体置信度
  repeated string recommendations = 3;   // 建议
}
```

### 7. 批量分析问诊数据

#### 请求
```protobuf
message BatchInquiryRequest {
  repeated SymptomsExtractionRequest extraction_requests = 1; // 批量症状提取请求
}
```

#### 响应
```protobuf
message BatchInquiryResponse {
  repeated SymptomsResponse extraction_results = 1; // 症状提取结果
  int32 success_count = 2;                        // 成功处理数量
  int32 error_count = 3;                          // 错误数量
}
```

### 8. 健康风险评估

#### 请求
```protobuf
message HealthRiskRequest {
  string user_id = 1;                            // 用户ID
  repeated string symptoms = 2;                  // 症状列表
  repeated TCMPattern patterns = 3;              // 中医证型
  map<string, string> additional_factors = 4;    // 其他因素
}
```

#### 响应
```protobuf
message HealthRiskResponse {
  repeated string risk_factors = 1;              // 风险因素
  string risk_level = 2;                         // 风险等级 (LOW, MEDIUM, HIGH)
  repeated string preventive_measures = 3;       // 预防措施
  float assessment_confidence = 4;               // 评估置信度
}
```

## 数据类型

### Symptom
```protobuf
message Symptom {
  string name = 1;              // 症状名称
  string severity = 2;          // 严重程度
  int64 onset_time = 3;         // 发病时间
  int64 duration = 4;           // 持续时间
  string description = 5;       // 描述
  float confidence = 6;         // 置信度
}
```

### BodyLocation
```protobuf
message BodyLocation {
  string name = 1;              // 部位名称
  string side = 2;              // 左/右/中央/双侧
  repeated string associated_symptoms = 3; // 关联症状
}
```

### TemporalFactor
```protobuf
message TemporalFactor {
  string factor_type = 1;       // 因素类型
  string description = 2;       // 描述
  repeated string symptoms_affected = 3; // 受影响症状
}
```

### TCMPattern
```protobuf
message TCMPattern {
  string id = 1;                // 证型ID
  string name = 2;              // 证型名称
  string english_name = 3;      // 英文名称
  string category = 4;          // 类别
  float confidence = 5;         // 置信度
  repeated string matched_symptoms = 6; // 匹配的症状
}
```

## 错误码

| 错误码 | 描述 |
|-------|------|
| 0     | 成功 |
| 1     | 未找到会话 |
| 2     | 会话已过期 |
| 3     | 用户认证失败 |
| 4     | 服务内部错误 |
| 5     | 请求参数错误 |

## 示例

### 开始会话
```python
import grpc
from inquiry_service_pb2 import StartSessionRequest
from inquiry_service_pb2_grpc import InquiryServiceStub

channel = grpc.insecure_channel('inquiry-service:50053')
stub = InquiryServiceStub(channel)

request = StartSessionRequest(
    user_id="user123",
    session_type="GENERAL"
)

response = stub.StartInquirySession(request)
print(f"会话ID: {response.session_id}")
```

### 发送消息
```python
from inquiry_service_pb2 import InteractionRequest

request = InteractionRequest(
    session_id="session123",
    user_input="我最近总是头痛，而且晚上睡不好觉"
)

for response in stub.InteractWithUser(request):
    print(f"回复: {response.response_text}")
    print(f"检测到的症状: {response.detected_symptoms}")
```

### 结束会话并获取摘要
```python
from inquiry_service_pb2 import EndSessionRequest

request = EndSessionRequest(
    session_id="session123",
    generate_summary=True
)

summary = stub.EndInquirySession(request)
print(f"检测到的症状: {[s.name for s in summary.symptoms]}")
print(f"可能的证型: {[p.name for p in summary.patterns]}")
```

### 证型匹配
```python
from inquiry_service_pb2 import TCMPatternMappingRequest

request = TCMPatternMappingRequest(
    symptoms=["头痛", "失眠", "口干", "心烦"],
    tongue_features=["舌红", "少苔"],
    pulse_features=["脉细数"]
)

response = stub.MapToTCMPatterns(request)
for pattern in response.patterns:
    print(f"证型: {pattern.name}, 置信度: {pattern.confidence}")
    print(f"匹配症状: {pattern.matched_symptoms}")
```

## 集成示例

以下是一个完整的问诊流程示例：

```python
import grpc
import json
from inquiry_service_pb2 import StartSessionRequest, InteractionRequest, EndSessionRequest
from inquiry_service_pb2_grpc import InquiryServiceStub

# 创建gRPC通道
channel = grpc.insecure_channel('inquiry-service:50053')
stub = InquiryServiceStub(channel)

# 1. 开始会话
start_request = StartSessionRequest(
    user_id="user123",
    session_type="GENERAL"
)
session_response = stub.StartInquirySession(start_request)
session_id = session_response.session_id
print(f"会话已开始，ID: {session_id}")
print(f"系统消息: {session_response.greeting_message}")

# 2. 进行多轮对话
conversations = [
    "我最近总是头痛，而且经常失眠",
    "头痛是持续性的，主要在太阳穴位置",
    "有时候会感到口干舌燥，特别是晚上",
    "我的舌头看起来比较红，舌苔很少"
]

for message in conversations:
    print(f"\n用户: {message}")
    
    # 发送消息
    interaction_request = InteractionRequest(
        session_id=session_id,
        user_input=message
    )
    
    # 接收流式响应
    for response in stub.InteractWithUser(interaction_request):
        print(f"系统: {response.response_text}")
        if response.detected_symptoms:
            print(f"检测到的症状: {response.detected_symptoms}")
        if response.follow_up_questions:
            print(f"跟进问题: {response.follow_up_questions[0]}")

# 3. 结束会话并获取总结
end_request = EndSessionRequest(
    session_id=session_id,
    generate_summary=True
)

summary = stub.EndInquirySession(end_request)
print("\n问诊总结:")
print(f"检测到的症状总数: {len(summary.symptoms)}")
print(f"可能的证型: {[p.name for p in summary.patterns]}")
print(f"建议: {summary.recommendations}")
```