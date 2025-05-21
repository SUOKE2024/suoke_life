# 切诊微服务 (Palpation Service)

切诊微服务是索克生活APP四诊合参系统的重要组成部分，负责处理与"切诊"（触诊）相关的数据采集、分析和结果生成。本服务实现了中医传统脉诊、腹诊和皮肤触诊等切诊方法的数字化和智能化。

## 功能特点

### 脉诊功能
- **脉搏波采集与处理**：采集和处理脉搏波形信号，支持多点位测量（寸、关、尺六部位）
- **脉搏波特征提取**：提取时域、频域和小波域的多维特征
- **脉象类型识别**：识别28种传统脉象类型（如浮脉、沉脉、迟脉、数脉等）
- **脏腑状态评估**：根据脉象特征评估相关脏腑状态

### 腹诊功能
- **腹部区域评估**：支持9个腹部区域的压痛、紧张度、质地和肿块分析
- **腹诊结果关联**：将腹诊结果与相关脏腑功能关联

### 皮肤触诊功能
- **皮肤状态评估**：分析皮肤的水分、弹性、质地、温度和颜色
- **皮肤触诊分析**：从皮肤状态推断相关生理病理情况

### 综合分析
- **多维度切诊整合**：整合脉诊、腹诊和皮肤触诊结果
- **中医证型映射**：将切诊结果映射到中医证型
- **健康评估报告**：生成切诊分析报告

### 新增功能
- **多设备适配支持**：支持多种脉诊设备，包括索克WP-100、TCM Diagnostics PulseWave Pro和MedSense PulseReader 2000
- **服务健康监控**：提供健康检查API，支持三级健康检查，便于服务监控
- **设备校准管理**：完善的设备校准流程，确保数据准确性

## 技术架构

- **后端框架**：Python + FastAPI + gRPC
- **信号处理**：NumPy, SciPy, PyWavelets
- **数据存储**：MongoDB
- **部署**：Docker, Kubernetes
- **监控**：Prometheus, Grafana

## 系统结构

```
palpation-service/
├── api/                    # API定义
│   └── grpc/              # gRPC接口
├── cmd/                    # 入口点
│   └── server.py          # 服务启动
├── config/                 # 配置文件
├── internal/               # 内部代码
│   ├── delivery/          # 接口层
│   ├── model/             # 数据模型
│   ├── repository/        # 数据访问
│   └── signal/            # 信号处理
│       └── device_adapter.py # 设备适配器
├── pkg/                    # 公共包
│   └── utils/             # 工具函数
├── deploy/                 # 部署配置
│   └── k8s/               # K8s资源文件
└── test/                   # 测试代码
```

## 运行服务

### 前置条件
- Python 3.8+
- MongoDB
- Redis (可选，用于缓存)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置
配置文件位于`config/config.yaml`，可通过环境变量覆盖配置。详细配置请查看`.env-example`文件。

### 本地运行
```bash
# 启动服务
python -m cmd.server
```

### Docker运行
```bash
# 构建Docker镜像
docker build -t palpation-service:latest .

# 运行容器
docker-compose up -d
```

## 开发状态

**当前开发完成度: 100%**

切诊服务已完成所有核心功能开发，包括:
- 所有gRPC API方法实现
- 完整的单元测试和集成测试
- 与其他服务的集成
- 部署配置和监控设置
- 健康检查API
- 多设备适配器

详细开发状态请查看 [开发状态文档](./docs/development_status.md)。

## 目录结构说明

