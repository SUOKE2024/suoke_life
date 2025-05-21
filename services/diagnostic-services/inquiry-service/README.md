# 问诊服务 (Inquiry Service)

问诊服务是索克生活APP四诊合参体系中的"问诊"部分，负责通过自然语言问答收集用户健康信息，提取症状并映射到中医理论体系中。

## 功能特点

- **智能问诊对话**：支持连续对话式问诊，通过大语言模型提供自然、专业的问诊体验
- **症状智能提取**：从用户自然语言描述中精准提取健康症状信息
- **中医证型映射**：将现代症状表述映射到传统中医证型理论体系
- **健康风险评估**：基于用户症状和健康档案进行健康风险评估
- **多模态集成**：支持文本、图像等多种数据输入方式
- **个性化推荐**：根据用户体质和症状提供个性化健康建议
- **历史分析**：支持历史病史分析和健康趋势追踪

## 服务架构

问诊服务采用Clean Architecture架构，主要分为以下几个层次：

1. **表现层** (Delivery)：gRPC服务接口实现
2. **对话管理** (Dialogue)：管理问诊会话流程
3. **大语言模型** (LLM)：负责生成问诊响应
4. **症状提取** (Symptom Extraction)：从文本中提取症状信息
5. **中医证型映射** (TCM Pattern Mapping)：将症状映射到中医证型
6. **中医知识库** (TCM Knowledge)：提供中医相关知识支持
7. **存储层** (Repository)：管理会话和用户数据的持久化

## 技术栈

- **开发语言**：Python 3.9+ (支持到Python 3.13)
- **通信协议**：gRPC
- **数据存储**：MongoDB / 内存存储
- **缓存**：Redis / 内存缓存
- **大语言模型**：支持多种LLM模型（Llama3, Qwen, ChatGLM等）
- **监控**：Prometheus + Grafana
- **容器化**：Docker / Kubernetes

## 目录结构

```
inquiry-service/
├── api/                       # API定义
│   ├── grpc/                  # gRPC协议定义
│   └── docs/                  # API文档
├── cmd/                       # 命令行入口
│   └── server.py              # 服务器入口
├── config/                    # 配置文件
│   ├── config.yaml            # 主配置文件
│   ├── prompts/               # 提示词模板
│   └── schemas/               # JSON模式定义
├── data/                      # 数据目录
│   ├── mock_responses/        # Mock响应数据
│   └── tcm_knowledge/         # 中医知识库数据
├── deploy/                    # 部署配置
│   ├── docker/                # Docker配置
│   ├── grafana/               # Grafana配置
│   ├── kubernetes/            # Kubernetes部署配置
│   └── prometheus/            # Prometheus配置
├── integration/               # 外部服务集成
│   └── xiaoai_service/        # 小艾服务集成
├── internal/                  # 内部实现
│   ├── delivery/              # 服务接口实现
│   ├── dialogue/              # 对话管理
│   ├── llm/                   # LLM客户端
│   ├── knowledge/             # 知识库
│   ├── model/                 # 数据模型
│   ├── repository/            # 数据存储
│   └── tcm/                   # 中医相关逻辑
├── logs/                      # 日志目录
├── pkg/                       # 公共包
│   └── utils/                 # 工具函数
└── test/                      # 测试代码
    ├── data/                  # 测试数据
    ├── integration/           # 集成测试
    └── internal/              # 单元测试
```

## 快速开始

### 前置条件

- Python 3.9+ (推荐Python 3.11/3.12，已支持Python 3.13)
- Docker和Docker Compose (可选)

### 环境变量配置

创建`.env`文件，参考`.env-example`：

```sh
cp .env-example .env
```

开发环境推荐配置：

```
SERVICE_ENV=development
LOG_LEVEL=DEBUG
USE_MOCK_MODE=true
MOCK_EXTERNAL_SERVICES=true
```

### 本地开发环境

1. 克隆仓库

```sh
git clone git@github.com:suoke-life/inquiry-service.git
cd inquiry-service
```

2. 安装依赖

```sh
pip install -r requirements.txt
```

3. 创建必要的目录

```sh
mkdir -p logs data/mock_responses data/tcm_knowledge
```

4. 生成gRPC代码 (如果需要更新协议)

```sh
python -m grpc_tools.protoc -I./api/grpc --python_out=. --grpc_python_out=. ./api/grpc/inquiry_service.proto
```

5. 启动服务

```sh
# 从正确的目录启动，确保路径正确
cd /path/to/inquiry-service
python cmd/server.py
```

### 使用Docker Compose运行完整环境

```sh
docker-compose up -d
```

### 部署到Kubernetes

```sh
kubectl apply -f deploy/kubernetes/inquiry-service.yaml
```

## API接口

问诊服务提供以下gRPC接口：

- `StartInquirySession`：开始问诊会话
- `InteractWithUser`：问诊互动（流式响应）
- `EndInquirySession`：结束问诊会话并获取总结
- `AnalyzeMedicalHistory`：分析用户病史
- `ExtractSymptoms`：提取症状信息
- `MapToTCMPatterns`：中医症状匹配
- `BatchAnalyzeInquiryData`：批量分析健康数据
- `AssessHealthRisks`：健康风险评估

详细接口定义请参考 `api/grpc/inquiry_service.proto` 文件。

## 配置说明

服务配置在 `config/config.yaml` 文件中，主要包括：

- **server**：服务器配置（端口、工作线程等）
- **dialogue**：对话管理配置（会话超时、默认语言等）
- **llm**：大语言模型配置（模型类型、推理参数等）
- **symptom_extraction**：症状提取配置
- **tcm_pattern_mapping**：中医证型映射配置
- **tcm_knowledge**：中医知识库配置
- **health_risk_assessment**：健康风险评估配置
- **database**：数据库配置
- **cache**：缓存配置
- **metrics**：监控指标配置
- **logging**：日志配置
- **integration**：外部服务集成配置
- **mock**：模拟模式配置

