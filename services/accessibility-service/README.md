# 索克生活无障碍服务

无障碍服务是索克生活APP平台的核心微服务，为平台提供全面的无障碍功能支持，包括导盲、手语识别、屏幕阅读、语音辅助等功能，确保索克生活APP能够满足不同用户群体的需求，实现普惠健康。

## 功能特性

- **导盲辅助**：基于计算机视觉的场景识别和障碍物检测，为视障用户提供导航引导
- **手语识别**：将手语视频转换为文本，支持中文和英文手语
- **屏幕阅读**：智能解析屏幕内容并提供语音描述，帮助视障用户操作APP
- **语音辅助**：支持27种方言的语音交互，提供自然、流畅的语音界面
- **健康内容无障碍转换**：将健康内容转换为无障碍格式，如音频、简化文本、盲文等
- **无障碍设置管理**：提供统一的用户无障碍设置管理接口
- **后台数据采集服务**：在设备待机和息屏条件下持续采集用户健康数据，支持智能电池管理
- **危机报警服务**：分析用户健康数据，检测异常并触发多级报警，与智能体协作响应紧急情况

## 系统架构

服务采用模块化设计，主要组件包括：

- **API层**：基于gRPC的服务接口定义，实现跨语言通信
- **业务逻辑层**：实现各项无障碍功能的核心逻辑
- **智能体集成层**：与平台四大智能体集成，提供无缝的无障碍体验
- **AI模型层**：封装多种AI模型，包括场景识别、手语识别、语音处理等
- **平台桥接层**：提供跨平台能力，实现不同操作系统和设备的适配

服务架构图：

```
┌────────────────────────────────────────────────────────────┐
│                  无障碍服务 (accessibility-service)          │
├────────────────┬────────────────────────┬─────────────────┤
│                │                        │                 │
│    gRPC接口     │      业务逻辑层         │    配置管理      │
│                │                        │                 │
├────────────────┴────────────────────────┴─────────────────┤
│                                                            │
│                      智能体集成适配器                        │
│                                                            │
├────────────┬───────────────┬───────────────┬──────────────┤
│            │               │               │              │
│  小艾服务    │   小克服务     │   老克服务     │  索儿服务    │
│  (xiaoai)  │  (xiaoke)     │   (laoke)     │  (soer)     │
│            │               │               │              │
└────────────┴───────────────┴───────────────┴──────────────┘
```

### 核心服务模块

#### 后台数据采集服务 (BackgroundCollectionService)

后台数据采集服务实现了在设备待机和息屏条件下持续采集用户健康数据的能力，主要特性包括：

- **多类型数据采集**：支持脉搏、睡眠、活动、环境和语音等多种数据类型
- **用户隐私控制**：精细化的用户同意管理，支持特定数据类型的授权和撤销
- **智能电池管理**：根据设备电池状态自动调整采集频率，低电量时大幅降低采集频率
- **用户状态感知**：根据用户状态（活跃、闲置、睡眠）调整采集策略
- **数据加密**：采集数据进行加密存储，保护用户隐私
- **与危机报警集成**：实时向危机报警服务传递数据，支持健康异常检测

#### 危机报警服务 (CrisisAlertService)

危机报警服务负责分析健康数据，检测异常并触发报警，主要特性包括：

- **多级报警机制**：支持信息、警告、危险、严重四级报警，不同级别采取不同响应措施
- **数据异常分析**：针对不同类型数据实现专门的异常检测算法
- **智能体协作**：紧急情况下与四大智能体协调响应，实现联动处理
- **紧急联系人通知**：高级别报警自动通知预设紧急联系人
- **健康历史记录**：保存报警历史，辅助长期健康趋势分析
- **个性化阈值设置**：支持为每个用户设置自定义报警阈值

## 开发指南

### 环境要求

- Python 3.10+
- gRPC
- OpenCV (M系列芯片Mac兼容性见下文)
- PyTorch (M系列芯片Mac需使用2.7.0+版本)
- Transformers
- 其他依赖请查看`requirements.txt`

> **注意**：在Apple M系列芯片Mac上，mediapipe库存在兼容性问题。如果遇到安装困难，可以设置环境变量`TEST_ENVIRONMENT=true`启动服务，这将跳过mediapipe依赖。

### 本地开发

1. **克隆代码**
   ```bash
   git clone git@github.com:SUOKE2024/accessibility-service.git
   cd accessibility-service
   ```

2. **创建虚拟环境(可选但推荐)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行服务**
   ```bash
   # 标准启动
   ./scripts/start_service.sh
   
   # 使用测试环境变量(跳过某些依赖)
   TEST_ENVIRONMENT=true ./scripts/start_service.sh
   
   # 指定日志目录
   LOGGING_FILE=./logs/service.log ./scripts/start_service.sh
   ```

### Docker部署

