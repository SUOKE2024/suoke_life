# 统一知识服务 (Unified Knowledge Service)

## 概述

统一知识服务是索克生活平台的核心组件，整合了医学知识管理和基准测试功能，为平台提供统一的知识服务支持。

## 功能特性

### 🧠 医学知识管理
- **知识库管理**: 医学文献、临床指南、专家经验的统一管理
- **智能检索**: 基于语义的知识检索和推荐
- **知识图谱**: 医学概念和关系的图谱化表示
- **内容分析**: 自动化的医学文本分析和提取

### 📊 基准测试
- **性能评估**: 系统和算法的性能基准测试
- **质量评价**: 服务质量和准确性评估
- **比较分析**: 不同版本和配置的对比分析
- **报告生成**: 详细的测试报告和可视化

### 🔧 技术特性
- **异步架构**: 基于FastAPI的高性能异步处理
- **模块化设计**: 松耦合的模块化架构
- **多数据源**: 支持PostgreSQL、MongoDB、Redis
- **容器化**: 完整的Docker容器化支持
- **监控告警**: 完善的监控和健康检查

## 快速开始

### 环境要求
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- MongoDB 6+
- Redis 7+

### 安装部署

#### 1. 克隆代码
```bash
git clone <repository-url>
cd unified-knowledge-service
```

#### 2. 环境配置
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

#### 3. Docker部署（推荐）
```bash
docker-compose up -d
```

#### 4. 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m unified_knowledge_service
```

### API文档

服务启动后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 医学知识管理

#### 知识检索
```http
GET /api/v1/knowledge/search?q=关键词&limit=10
```

#### 知识图谱查询
```http
GET /api/v1/knowledge/graph?concept=概念名称
```

#### 文献管理
```http
POST /api/v1/knowledge/literature
GET /api/v1/knowledge/literature/{id}
```

### 基准测试

#### 创建测试
```http
POST /api/v1/benchmark/test
```

#### 获取测试结果
```http
GET /api/v1/benchmark/test/{test_id}/results
```

#### 生成报告
```http
POST /api/v1/benchmark/report
```

## 配置说明

### 主配置文件 (config/service.yml)

```yaml
service:
  name: "unified-knowledge-service"
  port: 8000

database:
  primary:
    type: "postgresql"
    host: "localhost"
    port: 5432
    database: "unified_knowledge"

med_knowledge:
  data_path: "data/knowledge"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

benchmark:
  data_path: "data/benchmark"
  test_timeout: 300
```

### 环境变量

主要环境变量说明：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DB_HOST | 数据库主机 | localhost |
| DB_PORT | 数据库端口 | 5432 |
| DB_NAME | 数据库名称 | unified_knowledge |
| REDIS_HOST | Redis主机 | localhost |
| MONGO_HOST | MongoDB主机 | localhost |

## 开发指南

### 项目结构

```
unified-knowledge-service/
├── unified_knowledge_service/    # 主服务代码
│   ├── med_knowledge/           # 医学知识模块
│   ├── benchmark/               # 基准测试模块
│   ├── common/                  # 公共组件
│   └── api/                     # API接口
├── config/                      # 配置文件
├── tests/                       # 测试代码
├── docs/                        # 文档
├── deploy/                      # 部署文件
└── data/                        # 数据目录
```

### 添加新功能

1. 在相应模块下创建新的功能模块
2. 在API层添加对应的路由
3. 编写单元测试和集成测试
4. 更新API文档

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=unified_knowledge_service
```

## 监控和运维

### 健康检查

```bash
curl http://localhost:8000/health
```

### 服务状态

```bash
curl http://localhost:8000/info
```

### 日志查看

```bash
# Docker环境
docker-compose logs -f unified-knowledge-service

# 本地环境
tail -f logs/unified-knowledge-service.log
```

### 性能监控

- Prometheus指标: http://localhost:8000/metrics
- 健康检查: http://localhost:8000/health

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接配置是否正确

2. **服务启动失败**
   - 检查端口是否被占用
   - 查看日志文件获取详细错误信息

3. **API响应慢**
   - 检查数据库查询性能
   - 验证缓存配置是否正确

### 日志级别

可以通过环境变量调整日志级别：
```bash
export LOG_LEVEL=DEBUG
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目维护者: 索克生活开发团队
- 邮箱: dev@suoke.life
- 文档: https://docs.suoke.life

---

**版本**: 1.0.0  
**更新时间**: 2025年6月9日