## 中医知识库

问诊服务内置了中医知识库，包含以下主要内容：

- **证型数据**：常见中医证型及其描述、分类和相关症状
- **症状数据**：常见症状及其描述、相关部位和证型关联
- **症状-证型映射**：连接症状和可能的证型
- **证型分类**：按虚实、寒热等不同维度的分类
- **身体部位**：身体各部位及其关联的脏腑和常见症状

知识库数据存储在 `data/tcm_knowledge` 目录下，使用YAML格式文件进行管理。首次启动时如果数据不存在，系统会自动创建示例数据。

## LLM模型与提示词

服务使用LLM进行智能问诊和分析，提供了以下提示词模板：

- **系统提示词**：定义LLM的基本角色和行为规范
- **对话提示词**：引导LLM进行问诊互动
- **欢迎提示词**：生成会话开始时的欢迎语和建议问题
- **症状提取提示词**：指导LLM从文本中提取症状信息
- **证型映射提示词**：指导LLM进行中医证型的辨别
- **健康风险评估提示词**：指导LLM评估健康风险并提供预防策略
- **总结提示词**：指导LLM生成会话结束时的总结报告

提示词模板存储在 `config/prompts` 目录下，可以根据需要进行自定义调整。

## Mock模式

服务支持Mock模式，便于开发和测试：

### 启用方式

1. 通过配置文件 `config/config.yaml`：

```yaml
llm:
  use_mock_mode: true  # 启用LLM模拟
  
mock:
  enabled: true        # 启用全局模拟
  response_delay_ms: 200
  random_failures: false
```

2. 通过环境变量：

```
USE_MOCK_MODE=true
MOCK_EXTERNAL_SERVICES=true
```

### Mock数据

模拟响应数据存放在 `data/mock_responses` 目录下，可自定义模拟响应。

## 测试

服务提供了全面的测试覆盖：

- **单元测试**：测试各个组件的独立功能
- **集成测试**：测试组件之间的协作和完整流程
- **gRPC测试**：测试服务API接口的功能和性能

运行测试：

```sh
# 运行所有测试
pytest

# 运行特定测试
pytest test/internal/test_symptom_extractor.py

# 运行集成测试
pytest test/integration/
```

## 与其他服务的集成

问诊服务与索克生活APP的其他微服务协作：

- **小艾服务** (xiaoai-service)：四诊协调，整合问诊结果
- **闻诊服务** (listen-service)：语音和声音分析
- **望诊服务** (look-service)：图像分析
- **中医知识库** (med-knowledge)：提供专业知识支持

## 监控与可观测性

问诊服务集成了Prometheus和Grafana用于监控和可视化服务运行状态：

- **Prometheus**：收集服务指标，访问地址：http://localhost:9090
- **Grafana**：可视化监控面板，访问地址：http://localhost:3000 (默认用户名/密码：admin/admin)

主要监控指标包括：

- 请求延迟和吞吐量
- 活跃会话数
- LLM响应时间
- 症状提取准确率
- 系统资源使用情况

## 问题排查指南

### Python 3.13 兼容性问题

在Python 3.13中可能遇到的事件循环相关错误：

```
Task got Future attached to a different loop
```

**解决方案**：
- 使用 `asyncio.run()` 代替 `loop.run_until_complete()`
- 避免在不同线程间传递事件循环

### 常见问题与解决方案

1. **服务启动路径问题**

   症状：找不到模块或文件
   解决方案：确保在项目根目录下运行，使用绝对路径：
   ```sh
   cd /path/to/inquiry-service
   python cmd/server.py
   ```

2. **依赖缺失问题**

   症状：ModuleNotFoundError
   解决方案：安装缺失的依赖：
   ```sh
   pip install -r requirements.txt
   pip install python-dotenv grpcio grpcio-tools grpcio-reflection PyYAML httpx aiohttp
   ```

3. **gRPC反射错误**

   症状：启用服务器反射时出错
   解决方案：在服务启动时添加错误处理，如现有代码所示

4. **外部服务连接问题**

   症状：无法连接到其他微服务
   解决方案：
   - 确认服务地址配置正确
   - 启用Mock模式进行开发 (`USE_MOCK_MODE=true`)
   - 检查网络连接和防火墙设置

## 高级使用指南

### 自定义LLM接入

问诊服务支持接入多种大语言模型：

1. **本地模型**：配置 `local_inference` 和 `local_model_path`
2. **远程API**：配置 `remote_endpoint` 和相关API密钥

示例配置：
```yaml
llm:
  model_type: "llama3"  # 或 "glm", "gpt4", "qwen2"等
  local_inference: true
  local_model_path: "./data/models/tcm_medical_qa"
  # 或
  local_inference: false
  remote_endpoint: "http://ai-inference-service:8080/v1"
```

### 自定义中医知识库

您可以通过修改 `data/tcm_knowledge` 目录下的YAML文件来扩展和自定义中医知识库：

- **patterns.yaml**：证型数据
- **symptoms.yaml**：症状数据
- **symptom_pattern_mapping.yaml**：症状-证型映射
- **pattern_categories.yaml**：证型分类
- **body_locations.yaml**：身体部位信息

### 流式响应处理

处理长文本交互时推荐使用流式响应API：

```python
# 客户端示例
for response in stub.InteractWithUser(request):
    print(response.message_chunk, end="", flush=True)
```

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 [MIT 许可证](LICENSE)。 