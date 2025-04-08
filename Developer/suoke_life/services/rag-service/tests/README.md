# 索克生活RAG服务测试工具

## 概述

本目录包含对索克生活RAG服务进行测试的工具集，包括知识图谱推理、多模态搜索、多源检索、自适应学习以及TCM特征分析等功能测试。

## 测试类型

- **知识图谱推理测试** (`test_kg_reasoning.go`): 测试知识图谱推理功能
- **多模态搜索测试** (`test_multimodal.go`): 测试图像和音频结合文本的多模态搜索
- **多源检索测试** (`test_multi_source.go`): 测试从多个知识源检索信息
- **自适应学习测试** (`test_adaptive.go`): 测试RAG服务的自适应学习能力
- **TCM特征分析测试** (`test_tcm_features.go`): 测试中医特征提取与分析功能

## 使用方法

### 测试运行脚本

使用 `run_tests.sh` 脚本可以运行单个或多个测试:

```bash
./run_tests.sh [选项]
```

选项:
- `--mode <kg|multimodal|multi_source|adaptive|tcm|all>`: 指定要运行的测试模式
- `--verbose`: 启用详细输出
- `--clean`: 测试前清理结果目录
- `--mock`: 使用模拟模式，不需要真实服务器
- `--url <URL>`: 指定服务URL (默认: http://localhost:8080)

例如：
```bash
# 运行所有测试，使用模拟数据
./run_tests.sh --mode all --mock

# 只运行TCM特征测试，连接到特定服务器
./run_tests.sh --mode tcm --url http://118.31.223.213
```

### TCM特征分析测试

TCM特征分析测试支持以下特征类型：
- 舌诊分析 (tongue)
- 面诊分析 (face)
- 脉诊分析 (pulse)
- 声音分析 (voice)
- 体质辨识 (constitution)

单独运行TCM特征测试：

```bash
go run test_tcm_features.go -type tongue -input ./test_data/images/tongue_sample.jpg -output ./results/tongue_analysis.json

# 批量测试所有TCM特征
go run test_tcm_features.go -batch -mock -output ./results/tcm_features_batch.json
```

## 测试数据

测试数据存放在 `test_data` 目录中：
- `test_data/images`: 包含舌诊、面诊和中药材图像样本
- `test_data/audio`: 包含脉象和语音样本

## 测试结果

所有测试结果默认保存在 `test_results` 目录中，格式为JSON文件。每次测试运行都会生成带有时间戳的结果文件。

## 开发指南

### 添加新的测试用例

要添加新的TCM特征测试用例，编辑 `test_tcm_features.go` 文件中的 `tcmTestCases` 数组：

```go
var tcmTestCases = []TCMTestCase{
    {
        Name:        "新特征测试",
        FeatureType: "new_feature_type",
        InputFile:   "./test_data/path/to/sample.ext",
        Options: map[string]bool{
            "detailed": true,
        },
    },
    // 其他测试用例...
}
```

### 调试模式

使用 `-verbose` 标志可以启用详细输出，帮助调试：

```bash
go run test_tcm_features.go -type tongue -input ./test_data/images/tongue_sample.jpg -verbose
``` 