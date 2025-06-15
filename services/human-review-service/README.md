# 索克生活人工审核服务

人工审核服务是索克生活平台的核心质量控制组件，提供AI辅助的人工审核功能，确保平台内容和诊断结果的准确性和安全性。

## 🌟 核心功能

### 智能审核系统
- **AI辅助预审** - 使用机器学习模型进行初步内容筛选
- **多维度质量评估** - 从准确性、安全性、合规性等角度评估内容
- **智能优先级排序** - 根据风险等级自动分配审核优先级
- **实时异常检测** - 识别可疑内容和异常行为模式

### 专业审核流程
- **分层审核机制** - 初审、复审、终审的多层质量保障
- **专家协作平台** - 支持多专家协同审核和意见汇总
- **审核标准管理** - 可配置的审核规则和评分标准
- **审核历史追踪** - 完整的审核过程记录和可追溯性

### 内容类型支持
- **医学诊断结果** - 中医辨证、西医诊断的专业审核
- **健康建议内容** - 养生方案、用药建议的安全性审核
- **用户生成内容** - 社区分享、经验交流的合规性审核
- **多媒体内容** - 图像、视频、音频的智能识别和审核

## 🏗️ 技术架构

```
人工审核服务
├── AI预审引擎
│   ├── 文本分析模块
│   ├── 图像识别模块
│   ├── 风险评估模块
│   └── 优先级排序模块
├── 审核工作流
│   ├── 任务分发系统
│   ├── 审核员管理
│   ├── 质量控制
│   └── 进度跟踪
├── 专家协作平台
│   ├── 多人协作
│   ├── 意见汇总
│   ├── 争议解决
│   └── 知识共享
└── 数据管理
    ├── 审核记录
    ├── 统计分析
    ├── 性能监控
    └── 合规报告
```

## 🚀 技术栈

- **语言**: Python 3.13.3
- **框架**: FastAPI + Celery
- **数据库**: PostgreSQL + Redis
- **AI引擎**: PyTorch + Transformers + Sentence-Transformers
- **消息队列**: RabbitMQ + Redis
- **文件存储**: MinIO + AWS S3
- **监控**: Prometheus + Grafana + OpenTelemetry
- **部署**: Docker + Kubernetes

## 📁 项目结构

```
human-review-service/
├── api/                      # API定义
│   ├── grpc/                 # gRPC服务定义
│   │   ├── review.proto      # 审核服务协议
│   │   └── workflow.proto    # 工作流协议
│   └── rest/                 # REST API定义
│       ├── review_api.py     # 审核API
│       └── admin_api.py      # 管理API
├── cmd/                      # 服务入口点
│   └── server/
│       └── main.py           # 主服务器
├── internal/                 # 内部业务逻辑
│   ├── ai/                   # AI审核引擎
│   │   ├── text_analyzer.py  # 文本分析
│   │   ├── image_analyzer.py # 图像分析
│   │   ├── risk_assessor.py  # 风险评估
│   │   └── priority_ranker.py # 优先级排序
│   ├── workflow/             # 审核工作流
│   │   ├── task_manager.py   # 任务管理
│   │   ├── reviewer_manager.py # 审核员管理
│   │   ├── quality_control.py # 质量控制
│   │   └── progress_tracker.py # 进度跟踪
│   ├── collaboration/        # 专家协作
│   │   ├── expert_system.py  # 专家系统
│   │   ├── opinion_aggregator.py # 意见汇总
│   │   └── dispute_resolver.py # 争议解决
│   ├── models/               # 数据模型
│   │   ├── review_models.py  # 审核模型
│   │   ├── task_models.py    # 任务模型
│   │   └── user_models.py    # 用户模型
│   ├── repository/           # 数据访问层
│   │   ├── review_repository.py
│   │   ├── task_repository.py
│   │   └── user_repository.py
│   ├── service/              # 业务服务层
│   │   ├── review_service.py # 审核服务
│   │   ├── ai_service.py     # AI服务
│   │   └── workflow_service.py # 工作流服务
│   └── config/               # 配置管理
│       ├── settings.py       # 设置
│       └── ai_config.py      # AI配置
├── pkg/                      # 可导出包
│   ├── middleware/           # 中间件
│   ├── utils/                # 工具函数
│   └── cli/                  # 命令行工具
├── test/                     # 测试
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── e2e/                  # 端到端测试
├── deploy/                   # 部署配置
│   ├── docker/               # Docker配置
│   └── kubernetes/           # K8s配置
├── migrations/               # 数据库迁移
├── docs/                     # 文档
└── scripts/                  # 脚本工具
```

