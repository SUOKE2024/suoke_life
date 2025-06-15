# Corn Maze Service

Corn Maze Service是Soke Life APP的一个微服务，提供迷宫生成、探索和知识获取功能。它结合了中医养生知识和游戏化体验，帮助用户在有趣的探索过程中学习健康知识。

## 功能特点

- **多种迷宫类型**：提供健康路径、营养花园、中医之旅和平衡生活等多种主题的迷宫
- **知识节点**：迷宫中分布着各种健康、营养、中医等主题的知识点
- **挑战任务**：完成迷宫中的各类挑战，获取奖励和成长
- **个性化体验**：根据用户健康属性生成符合其需求的迷宫内容
- **进度跟踪**：记录用户的探索进度，支持保存和继续

## 技术架构

- **后端**：Python 3.9+
- **API**：gRPC接口
- **存储**：SQLite数据库
- **监控**：Prometheus + Grafana
- **容器化**：Docker + Kubernetes部署

## 快速开始

### 依赖安装

```bash
pip install -r requirements.txt
```

### 本地运行

```bash
# 启动服务
python cmd/server/main.py

# 运行单元测试
python -m pytest test/unit

# 运行集成测试
python -m pytest test/integration
```

### Docker构建与运行

```bash
# 构建镜像
docker build -t corn-maze-service:latest -f deploy/docker/Dockerfile .

# 运行容器
docker run -p 50057:50057 -p 51057:51057 -p 51058:51058 corn-maze-service:latest
```

## API接口

服务通过gRPC提供以下核心API：

- `CreateMaze`：创建一个新的迷宫
- `GetMaze`：获取特定迷宫的详情
- `GetUserMazes`：获取用户的迷宫列表
- `UpdateMaze`：更新迷宫信息
- `DeleteMaze`：删除迷宫
- `SearchMazes`：搜索公开迷宫
- `UpdateProgress`：更新用户在迷宫中的进度
- `GetProgress`：获取用户的迷宫进度
- `CompleteMaze`：完成迷宫并获取奖励

## 项目结构

```
corn-maze-service/
├── api/              # API定义
│   └── grpc/         # gRPC接口定义
├── cmd/              # 应用入口
│   └── server/       # 服务启动入口
├── config/           # 配置文件
├── data/             # 数据目录
├── deploy/           # 部署配置
│   ├── docker/       # Docker配置
│   ├── grafana/      # Grafana仪表盘
│   ├── kubernetes/   # Kubernetes部署配置
│   └── prometheus/   # Prometheus监控配置
├── docs/             # 文档
├── internal/         # 内部代码
│   ├── delivery/     # API实现
│   ├── maze/         # 迷宫生成逻辑
│   ├── model/        # 数据模型
│   ├── repository/   # 数据存储
│   └── service/      # 业务逻辑
├── pkg/              # 可复用包
│   └── utils/        # 工具类
├── test/             # 测试代码
│   ├── client/       # 测试客户端
│   ├── integration/  # 集成测试
│   └── unit/         # 单元测试
├── .github/          # GitHub工作流配置
├── Dockerfile        # Docker构建文件
├── requirements.txt  # Python依赖
└── README.md         # 项目说明
```

## 监控与可观测性

服务集成了完善的监控和可观测性功能：

- **指标收集**：通过Prometheus收集API调用、性能、错误等指标
- **可视化监控**：Grafana仪表盘展示服务状态和性能
- **健康检查**：提供健康检查端点，支持Kubernetes探针
- **日志记录**：结构化日志记录系统事件和错误

## 性能优化

- 使用SQLite连接池优化数据库访问
- 异步处理提高并发能力
- 缓存机制减少重复计算
- 分页查询优化大数据集访问

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

Corn Maze Service为Soke Life APP的专有组件，仅供内部使用。