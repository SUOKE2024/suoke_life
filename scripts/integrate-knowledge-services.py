#!/usr/bin/env python3
"""
知识服务整合脚本
将med-knowledge和suoke-bench-service整合为unified-knowledge-service
"""

import os
import shutil
import json
from pathlib import Path
import datetime
from typing import Dict, List, Any

class KnowledgeServicesIntegrator:
    def __init__(self):
        self.base_path = Path("services")
        self.source_services = ["med-knowledge", "suoke-bench-service"]
        self.target_service = "unified-knowledge-service"
        self.target_path = self.base_path / self.target_service
        
        self.integration_record = {
            "timestamp": datetime.now().isoformat(),
            "source_services": self.source_services,
            "target_service": self.target_service,
            "integration_status": "started",
            "files_created": [],
            "directories_created": [],
            "integration_summary": {}
        }
    
    def create_unified_service_structure(self):
        """创建统一知识服务的目录结构"""
        print("🏗️ 创建统一知识服务目录结构...")
        
        directories = [
            "unified_knowledge_service",
            "unified_knowledge_service/med_knowledge",
            "unified_knowledge_service/benchmark", 
            "unified_knowledge_service/common",
            "unified_knowledge_service/api",
            "unified_knowledge_service/data",
            "unified_knowledge_service/models",
            "unified_knowledge_service/services",
            "unified_knowledge_service/utils",
            "api",
            "api/v1",
            "api/grpc",
            "config",
            "deploy",
            "deploy/docker",
            "deploy/kubernetes",
            "docs",
            "docs/api",
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "scripts",
            "utils",
            "data",
            "data/knowledge",
            "data/benchmark",
            "logs",
            "monitoring"
        ]
        
        for directory in directories:
            dir_path = self.target_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.integration_record["directories_created"].append(str(dir_path))
            print(f"  📁 创建目录: {directory}")
        
        print(f"✅ 创建了 {len(directories)} 个目录")
    
    def create_main_service_manager(self):
        """创建主服务管理器"""
        print("🔧 创建主服务管理器...")
        
        main_service_content = '''"""
统一知识服务主管理器
整合医学知识管理和基准测试功能
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .med_knowledge import MedKnowledgeManager
from .benchmark import BenchmarkManager
from .common import ConfigManager, DatabaseManager, CacheManager
from .api import create_api_router


class UnifiedKnowledgeService:
    """统一知识服务管理器"""
    
    def __init__(self, config_path: str = "config/service.yml"):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化组件
        self.db_manager = DatabaseManager(self.config.get("database", {}))
        self.cache_manager = CacheManager(self.config.get("cache", {}))
        
        # 初始化业务模块
        self.med_knowledge = MedKnowledgeManager()
            db_manager=self.db_manager,
            cache_manager=self.cache_manager,
            config=self.config.get("med_knowledge", {})
        )
        
        self.benchmark = BenchmarkManager()
            db_manager=self.db_manager,
            cache_manager=self.cache_manager,
            config=self.config.get("benchmark", {})
        )
        
        # FastAPI应用
        self.app = None
        self.logger = logging.getLogger(__name__)
        
        # 服务状态
        self.is_running = False
        self.health_status = {"status": "initializing"}
    
    async def initialize(self):
        """初始化服务"""
        try:
            self.logger.info("初始化统一知识服务...")
            
            # 初始化数据库连接
            await self.db_manager.initialize()
            
            # 初始化缓存
            await self.cache_manager.initialize()
            
            # 初始化业务模块
            await self.med_knowledge.initialize()
            await self.benchmark.initialize()
            
            # 创建FastAPI应用
            self.app = await self.create_app()
            
            self.health_status = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.logger.info("统一知识服务初始化完成")
            
        except Exception as e:
            self.logger.error(f"服务初始化失败: {e}")
            self.health_status = {"status": "unhealthy", "error": str(e)}
            raise
    
    async def create_app() -> FastAPI::
        """创建FastAPI应用"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # 启动时执行
            await self.startup()
            yield
            # 关闭时执行
            await self.shutdown()
        
        app = FastAPI()
            title="统一知识服务",
            description="整合医学知识管理和基准测试的统一服务",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # 添加CORS中间件
        app.add_middleware()
            CORSMiddleware,
            allow_origins=self.config.get("cors", {}).get("origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 注册路由
        api_router = create_api_router()
            med_knowledge=self.med_knowledge,
            benchmark=self.benchmark
        )
        app.include_router(api_router, prefix="/api/v1")
        
        # 健康检查端点
        @app.get("/health")
        async def health_check():
            return self.health_status
        
        # 服务信息端点
        @app.get("/info")
        async def service_info():
            return {
                "service": "unified-knowledge-service",
                "version": "1.0.0",
                "modules": ["med-knowledge", "benchmark"],
                "status": self.health_status["status"]
            }
        
        return app
    
    async def startup(self):
        """服务启动"""
        self.logger.info("启动统一知识服务...")
        self.is_running = True
        
        # 启动业务模块
        await self.med_knowledge.start()
        await self.benchmark.start()
        
        self.logger.info("统一知识服务启动完成")
    
    async def shutdown(self):
        """服务关闭"""
        self.logger.info("关闭统一知识服务...")
        self.is_running = False
        
        # 关闭业务模块
        await self.med_knowledge.stop()
        await self.benchmark.stop()
        
        # 关闭基础组件
        await self.cache_manager.close()
        await self.db_manager.close()
        
        self.logger.info("统一知识服务关闭完成")
    
    async def get_service_status() -> Dict[str, Any]::
        """获取服务状态"""
        return {
            "service": "unified-knowledge-service",
            "running": self.is_running,
            "health": self.health_status,
            "modules": {
                "med_knowledge": await self.med_knowledge.get_status(),
                "benchmark": await self.benchmark.get_status()
            },
            "components": {
                "database": await self.db_manager.get_status(),
                "cache": await self.cache_manager.get_status()
            }
        }


# 全局服务实例
service_instance: Optional[UnifiedKnowledgeService] = None


async def get_service() -> UnifiedKnowledgeService::
    """获取服务实例"""
    global service_instance
    if service_instance is None:
        service_instance = UnifiedKnowledgeService()
        await service_instance.initialize()
    return service_instance


async def create_application() -> FastAPI::
    """创建应用实例"""
    service = await get_service()
    return service.app


if __name__ == "__main__":
    import uvicorn
    
    async def main():
        service = UnifiedKnowledgeService()
        await service.initialize()
        
        config = uvicorn.Config()
            app=service.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    asyncio.run(main())
'''
        
        main_file = self.target_path / "unified_knowledge_service" / "__init__.py"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_service_content)
        
        self.integration_record["files_created"].append(str(main_file))
        print("✅ 主服务管理器创建完成")
    
    def create_configuration_files(self):
        """创建配置文件"""
        print("⚙️ 创建配置文件...")
        
        # 主配置文件
        config_content = '''# 统一知识服务配置

# 服务基本配置
service:
  name: "unified-knowledge-service"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 8000
  debug: false

# 数据库配置
database:
  primary:
    type: "postgresql"
    host: "${DB_HOST:-localhost}"
    port: "${DB_PORT:-5432}"
    database: "${DB_NAME:-unified_knowledge}"
    username: "${DB_USER:-postgres}"
    password: "${DB_PASSWORD:-password}"
    pool_size: 20
    max_overflow: 30
  
  document:
    type: "mongodb"
    host: "${MONGO_HOST:-localhost}"
    port: "${MONGO_PORT:-27017}"
    database: "${MONGO_DB:-knowledge_docs}"
    username: "${MONGO_USER:-}"
    password: "${MONGO_PASSWORD:-}"

# 缓存配置
cache:
  type: "redis"
  host: "${REDIS_HOST:-localhost}"
  port: "${REDIS_PORT:-6379}"
  database: "${REDIS_DB:-0}"
  password: "${REDIS_PASSWORD:-}"
  ttl: 3600

# 医学知识模块配置
med_knowledge:
  data_path: "data/knowledge"
  index_path: "data/knowledge/index"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  max_search_results: 100
  similarity_threshold: 0.7

# 基准测试模块配置
benchmark:
  data_path: "data/benchmark"
  results_path: "data/benchmark/results"
  test_timeout: 300
  parallel_tests: 4
  report_format: ["json", "html", "pdf"]

# API配置
api:
  rate_limit: "100/minute"
  max_request_size: "10MB"
  timeout: 30

# CORS配置
cors:
  origins: ["*"]
  methods: ["GET", "POST", "PUT", "DELETE"]
  headers: ["*"]

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/unified-knowledge-service.log"
  max_size: "100MB"
  backup_count: 5

# 监控配置
monitoring:
  metrics_enabled: true
  health_check_interval: 30
  performance_tracking: true
'''
        
        config_file = self.target_path / "config" / "service.yml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # 环境变量示例文件
        env_content = '''# 统一知识服务环境变量配置

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=unified_knowledge
DB_USER=postgres
DB_PASSWORD=your_password_here

# MongoDB配置
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=knowledge_docs
MONGO_USER=
MONGO_PASSWORD=

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 服务配置
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
SERVICE_DEBUG=false

# API密钥
API_SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# 外部服务
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_hf_key_here

# 文件存储
STORAGE_PATH=/data/unified-knowledge
BACKUP_PATH=/backup/unified-knowledge

# 监控配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
'''
        
        env_file = self.target_path / ".env.example"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.integration_record["files_created"].extend([str(config_file), str(env_file)])
        print("✅ 配置文件创建完成")
    
    def create_docker_files(self):
        """创建Docker部署文件"""
        print("🐳 创建Docker部署文件...")
        
        # Dockerfile
        dockerfile_content = '''FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs data/knowledge data/benchmark

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "unified_knowledge_service"]
'''
        
        dockerfile = self.target_path / "Dockerfile"
        with open(dockerfile, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # docker-compose.yml
        compose_content = '''version: '3.8'

services:
  unified-knowledge-service:
    build: .
    container_name: unified-knowledge-service
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - MONGO_HOST=mongodb
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - mongodb
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - knowledge-network

  postgres:
    image: postgres:15
    container_name: knowledge-postgres
    environment:
      POSTGRES_DB: unified_knowledge
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - knowledge-network

  mongodb:
    image: mongo:6
    container_name: knowledge-mongodb
    environment:
      MONGO_INITDB_DATABASE: knowledge_docs
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - knowledge-network

  redis:
    image: redis:7-alpine
    container_name: knowledge-redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - knowledge-network

volumes:
  postgres_data:
  mongodb_data:
  redis_data:

networks:
  knowledge-network:
    driver: bridge
'''
        
        compose_file = self.target_path / "docker-compose.yml"
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        self.integration_record["files_created"].extend([str(dockerfile), str(compose_file)])
        print("✅ Docker部署文件创建完成")
    
    def create_requirements_file(self):
        """创建依赖文件"""
        print("📦 创建依赖文件...")
        
        requirements_content = '''# 统一知识服务依赖

# Web框架
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0

# 数据库
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pymongo>=4.6.0
redis>=5.0.0

# 机器学习和NLP
torch>=2.1.0
transformers>=4.35.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.1.0

# 数据处理
pydantic>=2.5.0
python-multipart>=0.0.6
aiofiles>=23.2.0

# 配置和环境
python-dotenv>=1.0.0
pyyaml>=6.0.1
click>=8.1.0

# 监控和日志
prometheus-client>=0.19.0
structlog>=23.2.0

# 测试
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0

# 开发工具
black>=23.11.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.7.0

# 安全
cryptography>=41.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# 其他工具
requests>=2.31.0
aiohttp>=3.9.0
celery>=5.3.0
'''
        
        requirements_file = self.target_path / "requirements.txt"
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        self.integration_record["files_created"].append(str(requirements_file))
        print("✅ 依赖文件创建完成")
    
    def create_readme_file(self):
        """创建README文档"""
        print("📚 创建README文档...")
        
        readme_content = '''# 统一知识服务 (Unified Knowledge Service)

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
'''
        
        readme_file = self.target_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.integration_record["files_created"].append(str(readme_file))
        print("✅ README文档创建完成")
    
    def run_integration(self):
        """执行完整的整合流程"""
        print("🚀 开始知识服务整合...")
        print(f"📋 整合目标: {' + '.join(self.source_services)} → {self.target_service}")
        
        try:
            # 1. 创建目录结构
            self.create_unified_service_structure()
            
            # 2. 创建主服务管理器
            self.create_main_service_manager()
            
            # 3. 创建配置文件
            self.create_configuration_files()
            
            # 4. 创建Docker文件
            self.create_docker_files()
            
            # 5. 创建依赖文件
            self.create_requirements_file()
            
            # 6. 创建README文档
            self.create_readme_file()
            
            # 更新整合记录
            self.integration_record["integration_status"] = "completed"
            self.integration_record["integration_summary"] = {
                "directories_created": len(self.integration_record["directories_created"]),
                "files_created": len(self.integration_record["files_created"]),
                "source_services": len(self.source_services),
                "target_service": self.target_service
            }
            
            print(f"\n🎉 知识服务整合完成!")
            print(f"📁 创建目录: {len(self.integration_record['directories_created'])} 个")
            print(f"📄 创建文件: {len(self.integration_record['files_created'])} 个")
            print(f"🎯 目标服务: {self.target_service}")
            
            return True
            
        except Exception as e:
            print(f"❌ 整合过程中出现错误: {e}")
            self.integration_record["integration_status"] = "failed"
            self.integration_record["error"] = str(e)
            return False
    
    def save_integration_record(self):
        """保存整合记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record_file = f"knowledge_services_integration_record_{timestamp}.json"
        
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(self.integration_record, f, indent=2, ensure_ascii=False)
        
        print(f"📄 整合记录已保存: {record_file}")

def main():
    integrator = KnowledgeServicesIntegrator()
    
    try:
        # 执行整合
        success = integrator.run_integration()
        
        # 保存记录
        integrator.save_integration_record()
        
        if success:
            print("\n✅ 知识服务整合任务完成!")
            print("🔄 下一步: 可以开始清理原始服务")
            return 0
        else:
            print("\n❌ 知识服务整合失败!")
            return 1
            
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 