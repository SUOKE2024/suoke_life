# SuokeBench 评测系统服务

SuokeBench 是索克生活APP的专属评测体系，旨在系统性衡量索克生活APP及四大智能体（小艾、小克、老克、索儿）的功能完备度、智能水平与用户体验。

![SuokeBench版本](https://img.shields.io/badge/版本-v1.0-blue)
![支持平台](https://img.shields.io/badge/平台-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
![Python版本](https://img.shields.io/badge/Python->=3.9-green)
![许可证](https://img.shields.io/badge/许可证-MIT-orange)

## 功能概述

SuokeBench 评测系统提供以下核心功能：

1. **多维度评测**: 全面覆盖中医五诊准确性、健康管理方案生成、多智能体协作、隐私安全和端侧性能等关键维度
2. **模型集成**: 支持集成本地模型和远程API模型，便于不同模型实现的灵活接入
3. **可视化分析**: 提供丰富直观的评测报告和结果可视化
4. **智能体协作评估**: 专门设计的多智能体协作评测指标和方法
5. **标准化API**: 提供完善的REST和gRPC接口，方便集成至开发流水线
6. **用户友好界面**: 提供Web界面可视化展示评测结果和历史数据

## 目录结构

```
suoke-bench-service/
├── api/                    # API定义
│   └── grpc/              # gRPC接口
├── cmd/                    # 入口点
│   └── server/            # 服务启动
├── internal/              # 内部代码
│   ├── benchmark/         # 基准测试引擎
│   ├── evaluation/        # 评估数据分析
│   ├── metrics/           # 性能指标定义
│   └── suokebench/        # SuokeBench自研评测框架
├── config/                # 配置文件
├── data/                  # 测试数据
│   ├── tcm-5d/            # 中医五诊数据集
│   ├── health-plan/       # 健康方案数据集
│   ├── agent-dialogue/    # 智能体对话数据集
│   └── privacy-zkp/       # 隐私与安全测试数据集
├── deploy/                # 部署配置
├── pkg/                   # 公共包
│   └── utils/            # 工具函数
└── test/                  # 测试代码
```

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/suoke-bench-service

# 安装依赖
uv sync

# 启动服务
uv run uvicorn cmd.server.main:app --reload --host 0.0.0.0 --port 8000
```

### 初始化环境

首次使用需要设置评测环境：

```bash
# 设置评测环境
make bench.setup

# 或手动运行
python -m internal.suokebench.setup
```

### 访问API文档

启动服务后，可以访问以下地址查看API文档：

- REST API: http://localhost:8000/docs
- gRPC API: 可使用类似grpcurl等工具查看

### 运行评测

```bash
# 运行全部评测
make bench.run

# 或手动运行
python -m internal.suokebench.runner

# 运行CI评测（子集）
make bench.ci

# 生成HTML报告（假设run_id为run_1234567890）
make bench.report run_id=run_1234567890 format=html
```

## 数据集

SuokeBench 评测系统使用四个核心数据集：

1. **TCM-5D Dataset**: 包含舌象图片20k、面色视频5k、脉波形10k、语音问诊记录50h，用于中医五诊模型评测。
2. **HealthPlan-TCM**: 结合9种体质与6大生活场景的健康管理案例5k条，用于健康方案生成评测。
3. **SuokeDialogue**: 多智能体协作对话3k轮，用于评估智能体协同效率。
4. **Privacy-ZKP Set**: 100组零知识证明与异常场景，用于验证隐私保护模块。

您可以通过以下命令下载示例数据集：

```bash
# 下载所有示例数据集
python -m internal.suokebench.setup --download-data all

# 下载特定数据集
python -m internal.suokebench.setup --download-data tcm-5d
```

## API使用示例

### REST API

```python
import requests
import json

# 运行评测
response = requests.post(
    "http://localhost:8000/api/run",
    json={
        "benchmark_id": "tongue_recognition_bench",
        "model_id": "tongue_classifier",
        "model_version": "v1.0",
        "parameters": {"threshold": "0.75"}
    }
)
run_id = response.json()["run_id"]

# 获取结果
result = requests.post(
    "http://localhost:8000/api/result",
    json={"run_id": run_id, "include_details": True}
).json()

# 生成报告
report = requests.post(
    "http://localhost:8000/api/report",
    json={"run_id": run_id, "format": "html", "include_samples": True}
).json()

# 获取报告URL
report_url = report["report_url"]
```

### Python客户端

```python
from internal.benchmark.client import SuokeBenchClient

# 创建客户端
client = SuokeBenchClient("localhost:8000")

# 运行评测
run_id = client.run_benchmark(
    benchmark_id="tongue_recognition_bench",
    model_id="tongue_classifier",
    model_version="v1.0"
)

# 获取结果
result = client.get_result(run_id)

# 显示关键指标
for metric_name, metric_value in result["metrics"].items():
    print(f"{metric_name}: {metric_value['value']}")
```

## 评测指标

SuokeBench 包含多种类型的评测指标：

### 基础指标

- **准确率 (Accuracy)**: 预测正确的样本比例
- **精确率 (Precision)**: 真正例占所有预测为正例的比例
- **召回率 (Recall)**: 真正例占所有实际为正例的比例
- **F1分数 (F1-Score)**: 精确率和召回率的调和平均值

### 中医辨证指标

- **舌象分类准确率**: 舌象特征识别的准确性评估
- **辩证准确率**: 中医体质辨识的准确性评估

### 性能指标

- **延迟 (Latency)**: 模型推理的平均延迟时间
- **吞吐量 (Throughput)**: 每秒处理的样本数

### 多智能体协作指标

- **协作效率**: 智能体间信息传递和决策效率
- **分工均衡度**: 智能体参与度和任务分配均衡性

### 隐私安全指标

- **隐私泄露率**: 敏感信息的防护能力
- **零知识证明正确率**: 零知识证明验证的准确性

## 自定义评测

您可以通过几个简单步骤创建自定义评测：

1. **定义配置**: 在`config/benchmarks/`目录中创建配置文件
2. **准备数据集**: 按格式要求准备评测数据集
3. **实现指标**: 如需自定义指标，在`internal/metrics/`中实现
4. **注册评测**: 在配置中注册新评测

配置示例:

```yaml
benchmarks:
  custom_benchmark:
    name: "自定义评测"
    description: "这是一个自定义评测示例"
    task: "TCM_DIAGNOSIS"
    datasets: ["custom_dataset"]
    metrics: ["accuracy", "precision", "recall", "f1"]
    parameters:
      threshold:
        description: "分类阈值"
        default: "0.5"
```

## 集成CI/CD

SuokeBench 可以轻松集成到 CI/CD 流水线中，以确保模型质量：

### GitHub Actions示例

```yaml
name: Model Benchmark

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          uv sync
      - name: Run benchmarks
        run: |
          python -m internal.suokebench.runner --ci
      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: data/results/
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t suoke-bench-service .

# 运行容器
docker run -p 8000:8000 -p 50051:50051 suoke-bench-service
```

### Kubernetes部署

```bash
# 应用部署配置
kubectl apply -f deploy/kubernetes/suoke-bench.yaml
```

## 扩展SuokeBench

### 添加新指标

1. 在`internal/metrics/`下创建指标实现文件
2. 在`metric_registry.py`中注册您的指标
3. 在配置中将指标添加到相关评测中

### 添加新模型类型

1. 在`internal/benchmark/model_interface.py`中实现新的模型接口
2. 在模型工厂方法中添加新类型的支持

## 联系与支持

- **问题反馈**: [GitHub Issues](https://github.com/SUOKE2024/suoke_life/issues)
- **技术支持**: song.xu@icloud.com

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件