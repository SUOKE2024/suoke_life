# 索克生活无障碍服务

索克生活无障碍服务是索克生活平台的核心微服务之一，致力于提供全方位的无障碍功能支持，让所有用户都能平等地获取健康服务，不受语言、视觉、听力等障碍的限制。

## 功能特点

- **导盲服务**：基于AI视觉识别，为视障用户提供环境描述和导航指引
- **手语识别**：支持中国手语和国际手语的识别和翻译
- **屏幕阅读**：智能识别界面元素，提供上下文感知的语音导航
- **语音辅助**：支持多种语言和方言的语音交互
- **内容转换**：将健康内容转换为多种无障碍格式
- **设置管理**：个性化无障碍设置，满足不同用户需求
- **后台数据收集**：低功耗、低侵入性的健康数据采集
- **危机报警**：多级健康危机监测和智能报警
- **实时语音翻译**：多语言和方言间的实时语音翻译，支持25种语言和27种中国方言

## 技术栈

- **语言**: Python 3.11
- **框架**: gRPC, asyncio
- **AI模型**: 
  - YOLOv8-seg (场景识别)
  - MediaPipe (手语识别)
  - Whisper (语音识别)
  - MBart-50 (多语言翻译)
- **容器化**: Docker, Kubernetes
- **监控**: Prometheus, Grafana
- **日志**: ELK Stack

## 快速开始

### 环境要求

- Python 3.11+
- CUDA 11.8+ (推荐，用于GPU加速)
- 4GB+ RAM (8GB+ 推荐)

### 安装

```bash
# 克隆仓库
git clone https://github.com/SUOKE2024/accessibility-service.git
cd accessibility-service

# 安装依赖
pip install -r requirements.txt

# 安装torch (GPU版本，如果有CUDA支持)
pip install torch==2.2.1+cu118 torchaudio==2.2.1+cu118 torchvision==0.17.1+cu118 -f https://download.pytorch.org/whl/cu118/torch_stable.html
```

### 配置

主配置文件位于 `config/config.yaml`，包含服务的基本设置。
特定功能配置文件：
- `config/dialect_config.yaml` - 方言服务配置
- `config/crisis_config.yaml` - 危机报警配置
- `config/collection_config.yaml` - 数据收集配置
- `config/translation_config.yaml` - 翻译服务配置

### 运行

```bash
# 运行服务器 (本地开发模式)
python -m cmd.server.main --dev

# 使用特定配置文件运行
python -m cmd.server.main --config config/prod_config.yaml

# 运行Docker容器
docker run -p 50051:50051 suoke/accessibility-service:latest
```

### 测试API

```bash
# 测试语音翻译API
python test/client/translation_test_client.py --test simple --audio test/data/sample.wav --source_lang zh_CN --target_lang en_XX

# 测试流式翻译API
python test/client/translation_test_client.py --test stream --audio test/data/long_sample.wav
```

## API接口

服务使用gRPC提供接口，主要API包括：

- **BlindAssistance**: 导盲服务API
- **SignLanguageRecognition**: 手语识别API
- **ScreenReading**: 屏幕阅读API
- **VoiceAssistance**: 语音辅助API
- **AccessibleContent**: 内容转换API
- **ManageSettings**: 设置管理API
- **ConfigureBackgroundCollection**: 数据采集配置API
- **GetCollectionStatus**: 数据采集状态API
- **SubmitCollectedData**: 数据提交API
- **TriggerHealthAlert**: 危机报警API
- **SpeechTranslation**: 语音翻译API
- **StreamingSpeechTranslation**: 流式翻译API
- **CreateTranslationSession**: 创建翻译会话API
- **GetSessionStatus**: 获取会话状态API
- **GetSupportedLanguages**: 获取支持的语言和方言API

详细API文档请参考 `docs/api/index.html`。

## 翻译服务功能

索克生活无障碍服务的翻译功能支持多语言和方言间的实时语音翻译，主要特点包括：

### 语言支持

- 支持25种语言互译，包括中文、英语、日语、韩语等
- 集成方言识别，支持中国27种方言
- 针对医疗和中医领域术语进行了特别优化

### API功能

- **批处理翻译**: 适用于短语音翻译
- **流式翻译**: 适用于长语音和实时对话翻译
- **会话管理**: 支持创建、查询和销毁翻译会话
- **语言查询**: 获取所有支持的语言和方言列表

### 使用示例

```python
# 简单翻译示例
response = await stub.SpeechTranslation(pb2.SpeechTranslationRequest(
    audio_data=audio_data,
    user_id="user123",
    source_language="zh_CN",
    target_language="en_XX"
))
print(f"翻译结果: {response.translated_text}")

# 流式翻译示例
async for result in stub.StreamingSpeechTranslation(request_generator()):
    print(f"实时翻译: {result.translated_text}")
```

## 项目结构

```
accessibility-service/
├── api/                  # API定义和接口
│   ├── grpc/             # gRPC接口定义
│   └── rest/             # REST接口(可选)
├── cmd/                  # 命令行入口
│   └── server/           # 服务器启动脚本
├── config/               # 配置文件
├── data/                 # 数据目录
├── deploy/               # 部署配置
│   ├── docker/           # Docker配置
│   ├── kubernetes/       # Kubernetes配置
│   └── grafana/          # 监控面板配置
├── docs/                 # 文档
├── internal/             # 内部实现
│   ├── delivery/         # 传输层
│   ├── integration/      # 外部集成
│   ├── model/            # 数据模型
│   ├── observability/    # 可观测性
│   ├── platform/         # 平台适配
│   ├── repository/       # 数据访问
│   ├── resilience/       # 弹性设计
│   ├── security/         # 安全模块
│   └── service/          # 核心服务
├── logs/                 # 日志目录
├── pkg/                  # 公共包
│   └── utils/            # 工具函数
├── scripts/              # 脚本
└── test/                 # 测试
    ├── client/           # 测试客户端
    ├── data/             # 测试数据
    ├── integration/      # 集成测试
    └── platform/         # 平台测试
```

## 贡献指南

请查阅 `CONTRIBUTING.md` 了解如何参与项目开发。

## 许可证

本项目采用 MIT 许可证，详情请参阅 `LICENSE` 文件。

## 联系我们

- 官方网站: [https://suoke.life](https://suoke.life)
- 技术支持: support@suoke.life
- 问题反馈: github.com/SUOKE2024/accessibility-service/issues 