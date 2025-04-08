# TCM特征测试指南

## 概述

TCM特征测试模块用于测试索克生活RAG服务对中医特色功能的支持，包括舌诊分析、面诊分析、脉诊分析、声音分析和体质辨识等特征。该测试模块可以验证服务的特征提取能力、分析准确性和响应速度。

## 功能特点

- **多模态分析**：支持图像（舌诊、面诊）和音频（脉诊、声音）多模态分析
- **特征提取**：从输入数据中提取关键中医特征
- **诊断结果**：生成初步中医诊断建议
- **批量测试**：支持多个测试用例批量运行
- **Mock模式**：支持离线模拟测试，无需连接实际服务

## 测试用例

当前支持的测试用例包括：

1. **舌诊分析**：分析舌象特征，包括舌色、舌苔、舌形、舌态等
2. **面诊分析**：分析面色、面形、气色等特征
3. **脉诊分析**：分析脉象、脉率、脉势等特征
4. **声音分析**：分析声音特征，包括音调、音量、清晰度等
5. **体质辨识**：根据综合特征判断体质类型

## 使用方法

### 独立运行

可以独立运行测试脚本对特定特征进行测试：

```bash
# 舌诊分析测试
go run test_tcm_features.go -type tongue -input ./test_data/images/tongue_sample.jpg -output ./results/tongue.json

# 面诊分析测试
go run test_tcm_features.go -type face -input ./test_data/images/face_sample.jpg -output ./results/face.json

# 脉诊分析测试
go run test_tcm_features.go -type pulse -input ./test_data/audio/pulse_sample.mp3 -output ./results/pulse.json

# 声音分析测试
go run test_tcm_features.go -type voice -input ./test_data/audio/voice_sample.mp3 -output ./results/voice.json

# 体质辨识测试（不需要输入文件）
go run test_tcm_features.go -type constitution -output ./results/constitution.json
```

### 批量测试

使用批量模式可以一次运行所有测试用例：

```bash
# 模拟模式批量测试
go run test_tcm_features.go -batch -mock -output ./results/tcm_batch.json

# 连接真实服务批量测试
go run test_tcm_features.go -batch -url http://example.com -output ./results/tcm_batch.json
```

### 与测试框架集成

TCM特征测试已集成到整体测试框架中，可以通过run_tests.sh脚本运行：

```bash
# 仅运行TCM特征测试
./run_tests.sh --mode tcm --mock

# 将TCM特征测试作为完整测试套件的一部分运行
./run_tests.sh --mode all
```

## 参数说明

测试脚本支持以下命令行参数：

- `-type`：特征类型，可选值为tongue、face、pulse、voice、constitution
- `-input`：输入文件路径（舌诊和面诊使用图像文件，脉诊和声音使用音频文件）
- `-output`：输出结果文件路径
- `-url`：服务URL，默认为http://localhost:8080/api/analyze/{特征类型}
- `-verbose`：开启详细输出
- `-mock`：使用模拟数据，不连接实际服务
- `-batch`：批量测试模式

## 结果解读

测试结果为JSON格式，包含以下主要字段：

- `status`：分析状态（success或error）
- `features`：提取的特征数据
- `metadata`：元数据信息
- `error`：错误信息（如果有）

特征数据根据不同特征类型有不同的结构，例如：

### 舌诊特征示例

```json
{
  "status": "success",
  "features": {
    "tongue_analysis": {
      "color": "淡红舌",
      "coating": "薄白苔",
      "shape": "正常",
      "moisture": 0.75,
      "cracks": [
        {"position": "center", "size": "小", "depth": "浅"}
      ],
      "diagnosis": {
        "primary": "气虚",
        "secondary": "阴虚"
      }
    },
    "analyzed_at": "2024-04-07T10:15:30+08:00",
    "model": "suoke-tcm-v2.0"
  }
}
```

## 扩展测试

### 添加新的测试用例

要添加新的测试用例，编辑`test_tcm_features.go`文件中的`tcmTestCases`数组：

```go
var tcmTestCases = []TCMTestCase{
    // 添加新的测试用例
    {
        Name:        "新测试用例",
        FeatureType: "feature_type",
        InputFile:   "./test_data/path/to/sample.ext",
        Options: map[string]bool{
            "detailed": true,
            "option1": true,
        },
    },
    // 其他测试用例...
}
```

### 支持新的特征类型

要支持新的特征类型，需要在`generateMockResponse`函数中添加相应的模拟数据生成逻辑：

```go
func generateMockResponse(req AnalysisRequest) (AnalysisResponse, error) {
    // ...现有代码...
    
    switch req.FeatureType {
    // ...现有特征类型...
    case "new_feature_type":
        response.Features["new_feature_analysis"] = map[string]interface{}{
            // 新特征的模拟数据
            "feature1": "value1",
            "feature2": 0.85,
            // ...其他特征...
        }
    }
    
    return response, nil
}
```

## 故障排除

如果遇到测试问题，可以尝试以下解决方法：

1. 使用`-verbose`参数获取详细输出，查看请求和响应详情
2. 检查测试数据文件是否存在且格式正确
3. 确认服务URL是否正确且可访问
4. 如果连接真实服务出现问题，可以使用`-mock`模式进行隔离测试 