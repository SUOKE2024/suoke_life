# 闻诊服务 (Listen Service)

闻诊服务是索克生活 APP 的核心微服务之一，负责中医四诊中的"闻"诊环节。该服务专注于音频处理和分析，提供语音特征提取、声音分析、情绪识别、方言检测和语音转写等功能，为智能体小艾提供听觉感知能力。

**开发状态：已完成 (100%)**

## 功能特点

- **语音特征分析**：分析语音中的特征（如音调、语速、气息特征等），提取中医相关特性
- **声音分析**：识别和分析非语言声音（如咳嗽声、呼吸声、心音等）
- **情绪分析**：从语音中分析情绪状态，支持中医五志（喜、怒、忧、思、恐）分析
- **方言检测**：识别用户使用的方言类型及地区
- **语音转写**：将语音转换为文本，支持后续的文本分析
- **批量分析**：支持一次请求进行多种音频分析，提高效率
- **四诊合参**：与其他诊断服务（望诊、问诊、切诊）集成，支持中医四诊合参

## 技术栈

- **开发语言**：Python 3.10+
- **框架**：gRPC, FastAPI
- **音频处理**：librosa, parselmouth, soundfile
- **机器学习**：PyTorch, scikit-learn
- **数据存储**：MongoDB
- **缓存**：Redis
- **监控**：Prometheus, Grafana
- **容器化**：Docker, Kubernetes
- **消息队列**：Kafka

## 架构设计

闻诊服务采用分层架构设计：

- **API 层**：提供 gRPC 接口，定义在 `api/grpc/listen_service.proto`
- **交付层**：实现 gRPC 服务接口，位于 `internal/delivery/`
- **核心层**：包含音频处理和分析核心逻辑，位于 `internal/audio/`
- **集成层**：负责与其他服务集成，实现四诊合参，位于 `internal/integration/`
- **存储层**：负责数据持久化，位于 `internal/repository/`
- **模型层**：定义数据模型，位于 `internal/model/`
- **工具层**：提供配置加载、指标收集等功能，位于 `pkg/utils/`

## 系统要求

- Python 3.10 或更高版本
- 至少 4GB RAM
- 支持 CUDA 的 GPU（推荐用于生产环境）
- 足够的磁盘空间用于模型存储（约 2GB）

## 快速开始

### 使用 Docker Compose

```bash
# 克隆仓库
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/listen-service

# 创建环境变量文件
cp .env-example .env

# 启动服务
docker-compose up -d
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python cmd/server.py
```

## 模型训练

服务需要多个机器学习模型，可通过提供的训练脚本进行训练：

```bash
# 训练语音特征分析模型
python scripts/model_training/train_voice_model.py \
    --data_dir /path/to/voice/dataset \
    --config config/model_training/voice_model.yaml \
    --output_dir models/voice_feature_analyzer

# 训练声音分析模型
python scripts/model_training/train_sound_model.py \
    --data_dir /path/to/sound/dataset \
    --config config/model_training/sound_model.yaml \
    --output_dir models/sound_feature_analyzer

# 训练情绪分析模型
python scripts/model_training/train_emotion_model.py \
    --data_dir /path/to/emotion/dataset \
    --config config/model_training/emotion_model.yaml \
    --output_dir models/emotion_detector
```

更多模型训练详情请参阅 `docs/models.md` 文档。

## API 文档

服务使用 gRPC 协议，API 定义位于 `api/grpc/listen_service.proto`。主要接口包括：

- `AnalyzeVoice`：分析语音特征
- `AnalyzeSound`：分析非语言声音
- `AnalyzeEmotion`：分析情绪
- `DetectDialect`：检测方言
- `TranscribeAudio`：语音转写
- `BatchAnalyze`：批量分析
- `HealthCheck`：健康检查

## 集成与四诊合参

闻诊服务支持与其他诊断服务的集成，实现中医四诊合参。主要集成点：

- **与小艾服务集成**：提供诊断结果给智能体小艾
- **与问诊服务集成**：结合问诊结果增强诊断准确性
- **与望诊服务集成**：结合望诊结果进行综合分析
- **与切诊服务集成**：结合切诊结果提高诊断完整性

集成配置位于 `config/integration.yaml`，集成实现位于 `internal/integration/` 目录。

## 性能测试

服务提供性能测试工具，位于 `test/performance/load_test.py`，可用于测试服务在高负载下的表现：

```bash
# 运行负载测试
python test/performance/load_test.py \
    --host localhost \
    --port 50052 \
    --test-data /path/to/test/audio \
    --total-requests 1000 \
    --concurrency 20 \
    --output-dir ./test_results
```

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t suoke/listen-service:latest .

# 运行容器
docker run -d -p 50052:50052 -p 9090:9090 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/models:/app/models \
  --name listen-service suoke/listen-service:latest
```

### Kubernetes 部署

```bash
# 部署到 Kubernetes
kubectl apply -f deploy/kubernetes/listen-service.yaml
```

## 监控

服务提供 Prometheus 指标，可通过 `/metrics` 端点访问。主要指标包括：

- 请求计数和延迟
- 音频处理时间和大小
- 模型推理时间和置信度
- 资源使用情况（CPU、内存、GPU）
- 错误计数和类型

预配置的 Grafana 仪表盘位于 `deploy/grafana/dashboards/`。

## 配置

配置文件位于 `config/` 目录，包括以下主要配置文件：

- `config.yaml`：主要服务配置
- `integration.yaml`：服务集成配置
- `tcm_knowledge/feature_constitution_map.json`：声音特征与中医体质映射关系

## 文档

详细文档位于 `docs/` 目录：

- `models.md`：模型详细说明
- `api/`：API 使用说明
- `development/`：开发指南
- `testing/`：测试指南

## 贡献

欢迎贡献代码、报告问题或提出改进建议。请遵循以下流程：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建合并请求

## 许可证

Copyright © 2024 SUOKE Life. All rights reserved. 