# 索克生活知识图谱服务

索克生活平台知识图谱服务，基于Neo4j和Milvus的中医知识图谱系统，提供中医药材、方剂、症状等实体关联知识查询和管理。

> **重要提示**: 本服务已从Node.js重构为Go实现，请参考下方关于重构的说明。

## 重构说明

本服务已从Node.js重构为Go实现，主要变化包括：

- 使用Go语言重新实现了所有核心功能
- 保持了相同的API接口和功能
- 数据库连接和查询逻辑优化
- 新增高效的数据导入工具
- 性能显著提升

如果需要访问旧版Node.js代码，请查看`node-backup-*`目录或git历史版本。

## 目录结构

```
.
├── cmd/                  # 可执行命令
│   ├── server/           # API服务器入口
│   └── importer/         # 数据导入工具
├── internal/             # 内部包
│   ├── api/              # API处理程序
│   ├── config/           # 配置
│   ├── database/         # 数据库连接
│   ├── domain/           # 领域模型
│   │   ├── entities/     # 实体定义
│   │   ├── repositories/ # 存储库接口
│   ├── infrastructure/   # 基础设施
│   │   ├── repositories/ # 存储库实现
├── pkg/                  # 公共包
├── data/                 # 数据文件
├── docs/                 # 文档
├── k8s/                  # Kubernetes配置
└── clean-scripts/        # 迁移/清理脚本
```

## 功能特点

- 知识图谱节点和关系管理
- 中医药材和方剂导入和查询
- 知识实体关系分析
- 图谱可视化数据格式支持
- 搜索和过滤
- 矢量相似度搜索

## 环境要求

- Go 1.20+
- Neo4j 4.4+
- Milvus 2.3+
- Redis 6.0+

## 安装和运行

### 快速启动（推荐）

使用提供的便捷脚本快速启动服务：

```bash
# 本地启动（需要自行配置Neo4j）
./scripts/start.sh

# 使用Docker Compose启动完整环境（包含Neo4j）
./scripts/docker-start.sh
```

### 本地开发

1. 克隆代码库：

```bash
git clone https://github.com/suoke-life/knowledge-graph-service.git
cd knowledge-graph-service
```

2. 构建代码：

```bash
go build -o knowledge-graph-service ./cmd/server
```

3. 运行服务：

```bash
./knowledge-graph-service
```

### Docker构建

使用Docker构建镜像：

```bash
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service:latest .
```

### Docker Compose环境

使用Docker Compose快速启动完整环境（包含Neo4j数据库）：

```bash
# 构建并启动所有服务
docker-compose up -d

# 仅重建并启动知识图谱服务
docker-compose up -d --build knowledge-graph-service

# 查看服务日志
docker-compose logs -f knowledge-graph-service

# 停止所有服务
docker-compose down
```

Neo4j管理界面访问：
- 地址：http://localhost:7474
- 默认凭据：neo4j/suokeneo4j

### Kubernetes部署

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## 数据导入

使用数据导入工具导入中医知识图谱数据：

```bash
# 构建导入工具
go build -o importer ./cmd/importer

# 导入中药数据
./importer -source=data/herbs.csv -type=herbs

# 导入方剂数据
./importer -source=data/formulas.csv -type=formulas
```

## API接口

主要API接口包括：

- `/api/v1/nodes` - 知识图谱节点管理
- `/api/v1/relationships` - 知识图谱关系管理
- `/api/v1/tcm` - 中医专业知识查询
- `/api/v1/search` - 知识图谱搜索
- `/health` - 健康检查

详细API文档参见 `/docs/api.md`

## 配置选项

配置优先级：命令行参数 > 环境变量 > 配置文件

主要配置选项：

- `PORT` - API服务端口，默认3000
- `LOG_LEVEL` - 日志级别，可选：debug, info, warn, error
- `NEO4J_URI` - Neo4j数据库URI
- `NEO4J_USER` - Neo4j用户名
- `NEO4J_PASSWORD` - Neo4j密码
- `REDIS_HOST` - Redis主机地址
- `REDIS_PORT` - Redis端口
- `MILVUS_HOST` - Milvus主机地址
- `MILVUS_PORT` - Milvus端口

## 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 提交Pull Request

## 许可证

内部项目，版权所有 © 索克生活

## CI/CD 自动化流程

本项目支持通过自动化脚本进行构建和部署，并集成了GitLab CI/CD流水线。

### 使用自动化脚本

#### 手动构建和部署