## 🔧 快速开始

### 环境要求
- Python 3.13.3+
- PostgreSQL 13+
- Redis 6+
- RabbitMQ 3.8+
- Docker & Docker Compose

### 安装依赖
```bash
# 使用UV包管理器（推荐）
uv sync

# 或使用pip
pip install -e .
```

### 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env
```

### 启动服务
```bash
# 开发环境
docker-compose up -d
python -m cmd.server.main

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

### 启动Celery工作进程
```bash
# 启动审核工作进程
celery -A internal.tasks.celery_app worker --loglevel=info --queues=review

# 启动AI分析工作进程
celery -A internal.tasks.celery_app worker --loglevel=info --queues=ai_analysis

# 启动Flower监控
celery -A internal.tasks.celery_app flower
```

## 📊 API文档

### REST API
服务启动后访问以下端点获取API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### gRPC API
查看 `api/grpc/` 目录下的 `.proto` 文件获取gRPC接口定义。

### 主要API端点

#### 审核管理
```http
POST /api/v1/reviews/submit          # 提交审核任务
GET  /api/v1/reviews/{review_id}     # 获取审核详情
PUT  /api/v1/reviews/{review_id}     # 更新审核状态
GET  /api/v1/reviews/queue           # 获取审核队列
```

#### AI预审
```http
POST /api/v1/ai/pre-review           # AI预审核
GET  /api/v1/ai/risk-assessment      # 风险评估
POST /api/v1/ai/content-analysis     # 内容分析
```

#### 工作流管理
```http
GET  /api/v1/workflow/tasks          # 获取任务列表
POST /api/v1/workflow/assign         # 分配任务
PUT  /api/v1/workflow/complete       # 完成任务
GET  /api/v1/workflow/statistics     # 工作流统计
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行单元测试
pytest test/unit/

# 运行集成测试
pytest test/integration/

# 运行性能测试
pytest test/performance/ --benchmark-only

# 生成覆盖率报告
pytest --cov=internal --cov-report=html
```

### 测试覆盖率目标
- 单元测试覆盖率: ≥90%
- 集成测试覆盖率: ≥80%
- 端到端测试覆盖率: ≥70%

## 📈 监控和指标

### Prometheus指标
- `review_tasks_total` - 审核任务总数
- `review_processing_duration` - 审核处理时长
- `ai_analysis_accuracy` - AI分析准确率
- `reviewer_workload` - 审核员工作负载
- `quality_score_distribution` - 质量分数分布

### 健康检查
```bash
# 服务健康状态
curl http://localhost:8000/health

# 详细健康检查
curl http://localhost:8000/health/detailed

# AI引擎状态
curl http://localhost:8000/health/ai
```

## 🔐 安全特性

- **数据加密** - 传输和存储数据的端到端加密
- **访问控制** - 基于角色的细粒度权限管理
- **审计日志** - 完整的操作记录和审计追踪
- **隐私保护** - 敏感信息的脱敏和匿名化处理
- **合规检查** - 符合医疗数据保护法规要求

## 🚀 部署

### Docker部署
```bash
# 构建镜像
docker build -t human-review-service:latest .

# 运行容器
docker run -d \
  --name human-review-service \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  human-review-service:latest
```

### Kubernetes部署
```bash
# 应用配置
kubectl apply -f deploy/kubernetes/

# 检查部署状态
kubectl get pods -l app=human-review-service

# 查看日志
kubectl logs -f deployment/human-review-service
```

## 📚 文档

- [API文档](./docs/api/) - 完整的API接口文档
- [部署指南](./docs/deployment/) - 生产环境部署指南
- [开发指南](./docs/development/) - 开发者指南
- [AI模型文档](./docs/ai/) - AI引擎使用说明
- [工作流配置](./docs/workflow/) - 审核工作流配置指南

## 🤝 贡献

我们欢迎社区贡献！请查看 [贡献指南](./CONTRIBUTING.md) 了解详情。

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 📞 联系我们

- **技术支持**: tech@suoke.life
- **产品咨询**: product@suoke.life
- **商务合作**: business@suoke.life

---

**索克生活人工审核服务 - 确保平台内容质量和用户安全** 🛡️ 