1. **构建镜像**
   ```bash
   docker build -t suoke/accessibility-service:latest -f deploy/docker/Dockerfile .
   ```

2. **运行容器**
   ```bash
   # 基本运行命令
   docker run -p 50051:50051 -v /path/to/config.yaml:/app/config/config.yaml suoke/accessibility-service:latest
   
   # 设置测试环境
   docker run -p 50051:50051 -e TEST_ENVIRONMENT=true \
     -v /path/to/config.yaml:/app/config/config.yaml \
     suoke/accessibility-service:latest
   ```

3. **使用Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Kubernetes部署

1. **准备环境变量**
   ```bash
   export REGISTRY_URL=your-registry.io
   export VERSION=v1.0.0
   ```

2. **应用Kubernetes配置**
   ```bash
   envsubst < deploy/kubernetes/deployment.yaml | kubectl apply -f -
   ```

## 与智能体集成

无障碍服务与索克生活APP的四大智能体深度集成：

1. **小艾(xiaoai)**：提供语音引导、交互、问诊，以及导盲、导医、手语识别等无障碍服务
2. **小克(xiaoke)**：提供医疗资源调度时的无障碍支持，如预约引导和服务查询
3. **老克(laoke)**：提供知识内容无障碍转换和无障碍学习体验
4. **索儿(soer)**：提供生活管理场景下的无障碍支持，如健康数据理解和决策辅助

集成方式包括：

- gRPC接口调用
- 事件通知
- 功能注册与发现

详细的集成指南请参考[集成指南](docs/integration_guide.md)。

## 测试

### 单元测试

```bash
# 运行所有测试
python -m pytest test

# 运行特定模块的测试
python -m pytest test/test_background_collection.py
python -m pytest test/test_battery_bridge.py

# 使用测试环境变量
TEST_ENVIRONMENT=true python -m pytest test
```

### 集成测试

```bash
python test/integration_test.py
```

### 客户端测试

使用Docker Compose进行测试：

```bash
docker-compose up -d
docker exec -it accessibility-test-client python test_client.py
```

或直接运行测试客户端：

```bash
cd test/client
python test_client.py --host localhost --port 50051
```

## 目录结构

```
accessibility-service/
├── api/                    # API定义
│   └── grpc/               # gRPC接口定义
├── cmd/                    # 命令行入口
│   └── server/             # 服务启动
├── config/                 # 配置文件
├── deploy/                 # 部署配置
│   ├── docker/             # Docker配置
│   └── kubernetes/         # Kubernetes配置
├── docs/                   # 文档
├── internal/               # 内部实现
│   ├── delivery/           # 接口交付层
│   ├── service/            # 服务实现层
│   │   ├── background_collection.py  # 后台数据采集服务
│   │   ├── crisis_alert.py           # 危机报警服务
│   │   └── ...
│   ├── platform/           # 平台适配层
│   │   ├── battery_bridge.py  # 电池信息桥接
│   │   ├── android_bridge.py  # 安卓平台适配
│   │   ├── ios_bridge.py      # iOS平台适配
│   │   └── flutter_bridge.py  # Flutter框架适配
│   ├── model/              # 模型定义
│   └── integration/        # 智能体集成层
├── pkg/                    # 可共享的包
│   └── utils/              # 工具函数
├── scripts/                # 脚本
├── test/                   # 测试
│   ├── client/             # 测试客户端
│   └── data/               # 测试数据
├── Dockerfile              # 容器定义
├── docker-compose.yml      # 开发环境定义
├── requirements.txt        # 依赖列表
└── README.md               # 说明文档
```

## 最近更新与修复

### v0.2.1 (2025-05-16)

- **后台数据采集服务增强**
  - 实现跨平台电池电量检测功能
  - 添加智能电池管理，根据电池电量自动调整采集频率
  - 优化用户状态检测(活跃、闲置、睡眠)功能

- **危机报警服务优化**
  - 实现活动数据和语音数据分析功能
  - 增强与智能体协作系统的集成
  - 完善多级警报机制(信息、警告、危险、严重)

- **平台适配层实现**
  - 新增platform模块，统一管理不同平台的接口适配
  - 实现电池桥接模块，统一电池信息获取接口
  - 增加iOS/Android/Flutter平台特定实现

- **问题修复**
  - 修复了gRPC导入路径问题
  - 改进了日志目录权限处理
  - 优化了测试环境下的缓存机制
  - 修复了MacOS M系列芯片兼容性问题

## 贡献指南

欢迎贡献代码或提交问题！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

提交代码前请确保通过所有测试，并遵循项目代码风格。

## 许可证

本项目采用MIT许可证，详情请查看[LICENSE](../LICENSE)文件。

## 联系我们

如有任何疑问或需要进一步支持，请联系无障碍服务团队：accessibility-team@suoke.life 