项目提供了用于手动构建和部署的脚本`scripts/run-ci-cd.sh`，该脚本支持多架构镜像构建和Kubernetes部署。

##### 基本用法

```bash
# 完整流程：检查、测试、构建和部署
./scripts/run-ci-cd.sh

# 仅构建镜像，不部署
SKIP_DEPLOY=true ./scripts/run-ci-cd.sh

# 仅部署已构建的镜像
SKIP_LINT=true SKIP_TESTS=true SKIP_BUILD=true ./scripts/run-ci-cd.sh
```

##### 支持的环境变量

脚本支持以下环境变量来自定义构建和部署行为：

| 环境变量 | 描述 | 默认值 |
|----------|------|-------|
| `REGISTRY` | 容器镜像仓库地址 | `suoke-registry.cn-hangzhou.cr.aliyuncs.com` |
| `REPOSITORY` | 镜像名称 | `suoke/suoke-knowledge-graph-service` |
| `REGISTRY_USERNAME` | 镜像仓库用户名 | - |
| `REGISTRY_PASSWORD` | 镜像仓库密码 | - |
| `NAMESPACE` | Kubernetes命名空间 | `suoke-prod` |
| `VERSION` | 镜像版本号 | 自动生成 |
| `DOCKERFILE` | 多架构Dockerfile路径 | `Dockerfile.new` |
| `DOCKERFILE_AMD64` | AMD64架构专用Dockerfile路径 | `Dockerfile.amd64` |
| `SKIP_LINT` | 是否跳过代码检查 | `false` |
| `SKIP_TESTS` | 是否跳过单元测试 | `false` |
| `SKIP_BUILD` | 是否跳过镜像构建 | `false` |
| `SKIP_DEPLOY` | 是否跳过部署 | `false` |
| `BUILD_ARM64` | 是否构建单独的ARM64镜像 | `false` |
| `CI` | 是否在CI环境中运行 | `false` |

##### 示例：仅部署到开发环境

```bash
NAMESPACE=suoke-dev SKIP_LINT=true SKIP_TESTS=true SKIP_BUILD=true ./scripts/run-ci-cd.sh
```

#### 在GitLab CI/CD中使用

项目根目录下的`.gitlab-ci.yml`文件配置了完整的CI/CD流水线，包括以下阶段：

1. **lint**: 进行代码规范检查
2. **test**: 运行单元测试
3. **security**: 进行安全性扫描
4. **build**: 构建多架构Docker镜像
5. **deploy**: 部署到不同环境(开发、预发布、生产)

##### GitLab CI/CD变量配置

需要在GitLab项目中配置以下CI/CD变量：

| 变量名 | 描述 |
|--------|------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云容器镜像服务用户名 |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云容器镜像服务密码 |
| `KUBE_CONFIG_DEV` | 开发环境Kubernetes配置(Base64编码) |
| `KUBE_CONFIG_STAGING` | 预发布环境Kubernetes配置(Base64编码) |
| `KUBE_CONFIG_PROD` | 生产环境Kubernetes配置(Base64编码) |

##### 环境部署规则

不同环境的部署按照以下规则触发：

- **开发环境**: 当代码提交到`develop`分支时，可手动触发部署
- **预发布环境**: 当代码提交到`release/*`分支时，可手动触发部署
- **生产环境**: 当代码提交到`main`分支时，可手动触发部署

### 多架构支持

系统支持构建以下类型的Docker镜像：

1. 多架构镜像(`linux/amd64,linux/arm64`)
2. AMD64专用镜像
3. 可选的ARM64专用镜像

所有镜像会使用相同的版本号，但AMD64和ARM64专用镜像会添加架构后缀，例如：
- `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/suoke-knowledge-graph-service:1.0.0` (多架构)
- `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/suoke-knowledge-graph-service:1.0.0-amd64` (仅AMD64)
- `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/suoke-knowledge-graph-service:1.0.0-arm64` (仅ARM64)

## 问题排查

如果遇到部署问题，可以使用以下命令进行排查：

```bash
# 查看Pod状态
kubectl get pods -n suoke-prod -l app.kubernetes.io/name=knowledge-graph-service

# 查看Pod详情
kubectl describe pod -n suoke-prod <pod-name>

# 查看Pod日志
kubectl logs -n suoke-prod <pod-name>

# 使用分析脚本
./scripts/analyze-situation.sh
```

## 贡献指南

请参阅[贡献指南](CONTRIBUTING.md)了解如何为项目做出贡献。

## 许可证

本项目采用[MIT许可证](LICENSE)。