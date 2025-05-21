# 望诊服务 (Look Service)

望诊服务是索克生活APP的核心微服务之一，负责提供基于中医望诊理论的面色分析和形体分析功能。通过多模态视觉分析技术，将用户的面部特征和体态特征与中医理论相结合，提供个性化的健康分析和建议。

## 功能特性

- **面色分析**：分析用户面部图像的色泽、光泽和水分状态，将其与中医五色（青、赤、黄、白、黑）理论相关联，推断脏腑功能状态。
- **形体分析**：分析用户体态，包括体型特征、姿态和比例，评估气血运行、脏腑功能以及整体健康状态。
- **中医理论关联**：将视觉特征与中医理论关联，生成体质分析和健康建议。
- **数据持久化**：保存分析记录，支持历史查询和趋势分析。
- **小艾服务集成**：与小艾服务(xiaoai-service)集成，提供更全面的中医四诊分析结果。

## 技术架构

- **编程语言**：Python 3.11
- **通信协议**：gRPC
- **图像处理**：OpenCV, NumPy
- **人工智能**：计算机视觉与传统中医知识图谱结合
- **存储**：SQLite（轻量级文件数据库）
- **监控**：Prometheus, OpenTelemetry
- **部署**：Docker, Kubernetes

## 项目结构

```
look-service/
├── api/                    # API定义
│   └── grpc/               # gRPC协议定义
│       ├── look_service.proto  # 服务协议定义
│       └── ...
├── cmd/                    # 命令行工具和服务入口
│   └── server.py           # 服务入口
├── config/                 # 配置相关
│   ├── config.py           # 配置加载
│   └── config.yaml         # 配置文件
├── deploy/                 # 部署相关
│   ├── docker/             # Docker部署
│   └── kubernetes/         # Kubernetes部署
├── internal/               # 内部实现
│   ├── analysis/           # 分析算法
│   │   ├── face_analyzer.py   # 面色分析器
│   │   └── body_analyzer.py   # 形体分析器
│   ├── delivery/           # 服务实现
│   │   └── look_service_impl.py  # 服务实现
│   ├── integration/        # 外部集成
│   │   └── xiaoai_client.py     # 小艾服务客户端
│   ├── model/              # 模型相关
│   │   └── model_factory.py    # 模型工厂
│   └── repository/         # 数据存储
│       └── analysis_repository.py  # 分析结果存储
├── pkg/                    # 通用工具包
│   └── utils/              # 工具类
│       ├── exceptions.py   # 异常定义
│       └── image_utils.py  # 图像处理工具
├── test/                   # 测试
│   ├── integration/        # 集成测试
│   ├── performance/        # 性能测试
│   └── unit/               # 单元测试
├── Dockerfile              # Docker构建文件
├── README.md               # 项目说明
└── requirements.txt        # 依赖项
```

## 快速开始

### 环境要求

- Python 3.11+
- OpenCV
- gRPC

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地运行

```bash
# 设置环境变量
export CONFIG_PATH=./config/config.yaml

# 启动服务
python cmd/server.py
```

### Docker部署

```bash
# 构建镜像
docker build -t suoke/look-service:latest .

# 运行容器
docker run -p 50053:50053 suoke/look-service:latest
```

### Kubernetes部署

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

## API说明

服务通过gRPC协议提供以下主要API：

- `AnalyzeFace` - 分析面色
- `AnalyzeBody` - 分析形体
- `GetFaceAnalysis` - 获取面色分析结果
- `GetBodyAnalysis` - 获取形体分析结果
- `GetUserAnalysisHistory` - 获取用户分析历史
- `DeleteAnalysis` - 删除分析记录
- `HealthCheck` - 健康检查

详细API文档见 [API文档](../../../docs/api/look_service_api.md)

## 测试

### 单元测试

```bash
# 运行所有单元测试
pytest test/unit

# 运行特定测试
pytest test/unit/test_face_analyzer.py
```

### 集成测试

```bash
# 运行集成测试
pytest test/integration
```

### 性能测试

```bash
# 运行性能测试
python test/performance/test_service_performance.py
```

## 开发指南

### 代码规范

- 使用Black进行代码格式化
- 使用Pylint进行代码静态分析
- 遵循PEP 8编码规范

### 提交前检查

```bash
# 运行格式化
black .

# 运行静态分析
pylint **/*.py

# 运行单元测试
pytest
```

## 监控与可观测性

- **Prometheus指标**：服务暴露在`/metrics`端点
- **日志**：结构化日志输出到`logs/look_service.log`
- **分布式追踪**：支持OpenTelemetry与Jaeger集成

## 故障排除

常见问题和解决方案：

1. **服务启动失败**：检查配置文件路径和内容是否正确
2. **分析失败**：检查图像格式和大小是否支持
3. **集成失败**：检查xiaoai-service是否可达
4. **性能问题**：检查资源配置和并发设置

## 贡献指南

1. Fork该仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

## 版本历史

- v1.0.0 - 初始版本
- v1.1.0 - 添加形体分析功能
- v1.2.0 - 改进面色分析算法
- v1.3.0 - 与xiaoai-service集成

## 许可证

版权所有 © 2024 索克生活科技 