```
palpation-service/
├── api/                    # API定义
│   └── grpc/              # gRPC接口
│       └── palpation_service.proto # 服务定义
├── cmd/                    # 入口点
│   └── server.py          # 服务启动
├── config/                 # 配置文件
│   └── config.yaml        # 主配置文件
├── docs/                   # 文档
│   └── development_status.md # 开发状态文档
├── internal/               # 内部代码
│   ├── delivery/          # 接口层
│   │   ├── palpation_service_impl.py # 服务实现
│   │   ├── comprehensive_analysis.py # 综合分析处理器
│   │   └── batch_analyzer.py # 批量分析处理器
│   ├── model/             # 数据模型
│   ├── repository/        # 数据访问
│   │   ├── session_repository.py # 会话数据仓库
│   │   └── user_repository.py # 用户数据仓库
│   └── signal/            # 信号处理
│       ├── pulse_processor.py # 脉搏处理器
│       ├── abdominal_analyzer.py # 腹诊分析器
│       ├── skin_analyzer.py # 皮肤分析器
│       └── device_adapter.py # 设备适配器
├── pkg/                    # 公共包
│   └── utils/             # 工具函数
├── deploy/                 # 部署配置
│   ├── docker/            # Docker配置
│   ├── grafana/           # Grafana监控配置
│   ├── kubernetes/        # K8s资源文件
│   └── prometheus/        # Prometheus监控配置
└── test/                   # 测试代码
    ├── test_pulse_processor.py # 脉搏处理器测试
    ├── test_abdominal_analyzer.py # 腹诊分析器测试
    ├── test_skin_analyzer.py # 皮肤分析器测试
    └── integration/       # 集成测试
        └── test_palpation_service.py # 服务集成测试
```

## API文档

### gRPC接口
主要接口包括：
- `StartPulseSession` - 开始脉诊会话
- `RecordPulseData` - 记录脉搏数据
- `ExtractPulseFeatures` - 提取脉象特征
- `AnalyzePulse` - 分析脉象
- `AnalyzeAbdominalPalpation` - 腹诊分析
- `AnalyzeSkinPalpation` - 皮肤触诊分析
- `GetComprehensivePalpationAnalysis` - 获取综合切诊分析
- `BatchAnalyzePulseData` - 批量分析历史脉诊数据
- `ComparePulseSessions` - 比较多次脉诊数据
- `GeneratePalpationReport` - 生成切诊报告
- `HealthCheck` - 服务健康检查（支持三级检查：最小、基础、完整）

详细API文档请参考`api/grpc/palpation_service.proto`文件。

## 健康检查

服务提供健康检查API，用于监控服务状态。健康检查支持三个级别：

1. **最小 (MINIMAL)**：仅检查服务是否运行
2. **基础 (BASIC)**：检查服务和数据库连接状态
3. **完整 (FULL)**：全面检查所有依赖和集成点

使用示例：

```python
import grpc
from api.grpc import palpation_service_pb2 as pb2
from api.grpc import palpation_service_pb2_grpc as pb2_grpc

# 创建gRPC通道
channel = grpc.insecure_channel('localhost:50053')
stub = pb2_grpc.PalpationServiceStub(channel)

# 执行健康检查
request = pb2.HealthCheckRequest(level=pb2.HealthCheckRequest.HealthCheckLevel.BASIC)
response = stub.HealthCheck(request)

print(f"服务状态: {response.status}")
for component in response.components:
    print(f"组件: {component.component_name}, 状态: {component.status}, 详情: {component.details}")
```

## 设备支持

切诊服务支持多种脉诊设备，通过设备适配器统一数据格式。当前支持的设备有：

1. **索克WP-100**：索克自研脉诊仪，支持六部位脉象采集
2. **TCM Diagnostics PulseWave Pro**：第三方专业脉诊仪器
3. **MedSense PulseReader 2000**：便携式脉诊设备

各设备支持的功能比较：

| 设备 | 支持位置 | 皮肤温度 | 皮肤湿度 | 最高采样率 | 无线 |
|------|---------|---------|---------|-----------|------|
| 索克WP-100 | 六部位 | ✅ | ✅ | 1000Hz | ✅ |
| PulseWave Pro | 六部位 | ✅ | ✅ | 500Hz | ❌ |
| PulseReader 2000 | 六部位 | ✅ | ❌ | 200Hz | ✅ |

## 与其他服务集成

切诊服务与索克生活APP的以下服务进行集成：

- **小艾服务 (xiaoai-service)**：提供切诊数据作为四诊合参的组成部分
- **望诊服务 (look-service)**：结合舌诊和面诊结果
- **闻诊服务 (listen-service)**：结合声音和气味分析
- **问诊服务 (inquiry-service)**：结合问诊信息
- **检索服务 (rag-service)**：获取相关健康知识

## 贡献指南

欢迎贡献代码、报告问题或提出功能建议。请遵循项目的编码规范和工作流程。

## 许可证

本项目采用MIT许可证。

## 联系方式

如有任何问题，请联系索克生活APP开发团队。 