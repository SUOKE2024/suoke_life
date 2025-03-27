# 索克生活 RAG 服务

索克生活RAG服务是一个专注于中医知识检索和生成的服务，使用检索增强生成（RAG）技术提供高质量的中医知识检索服务。

## 功能特点

- 基于知识图谱的中医知识检索
- 多种检索策略支持（语义搜索、关键词搜索、混合搜索）
- 高质量结果重排序
- 完善的监控和日志系统
- 支持Kubernetes部署
- 专业领域知识检索（精准医学、多模态健康等）
- 跨领域知识整合
- 证据级别评估
- 环境健康数据检索
- 心理健康知识定制检索

## 目录结构

```
├── config/                  # 配置文件
├── data/                    # 数据文件
├── k8s/                     # Kubernetes配置文件
├── logs/                    # 日志文件
├── models/                  # 模型文件
├── scripts/                 # 脚本文件
│   └── deploy/              # 部署脚本
│       └── kubernetes/      # Kubernetes配置文件
├── src/                     # 源代码
│   ├── api/                 # API接口
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # 路由定义
│   │   │   ├── retrieval.py           # 基础检索路由
│   │   │   └── specialized_retrievers.py  # 专业领域检索路由
│   ├── config/              # 配置模块
│   ├── knowledge_graph/     # 知识图谱模块
│   │   └── schema.py        # 知识图谱模式定义
│   ├── monitoring/          # 监控模块
│   ├── retrievers/          # 检索器模块
│   │   └── knowledge_retrievers.py  # 知识检索器
│   └── utils/               # 工具模块
├── tests/                   # 测试代码
├── .github/                 # GitHub相关配置
│   └── workflows/           # GitHub Actions工作流
├── Dockerfile               # Docker构建文件
├── docker-compose.yml       # Docker Compose配置
├── requirements.txt         # Python依赖
└── README.md                # 项目说明
```

## 快速开始

### 本地开发

1. 克隆仓库

```bash
git clone <repository-url>
cd services/rag-service
```

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 运行测试

```bash
pytest
```

5. 使用Docker Compose运行服务

```bash
docker-compose up -d
```

服务将在以下端口可用：
- RAG服务: http://localhost:8000
- Neo4j: http://localhost:7474
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000

### Kubernetes部署

1. 配置Kubernetes

确保您有一个正常运行的Kubernetes集群并配置好了kubectl。

2. 使用部署脚本部署

```bash
cd scripts/deploy
chmod +x deploy.sh
./deploy.sh dev  # 部署到开发环境
```

可用的环境包括:
- `dev`: 开发环境
- `test`: 测试环境
- `prod`: 生产环境

## CI/CD

项目使用GitHub Actions进行持续集成和部署。工作流程包括：

1. 测试：运行单元测试和代码质量检查
2. 构建：构建Docker镜像并推送到容器仓库
3. 部署：部署到Kubernetes集群

详情请查看 `.github/workflows/ci-cd.yml` 文件。

## API文档

部署后，可以通过访问 `/docs` 或 `/redoc` 查看API文档。

### 新增API端点

- `/api/specialized/precision-medicine` - 精准医学知识检索
- `/api/specialized/multimodal-health` - 多模态健康数据检索
- `/api/specialized/environmental-health` - 环境健康知识检索
- `/api/specialized/mental-health` - 心理健康知识检索

## 专业领域检索

RAG服务现在支持以下专业领域的特定检索功能：

1. **精准医学检索**
   - 支持基因组学数据检索
   - 支持基于药物相互作用的检索
   - 支持基于疾病风险因子的检索
   - 提供证据级别评估

2. **多模态健康检索**
   - 支持图像特征语义检索
   - 支持音频特征语义检索
   - 支持可穿戴设备数据模式检索
   - 支持多源数据融合检索

3. **环境健康检索**
   - 支持环境因素与健康影响关联检索
   - 支持季节性和气候变化影响检索
   - 支持环境暴露途径特定检索
   - 支持地域特定环境健康检索

4. **心理健康检索**
   - 支持基于心理学领域的检索
   - 支持基于年龄群体的检索
   - 支持基于干预技术的检索
   - 优先提供具有完整干预方案的知识

## 监控

服务包含Prometheus指标端点（`/metrics`），可以与Grafana集成进行监控和可视化。

## 故障排查

1. 检查服务日志

```bash
kubectl logs -n <namespace> -l app=rag-service
```

2. 检查服务状态

```bash
kubectl get pods -n <namespace> -l app=rag-service
```

3. 检查服务健康状态

```bash
curl http://rag-service-host/health
```

## 许可证

© 索克生活科技

# RAG Service (Podman版本)

## 版本
当前版本：1.0.1-podman

## 更新日志
- 2024-03-27: 添加Podman容器支持
- 迁移构建系统从Docker到Podman
- 优化健康检查机制
- 更新CI/CD流程

## 构建说明
本服务现已支持使用Podman进行构建和部署：

```bash
# 构建镜像
podman build -t registry.cn-hangzhou.aliyuncs.com/suoke/rag-service:latest -f Dockerfile.podman .

# 运行容器
podman run -d -p 8000:8000 registry.cn-hangzhou.aliyuncs.com/suoke/rag-service:latest
```

## 健康检查
服务提供了基本的健康检查端点：
- 端口：8000
- 路径：/
- 返回：`{"status": "healthy", "podman": true}`

## CI/CD
- 使用GitHub Actions自动构建
- 自动推送到阿里云容器镜像服务
- 自动生成Kubernetes部署配置

## 注意事项
- 确保已安装Podman
- 确保有阿里云容器镜像服务的访问权限
- 遵循最新的Podman最佳实践