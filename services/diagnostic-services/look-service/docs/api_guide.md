# 望诊服务 API 使用指南

## 目录

- [概述](#概述)
- [API 接口列表](#api-接口列表)
- [接口详细说明](#接口详细说明)
  - [舌象分析 (AnalyzeTongue)](#舌象分析-analyzetongue)
  - [面色分析 (AnalyzeFace)](#面色分析-analyzeface)
  - [形体分析 (AnalyzeBody)](#形体分析-analyzebody)
  - [获取历史记录 (GetAnalysisHistory)](#获取历史记录-getanalysishistory)
  - [比较分析结果 (CompareAnalysis)](#比较分析结果-compareanalysis)
  - [健康检查 (HealthCheck)](#健康检查-healthcheck)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [集成示例](#集成示例)
  - [Python 集成示例](#python-集成示例)
  - [Go 集成示例](#go-集成示例)
  - [与小艾服务集成](#与小艾服务集成)
- [性能考量](#性能考量)
- [附录：常见问题解答](#附录常见问题解答)

## 概述

望诊服务是索克生活 APP 四诊合参系统的重要组成部分，专注于数字化中医"望诊"技术的实现。本服务提供舌象分析、面色分析、形体分析等功能，通过计算机视觉和深度学习技术，将传统中医的望诊方法数字化，支持智能化的健康状态评估。

服务采用 gRPC 协议，通过 Protocol Buffers 定义接口，支持高效的二进制数据传输，适合于跨语言、跨平台的调用。

## API 接口列表

望诊服务提供以下主要 API 接口：

| 接口名称 | 说明 | 适用场景 |
|---------|------|---------|
| AnalyzeTongue | 舌象分析 | 分析舌头图像，获取舌质、舌苔特征与健康关联 |
| AnalyzeFace | 面色分析 | 分析面部特征，获取面色、区域特点与脏腑关联 |
| AnalyzeBody | 形体分析 | 分析身体姿态、形体特征与健康状态关联 |
| GetAnalysisHistory | 获取历史记录 | 查询用户的历史分析记录 |
| CompareAnalysis | 比较分析结果 | 对比两次分析结果，评估健康状态变化 |
| HealthCheck | 健康检查 | 检查服务是否正常运行 |

## 接口详细说明

### 舌象分析 (AnalyzeTongue)

此接口用于分析舌头图像，识别舌质、舌苔特征，关联中医体质类型。

#### 请求参数

```protobuf
message TongueAnalysisRequest {
  bytes image = 1;                // 舌象图像二进制数据
  string user_id = 2;             // 用户ID
  AnalysisType analysis_type = 3; // 分析类型
  bool save_result = 4;           // 是否保存分析结果
  map<string, string> metadata = 5; // 元数据
}
```

**参数说明**：

- `image`: 舌头图像的二进制数据，支持 JPEG、PNG 格式
- `user_id`: 用户唯一标识，用于关联分析记录
- `analysis_type`: 分析类型枚举值
  - `BASIC`(0): 基础分析，仅包含基本特征
  - `COMPREHENSIVE`(1): 全面分析，包含所有特征和体质关联
  - `SPECIALIZED`(2): 专项分析，针对特定健康问题的深度分析
- `save_result`: 是否将分析结果保存到数据库
- `metadata`: 可选的元数据，如设备信息、环境条件等

#### 响应结果

```protobuf
message TongueAnalysisResponse {
  string request_id = 1;               // 请求ID
  string tongue_color = 2;             // 舌色
  string tongue_shape = 3;             // 舌形
  string coating_color = 4;            // 苔色
  string coating_distribution = 5;     // 苔布
  repeated string features = 6;        // 特征列表
  repeated FeatureLocation locations = 7;  // 特征位置
  repeated ConstitutionCorrelation body_constitution = 8; // 体质关联
  map<string, float> metrics = 9;      // 量化指标
  string analysis_summary = 10;        // 分析总结
  string analysis_id = 11;             // 分析记录ID
  int64 timestamp = 12;                // 时间戳
}
```

**响应字段说明**：

- `request_id`: 请求唯一标识
- `tongue_color`: 舌色，如"淡红"、"淡白"、"红"等
- `tongue_shape`: 舌形，如"正常"、"胖大"、"瘦薄"等
- `coating_color`: 舌苔颜色，如"白"、"黄"、"灰"等
- `coating_distribution`: 舌苔分布，如"薄白"、"厚腻"、"剥脱"等
- `features`: 识别到的特征列表，如"舌尖红"、"舌边齿痕"等
- `locations`: 特征在图像中的位置坐标
- `body_constitution`: 关联的中医体质类型及置信度
- `metrics`: 量化指标，如舌色饱和度、舌苔厚度等
- `analysis_summary`: 分析总结，简要描述分析结果
- `analysis_id`: 分析记录ID，用于查询或比较
- `timestamp`: 分析时间戳

#### 示例用法

```python
# 读取舌象图像
with open("tongue_image.jpg", "rb") as f:
    image_data = f.read()

# 创建请求
request = look_service_pb2.TongueAnalysisRequest(
    image=image_data,
    user_id="user123",
    analysis_type=look_service_pb2.AnalysisType.COMPREHENSIVE,
    save_result=True,
    metadata={"device_type": "mobile", "app_version": "1.2.0"}
)

# 发送请求
response = stub.AnalyzeTongue(request)

# 处理响应
print(f"舌色: {response.tongue_color}")
print(f"舌苔: {response.coating_color}，{response.coating_distribution}")
print(f"体质分析: {[c.constitution_type for c in response.body_constitution]}")
print(f"分析总结: {response.analysis_summary}")
```

### 面色分析 (AnalyzeFace)

此接口用于分析面部图像，识别面色特征，关联脏腑功能状态和中医体质类型。

#### 请求参数

```protobuf
message FaceAnalysisRequest {
  bytes image = 1;                // 面部图像二进制数据
  string user_id = 2;             // 用户ID
  AnalysisType analysis_type = 3; // 分析类型
  bool save_result = 4;           // 是否保存分析结果
  map<string, string> metadata = 5; // 元数据
}
```

**参数说明**同舌象分析请求，只是图像内容为面部。

#### 响应结果

```protobuf
message FaceAnalysisResponse {
  string request_id = 1;               // 请求ID
  string face_color = 2;               // 整体面色
  repeated FaceRegionAnalysis regions = 3; // 区域分析
  repeated string features = 4;        // 特征列表
  repeated ConstitutionCorrelation body_constitution = 5; // 体质关联
  repeated OrganCorrelation organ_correlations = 6; // 脏腑关联
  string analysis_summary = 7;         // 分析总结
  string analysis_id = 8;              // 分析记录ID
  int64 timestamp = 9;                 // 时间戳
}
```

**响应字段说明**：

- `request_id`: 请求唯一标识
- `face_color`: 整体面色，如"红润"、"苍白"、"萎黄"等
- `regions`: 面部区域分析结果，包含额头、两颊、鼻子等区域的颜色和特征
- `features`: 识别到的特征列表
- `body_constitution`: 关联的中医体质类型及置信度
- `organ_correlations`: 面部区域与脏腑关联分析结果
- `analysis_summary`: 分析总结
- `analysis_id`: 分析记录ID
- `timestamp`: 分析时间戳

### 形体分析 (AnalyzeBody)

此接口用于分析全身图像，识别形体特征和姿态，关联中医体质类型。

#### 请求参数

```protobuf
message BodyAnalysisRequest {
  bytes image = 1;                // 全身图像二进制数据
  string user_id = 2;             // 用户ID
  AnalysisType analysis_type = 3; // 分析类型
  bool save_result = 4;           // 是否保存分析结果
  map<string, string> metadata = 5; // 元数据
}
```

**参数说明**同上，只是图像内容为全身。

#### 响应结果

```protobuf
message BodyAnalysisResponse {
  string request_id = 1;               // 请求ID
  string body_type = 2;                // 体型
  repeated BodyFeature features = 3;   // 特征列表
  repeated PostureAnalysis posture = 4; // 姿态分析
  repeated ConstitutionCorrelation body_constitution = 5; // 体质关联
  string analysis_summary = 6;         // 分析总结
  string analysis_id = 7;              // 分析记录ID
  int64 timestamp = 8;                 // 时间戳
}
```

**响应字段说明**：

- `request_id`: 请求唯一标识
- `body_type`: 体型分类，如"偏瘦"、"中等"、"偏胖"等
- `features`: 识别到的形体特征
- `posture`: 姿态分析结果，包含站姿、坐姿等
- `body_constitution`: 关联的中医体质类型及置信度
- `analysis_summary`: 分析总结
- `analysis_id`: 分析记录ID
- `timestamp`: 分析时间戳

### 获取历史记录 (GetAnalysisHistory)

此接口用于查询用户的历史分析记录。

#### 请求参数

```protobuf
message AnalysisHistoryRequest {
  string user_id = 1;             // 用户ID
  string analysis_type = 2;       // 分析类型: "tongue", "face", "body"
  int32 limit = 3;                // 返回记录数量限制
  int64 start_time = 4;           // 开始时间戳
  int64 end_time = 5;             // 结束时间戳
}
```

**参数说明**：

- `user_id`: 用户唯一标识
- `analysis_type`: 分析类型字符串，可为"tongue"、"face"或"body"
- `limit`: 返回记录的最大数量
- `start_time`: 查询时间范围的开始时间戳
- `end_time`: 查询时间范围的结束时间戳

#### 响应结果

```protobuf
message AnalysisHistoryResponse {
  repeated AnalysisRecord records = 1; // 历史记录
  int32 total_count = 2;              // 总记录数
}

message AnalysisRecord {
  string analysis_id = 1;          // 分析ID
  string analysis_type = 2;        // 分析类型
  int64 timestamp = 3;             // 时间戳
  string summary = 4;              // 摘要
  bytes thumbnail = 5;             // 缩略图
}
```

**响应字段说明**：

- `records`: 分析记录列表
- `total_count`: 符合条件的总记录数

每条记录包含：
- `analysis_id`: 分析记录ID
- `analysis_type`: 分析类型
- `timestamp`: 分析时间戳
- `summary`: 分析结果摘要
- `thumbnail`: 分析图像的缩略图

### 比较分析结果 (CompareAnalysis)

此接口用于比较同一用户的两次分析结果，评估健康状态变化。

#### 请求参数

```protobuf
message CompareAnalysisRequest {
  string user_id = 1;              // 用户ID
  string analysis_type = 2;        // 分析类型: "tongue", "face", "body"
  string first_analysis_id = 3;    // 第一个分析ID
  string second_analysis_id = 4;   // 第二个分析ID
}
```

**参数说明**：

- `user_id`: 用户唯一标识
- `analysis_type`: 分析类型字符串
- `first_analysis_id`: 第一次分析的记录ID（较早的记录）
- `second_analysis_id`: 第二次分析的记录ID（较新的记录）

#### 响应结果

```protobuf
message CompareAnalysisResponse {
  repeated FeatureComparison feature_comparisons = 1; // 特征比较
  repeated string improvements = 2;                  // 改善项
  repeated string deteriorations = 3;                // 恶化项
  repeated string unchanged = 4;                     // 未变项
  string comparison_summary = 5;                     // 比较总结
}

message FeatureComparison {
  string feature_name = 1;       // 特征名称
  string first_value = 2;        // 第一个值
  string second_value = 3;       // 第二个值
  float change_percentage = 4;   // 变化百分比
  string change_direction = 5;   // 变化方向: "improved", "deteriorated", "unchanged"
}
```

**响应字段说明**：

- `feature_comparisons`: 各项特征的详细比较结果
- `improvements`: 改善的项目列表
- `deteriorations`: 恶化的项目列表
- `unchanged`: 未变的项目列表
- `comparison_summary`: 比较总结

### 健康检查 (HealthCheck)

此接口用于检查服务是否正常运行。

#### 请求参数

```protobuf
message HealthCheckRequest {
  bool include_details = 1;      // 是否包含详细信息
}
```

**参数说明**：

- `include_details`: 是否在响应中包含服务详细状态信息

#### 响应结果

```protobuf
message HealthCheckResponse {
  enum Status {
    UNKNOWN = 0;
    SERVING = 1;
    NOT_SERVING = 2;
  }
  Status status = 1;               // 服务状态
  map<string, string> details = 2; // 详细状态信息
}
```

**响应字段说明**：

- `status`: 服务状态枚举值
  - `UNKNOWN`(0): 未知状态
  - `SERVING`(1): 服务正常
  - `NOT_SERVING`(2): 服务异常
- `details`: 当`include_details`为`true`时，返回详细的服务状态信息

## 错误处理

望诊服务使用标准的 gRPC 错误码进行错误报告，常见错误码如下：

| 错误码 | 说明 | 处理建议 |
|-------|-----|---------|
| INVALID_ARGUMENT | 请求参数无效 | 检查请求参数格式和值是否符合要求 |
| NOT_FOUND | 找不到请求的资源 | 确认资源ID是否正确 |
| PERMISSION_DENIED | 权限不足 | 检查身份验证信息 |
| RESOURCE_EXHAUSTED | 资源超限 | 减少请求频率或联系管理员调整配额 |
| INTERNAL | 服务器内部错误 | 联系服务管理员，提供错误详情 |
| UNAVAILABLE | 服务暂时不可用 | 稍后重试，或检查服务状态 |

建议在调用服务时实现适当的重试和回退机制，特别是对于`RESOURCE_EXHAUSTED`和`UNAVAILABLE`错误。

## 最佳实践

1. **图像质量控制**：
   - 舌头图像应当在光线充足的环境下拍摄
   - 确保图像清晰，无严重模糊
   - 舌头应完全伸出，显示舌面和舌质
   - 避免使用滤镜或过度编辑的图像

2. **调用频率**：
   - 对同一用户的同一类分析，建议间隔至少1小时
   - 批量分析请求应控制速率，避免触发限流

3. **错误处理**：
   - 实现指数退避重试逻辑处理临时错误
   - 对于图像质量问题，提示用户重新拍摄而非重试

4. **数据存储**：
   - 对于重要分析结果，应在客户端保存本地副本
   - 重要结果数据应加密存储

## 集成示例

### Python 集成示例

```python
import grpc
from api.grpc import look_service_pb2, look_service_pb2_grpc
import cv2
import numpy as np
import time
from datetime import datetime

# 创建gRPC连接
channel = grpc.insecure_channel('localhost:50051')
stub = look_service_pb2_grpc.LookServiceStub(channel)

def analyze_tongue_image(image_path, user_id):
    """分析舌象图像"""
    try:
        # 读取并预处理图像
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
            
        # 图像质量检查
        if img.shape[0] < 300 or img.shape[1] < 300:
            print("警告: 图像分辨率过低，可能影响分析结果")
            
        # 转换为JPEG二进制数据
        _, img_encoded = cv2.imencode('.jpg', img)
        img_bytes = img_encoded.tobytes()
        
        # 创建请求
        request = look_service_pb2.TongueAnalysisRequest(
            image=img_bytes,
            user_id=user_id,
            analysis_type=look_service_pb2.AnalysisType.COMPREHENSIVE,
            save_result=True,
            metadata={
                "timestamp": str(int(time.time())),
                "source": "mobile_app"
            }
        )
        
        # 发送请求
        print("正在分析舌象...")
        response = stub.AnalyzeTongue(request)
        
        # 处理响应
        print("\n===== 舌象分析结果 =====")
        print(f"舌色: {response.tongue_color}")
        print(f"舌形: {response.tongue_shape}")
        print(f"舌苔: {response.coating_color} {response.coating_distribution}")
        print("\n识别到的特征:")
        for feature in response.features:
            print(f"- {feature}")
            
        print("\n体质关联:")
        for constitution in response.body_constitution:
            print(f"- {constitution.constitution_type}: {constitution.confidence:.2f}")
            print(f"  {constitution.description}")
            
        print(f"\n分析总结: {response.analysis_summary}")
        print(f"分析ID: {response.analysis_id}")
        print(f"分析时间: {datetime.fromtimestamp(response.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        return response
        
    except grpc.RpcError as e:
        status_code = e.code()
        details = e.details()
        print(f"gRPC错误: {status_code} - {details}")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    result = analyze_tongue_image("examples/tongue/sample1.jpg", "user1234")
    
    if result:
        # 保存分析ID用于后续查询或比较
        with open("analysis_records.txt", "a") as f:
            f.write(f"{result.analysis_id},{result.timestamp},tongue,{result.analysis_summary}\n")
```

### Go 集成示例

```go
package main

import (
    "context"
    "fmt"
    "io/ioutil"
    "log"
    "time"
    
    "google.golang.org/grpc"
    pb "github.com/SUOKE2024/look-service/api/grpc"
)

func main() {
    // 创建gRPC连接
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("无法连接服务: %v", err)
    }
    defer conn.Close()
    
    // 创建客户端
    client := pb.NewLookServiceClient(conn)
    
    // 读取舌象图像
    imageData, err := ioutil.ReadFile("examples/tongue/sample1.jpg")
    if err != nil {
        log.Fatalf("读取图像失败: %v", err)
    }
    
    // 创建上下文
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    
    // 创建请求
    req := &pb.TongueAnalysisRequest{
        Image:        imageData,
        UserId:       "user1234",
        AnalysisType: pb.AnalysisType_COMPREHENSIVE,
        SaveResult:   true,
        Metadata: map[string]string{
            "timestamp": fmt.Sprintf("%d", time.Now().Unix()),
            "source":    "desktop_app",
        },
    }
    
    // 发送请求
    fmt.Println("正在分析舌象...")
    resp, err := client.AnalyzeTongue(ctx, req)
    if err != nil {
        log.Fatalf("分析失败: %v", err)
    }
    
    // 处理响应
    fmt.Println("\n===== 舌象分析结果 =====")
    fmt.Printf("舌色: %s\n", resp.TongueColor)
    fmt.Printf("舌形: %s\n", resp.TongueShape)
    fmt.Printf("舌苔: %s %s\n", resp.CoatingColor, resp.CoatingDistribution)
    
    fmt.Println("\n识别到的特征:")
    for _, feature := range resp.Features {
        fmt.Printf("- %s\n", feature)
    }
    
    fmt.Println("\n体质关联:")
    for _, constitution := range resp.BodyConstitution {
        fmt.Printf("- %s: %.2f\n", constitution.ConstitutionType, constitution.Confidence)
        fmt.Printf("  %s\n", constitution.Description)
    }
    
    fmt.Printf("\n分析总结: %s\n", resp.AnalysisSummary)
    fmt.Printf("分析ID: %s\n", resp.AnalysisId)
    fmt.Printf("分析时间: %s\n", time.Unix(resp.Timestamp, 0).Format("2006-01-02 15:04:05"))
}
```

### 与小艾服务集成

望诊服务通常与小艾服务配合使用，形成完整的四诊合参系统。以下示例演示如何将望诊结果发送至小艾服务以进行综合诊断：

```python
import grpc
from api.grpc import look_service_pb2, look_service_pb2_grpc
from integration.xiaoai_service.api.grpc import xiaoai_service_pb2, xiaoai_service_pb2_grpc

# 创建望诊服务连接
look_channel = grpc.insecure_channel('localhost:50051')
look_stub = look_service_pb2_grpc.LookServiceStub(look_channel)

# 创建小艾服务连接
xiaoai_channel = grpc.insecure_channel('localhost:50052')
xiaoai_stub = xiaoai_service_pb2_grpc.XiaoaiServiceStub(xiaoai_channel)

def perform_integrated_diagnosis(user_id, image_path):
    """执行集成诊断流程"""
    try:
        # 1. 调用望诊服务进行舌象分析
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        tongue_request = look_service_pb2.TongueAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=look_service_pb2.AnalysisType.COMPREHENSIVE,
            save_result=True
        )
        
        tongue_response = look_stub.AnalyzeTongue(tongue_request)
        print(f"舌象分析完成: {tongue_response.analysis_summary}")
        
        # 2. 将舌象分析结果发送至小艾服务
        xiaoai_request = xiaoai_service_pb2.IntegrateDiagnosticRequest(
            user_id=user_id,
            diagnostic_type="tongue",
            analysis_id=tongue_response.analysis_id,
            diagnostic_summary=tongue_response.analysis_summary,
            diagnostic_time=tongue_response.timestamp,
            diagnostic_details={
                "tongue_color": tongue_response.tongue_color,
                "tongue_shape": tongue_response.tongue_shape,
                "coating_color": tongue_response.coating_color,
                "coating_distribution": tongue_response.coating_distribution,
                "features": ",".join(tongue_response.features)
            }
        )
        
        # 3. 接收小艾服务的整合分析结果
        xiaoai_response = xiaoai_stub.IntegrateDiagnostic(xiaoai_request)
        
        print("\n===== 小艾整合诊断结果 =====")
        print(f"整合ID: {xiaoai_response.integration_id}")
        print(f"诊断结果: {xiaoai_response.diagnostic_result}")
        print(f"推荐方案: {xiaoai_response.recommendation}")
        
        return xiaoai_response
        
    except Exception as e:
        print(f"整合诊断过程中出错: {e}")
        return None

# 使用示例
perform_integrated_diagnosis("user1234", "examples/tongue/sample1.jpg")
```

## 性能考量

望诊服务在处理图像和运行深度学习模型时需要大量计算资源，因此存在一定的延迟。以下是各接口的典型性能特征：

| 接口名称 | 典型响应时间 | 资源消耗 | 并发能力 |
|---------|-----------|---------|---------|
| AnalyzeTongue | 300-600ms | 中等 | 每节点20-30 QPS |
| AnalyzeFace | 400-700ms | 高 | 每节点15-25 QPS |
| AnalyzeBody | 500-800ms | 高 | 每节点10-20 QPS |
| GetAnalysisHistory | 50-100ms | 低 | 每节点100+ QPS |
| CompareAnalysis | 100-200ms | 低 | 每节点50+ QPS |
| HealthCheck | <20ms | 极低 | 每节点500+ QPS |

**优化建议**：

1. **客户端优化**：
   - 在分析前预处理图像，调整尺寸和质量
   - 实现请求缓冲和批处理
   - 实现指数退避重试

2. **服务配置**：
   - 根据实际负载配置适当的副本数
   - 为分析服务配置GPU资源
   - 设置合理的超时时间和重试策略

## 附录：常见问题解答

### Q1: 图像质量对分析结果有何影响？

**A**: 图像质量是准确分析的关键因素。低质量图像（模糊、曝光不当、角度不正）会显著降低分析准确度。建议在光线充足的环境下，保持正确的拍摄角度和距离，确保图像清晰且完整显示目标区域。

### Q2: 如何处理分析失败的情况？

**A**: 分析失败可能由多种原因导致，如图像质量问题、服务过载或网络异常。建议：
- 对临时性错误实现重试机制
- 记录详细错误信息以便排查
- 向用户提供具体反馈，指导如何改进（如重新拍摄）
- 在重要流程中实现降级机制，如使用缓存的分析结果

### Q3: 服务支持批量处理请求吗？

**A**: 当前版本不支持单一请求中批量处理多张图像。如需批量分析，建议:
- 使用客户端队列管理多个请求
- 控制并发请求数量，避免触发服务限流
- 实现请求结果的本地聚合

### Q4: 如何进行服务访问授权？

**A**: 望诊服务使用API Key进行授权。请联系服务管理员获取有效的API Key，并在每次请求的元数据中包含`api_key`字段。

### Q5: 分析结果的准确性如何评估？

**A**: 望诊服务的分析结果基于大量临床数据训练的模型，准确度取决于多种因素：
- 模型版本（较新版本通常更准确）
- 图像质量
- 具体分析类型

当前版本的准确度指标：
- 舌象基本特征识别: 85-90%
- 面色分析: 80-85%
- 体质类型关联: 75-80%

---

*如有其他问题或需要进一步支持，请联系技术支持团队: support@suoke.life* 