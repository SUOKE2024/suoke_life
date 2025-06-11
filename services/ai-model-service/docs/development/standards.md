# 代码规范

本文档定义了AI Model Service项目的代码规范和最佳实践，确保代码质量、可维护性和团队协作效率。

## 🎯 总体原则

### 1. 代码质量原则
- **可读性优先**: 代码应该易于理解和维护
- **一致性**: 遵循统一的编码风格和命名规范
- **简洁性**: 避免过度复杂的设计和实现
- **可测试性**: 编写易于测试的代码
- **文档化**: 提供充分的文档和注释

### 2. 开发原则
- **DRY (Don't Repeat Yourself)**: 避免重复代码
- **SOLID**: 遵循面向对象设计原则
- **KISS (Keep It Simple, Stupid)**: 保持简单
- **YAGNI (You Aren't Gonna Need It)**: 不要过度设计

## 🐍 Python 代码规范

### 1. 基础规范

#### PEP 8 合规性
项目严格遵循 [PEP 8](https://pep8.org/) 规范，使用自动化工具确保合规性。

#### 代码格式化工具
```bash
# Black - 代码格式化
uv run black src tests

# isort - 导入排序
uv run isort src tests

# Ruff - 代码检查和自动修复
uv run ruff check --fix src tests
```

### 2. 命名规范

#### 变量和函数
```python
# ✅ 好的命名
user_name = "张三"
model_config = ModelConfig()
deployment_status = "running"

def get_model_status(model_id: str) -> str:
    """获取模型状态"""
    pass

def deploy_model_to_kubernetes(config: ModelConfig) -> DeploymentInfo:
    """部署模型到Kubernetes集群"""
    pass

# ❌ 避免的命名
n = "张三"  # 不清晰
cfg = ModelConfig()  # 缩写不明确
s = "running"  # 单字母变量

def get_status(id):  # 参数类型不明确
    pass
```

#### 类和模块
```python
# ✅ 类名使用 PascalCase
class ModelManager:
    """模型管理器"""
    pass

class DeploymentInfo:
    """部署信息"""
    pass

# ✅ 模块名使用 snake_case
# model_manager.py
# deployment_info.py
# kubernetes_client.py
```

#### 常量
```python
# ✅ 常量使用 UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30
MAX_RETRY_ATTEMPTS = 3
KUBERNETES_NAMESPACE = "suoke-life"

# 配置常量
class Config:
    DEFAULT_MODEL_REPLICAS = 1
    MAX_MODEL_REPLICAS = 10
    HEALTH_CHECK_INTERVAL = 30
```

### 3. 类型注解

#### 强制类型注解
所有函数和方法必须包含类型注解：

```python
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

# ✅ 完整的类型注解
def deploy_model(
    config: ModelConfig,
    namespace: str = "default",
    timeout: int = 300
) -> DeploymentInfo:
    """部署模型到Kubernetes"""
    pass

async def get_model_status(
    model_id: str,
    include_metrics: bool = False
) -> Optional[DeploymentInfo]:
    """异步获取模型状态"""
    pass

# ✅ 类属性类型注解
class ModelManager:
    """模型管理器"""
    
    def __init__(self, k8s_client: KubernetesClient) -> None:
        self.k8s_client: KubernetesClient = k8s_client
        self.deployments: Dict[str, DeploymentInfo] = {}
        self.metrics: Optional[MetricsCollector] = None
```

#### 复杂类型定义
```python
from typing import TypeAlias, Protocol, Generic, TypeVar

# 类型别名
ModelID: TypeAlias = str
ResourceRequirements: TypeAlias = Dict[str, str]

# 协议定义
class Deployable(Protocol):
    """可部署的协议"""
    
    def deploy(self) -> DeploymentInfo:
        """部署方法"""
        ...

# 泛型类型
T = TypeVar('T')

class Repository(Generic[T]):
    """通用仓库类"""
    
    def save(self, entity: T) -> T:
        """保存实体"""
        pass
```

### 4. 文档字符串

#### 函数文档
```python
def deploy_model(config: ModelConfig, namespace: str = "default") -> DeploymentInfo:
    """部署AI模型到Kubernetes集群
    
    Args:
        config: 模型配置信息，包含镜像、资源需求等
        namespace: Kubernetes命名空间，默认为"default"
        
    Returns:
        DeploymentInfo: 部署信息，包含状态、端点等
        
    Raises:
        DeploymentError: 当部署失败时抛出
        ValidationError: 当配置验证失败时抛出
        
    Example:
        >>> config = ModelConfig(
        ...     model_id="tcm_diagnosis",
        ...     docker_image="suoke/tcm:1.0.0"
        ... )
        >>> deployment = deploy_model(config)
        >>> print(deployment.status)
        'running'
    """
    pass
```

#### 类文档
```python
class ModelManager:
    """AI模型管理器
    
    负责管理AI模型的完整生命周期，包括部署、监控、扩缩容和删除。
    支持多种AI框架和Kubernetes部署。
    
    Attributes:
        k8s_client: Kubernetes客户端
        deployments: 当前部署的模型字典
        metrics: 指标收集器
        
    Example:
        >>> manager = ModelManager(k8s_client)
        >>> deployment = manager.deploy_model(config)
        >>> status = manager.get_model_status(deployment.model_id)
    """
    
    def __init__(self, k8s_client: KubernetesClient) -> None:
        """初始化模型管理器
        
        Args:
            k8s_client: Kubernetes客户端实例
        """
        pass
```

### 5. 错误处理

#### 异常定义
```python
# ✅ 自定义异常类
class AIModelServiceError(Exception):
    """AI模型服务基础异常"""
    pass

class DeploymentError(AIModelServiceError):
    """部署相关异常"""
    
    def __init__(self, message: str, model_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.model_id = model_id
        self.details = details or {}

class ValidationError(AIModelServiceError):
    """验证相关异常"""
    pass

class KubernetesError(AIModelServiceError):
    """Kubernetes操作异常"""
    pass
```

#### 异常处理
```python
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

# ✅ 结构化异常处理
async def deploy_model(config: ModelConfig) -> DeploymentInfo:
    """部署模型"""
    try:
        # 验证配置
        config.validate()
        
        # 部署到Kubernetes
        deployment = await self._deploy_to_k8s(config)
        
        logger.info(
            "模型部署成功",
            model_id=config.model_id,
            deployment_id=deployment.deployment_id
        )
        
        return deployment
        
    except ValidationError as e:
        logger.error(
            "模型配置验证失败",
            model_id=config.model_id,
            error=str(e)
        )
        raise
        
    except KubernetesError as e:
        logger.error(
            "Kubernetes部署失败",
            model_id=config.model_id,
            error=str(e)
        )
        raise DeploymentError(
            f"部署模型失败: {e}",
            model_id=config.model_id,
            details={"kubernetes_error": str(e)}
        )
        
    except Exception as e:
        logger.exception(
            "部署过程中发生未知错误",
            model_id=config.model_id
        )
        raise DeploymentError(
            f"部署失败: {e}",
            model_id=config.model_id
        )

# ✅ 重试机制
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def check_model_health(model_id: str) -> bool:
    """检查模型健康状态，支持重试"""
    try:
        response = await self.http_client.get(f"/models/{model_id}/health")
        return response.status_code == 200
    except Exception as e:
        logger.warning(
            "模型健康检查失败，将重试",
            model_id=model_id,
            error=str(e)
        )
        raise
```

### 6. 异步编程

#### 异步函数规范
```python
import asyncio
from typing import AsyncGenerator, AsyncIterator

# ✅ 异步函数命名和实现
async def deploy_model_async(config: ModelConfig) -> DeploymentInfo:
    """异步部署模型"""
    async with self.k8s_client.session() as session:
        deployment = await session.create_deployment(config)
        await deployment.wait_for_ready(timeout=300)
        return deployment

# ✅ 异步生成器
async def stream_model_logs(model_id: str) -> AsyncGenerator[str, None]:
    """流式获取模型日志"""
    async with self.k8s_client.watch_logs(model_id) as stream:
        async for line in stream:
            yield line

# ✅ 异步上下文管理器
class ModelDeploymentContext:
    """模型部署上下文管理器"""
    
    async def __aenter__(self) -> 'ModelDeploymentContext':
        await self.setup_resources()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.cleanup_resources()
```

## 🏗️ 架构规范

### 1. 项目结构

#### 模块组织
```
src/ai_model_service/
├── __init__.py
├── main.py                 # 应用入口
├── api/                    # API层
│   ├── __init__.py
│   ├── app.py             # FastAPI应用
│   └── v1/                # API版本
│       ├── models.py      # 模型管理API
│       └── health.py      # 健康检查API
├── core/                   # 核心业务逻辑
│   ├── __init__.py
│   ├── manager.py         # 模型管理器
│   ├── deployer.py        # 部署器
│   ├── monitor.py         # 监控器
│   └── inference.py       # 推理引擎
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── config.py          # 配置模型
│   ├── deployment.py      # 部署模型
│   └── inference.py       # 推理模型
├── utils/                  # 工具函数
│   ├── __init__.py
│   ├── k8s.py            # Kubernetes工具
│   ├── logging.py        # 日志工具
│   └── metrics.py        # 指标工具
└── config/                # 配置管理
    ├── __init__.py
    └── settings.py       # 设置
```

#### 依赖注入
```python
from typing import Protocol
from abc import ABC, abstractmethod

# ✅ 接口定义
class ModelRepository(Protocol):
    """模型仓库接口"""
    
    async def save(self, model: ModelConfig) -> None:
        """保存模型配置"""
        ...
        
    async def get(self, model_id: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        ...

# ✅ 依赖注入
class ModelManager:
    """模型管理器"""
    
    def __init__(
        self,
        repository: ModelRepository,
        k8s_client: KubernetesClient,
        metrics: MetricsCollector
    ) -> None:
        self.repository = repository
        self.k8s_client = k8s_client
        self.metrics = metrics
```

### 2. 数据模型

#### Pydantic 模型
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from enum import Enum

# ✅ 枚举定义
class ModelType(str, Enum):
    """模型类型枚举"""
    TCM_DIAGNOSIS = "tcm_diagnosis"
    MULTIMODAL = "multimodal"
    TREATMENT = "treatment"

class DeploymentStatus(str, Enum):
    """部署状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"

# ✅ 数据模型定义
class ModelConfig(BaseModel):
    """模型配置"""
    
    model_id: str = Field(..., description="模型唯一标识")
    name: str = Field(..., description="模型名称")
    version: str = Field(..., description="模型版本")
    model_type: ModelType = Field(..., description="模型类型")
    docker_image: str = Field(..., description="Docker镜像")
    resource_requirements: Dict[str, str] = Field(
        default_factory=dict,
        description="资源需求"
    )
    
    @validator('model_id')
    def validate_model_id(cls, v: str) -> str:
        """验证模型ID格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('模型ID只能包含字母、数字、下划线和连字符')
        return v
    
    @validator('version')
    def validate_version(cls, v: str) -> str:
        """验证版本格式"""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('版本号必须符合语义化版本格式 (x.y.z)')
        return v
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"
```

## 🧪 测试规范

### 1. 测试结构

#### 测试文件组织
```
tests/
├── __init__.py
├── conftest.py            # 测试配置和fixture
├── unit/                  # 单元测试
│   ├── test_models.py
│   ├── test_manager.py
│   └── test_utils.py
├── integration/           # 集成测试
│   ├── test_api.py
│   └── test_k8s.py
└── fixtures/              # 测试数据
    ├── model_configs.py
    └── deployment_data.py
```

#### 测试命名
```python
# ✅ 测试函数命名
def test_deploy_model_with_valid_config():
    """测试使用有效配置部署模型"""
    pass

def test_deploy_model_with_invalid_config_raises_validation_error():
    """测试使用无效配置部署模型时抛出验证错误"""
    pass

def test_get_model_status_returns_correct_info():
    """测试获取模型状态返回正确信息"""
    pass

# ✅ 测试类命名
class TestModelManager:
    """模型管理器测试"""
    
    def test_init_with_valid_dependencies(self):
        """测试使用有效依赖初始化"""
        pass
        
    def test_deploy_model_success(self):
        """测试成功部署模型"""
        pass
```

### 2. 测试实现

#### Fixture 定义
```python
# conftest.py
import pytest
from unittest.mock import Mock, AsyncMock
from ai_model_service.models.config import ModelConfig
from ai_model_service.core.manager import ModelManager

@pytest.fixture
def sample_model_config() -> ModelConfig:
    """示例模型配置"""
    return ModelConfig(
        model_id="test_model",
        name="测试模型",
        version="1.0.0",
        model_type="tcm_diagnosis",
        docker_image="test/model:1.0.0"
    )

@pytest.fixture
def mock_k8s_client() -> Mock:
    """模拟Kubernetes客户端"""
    client = Mock()
    client.create_deployment = AsyncMock()
    client.get_deployment = AsyncMock()
    return client

@pytest.fixture
def model_manager(mock_k8s_client) -> ModelManager:
    """模型管理器实例"""
    return ModelManager(k8s_client=mock_k8s_client)
```

#### 单元测试
```python
import pytest
from unittest.mock import AsyncMock, patch
from ai_model_service.core.manager import ModelManager
from ai_model_service.models.config import ModelConfig

class TestModelManager:
    """模型管理器测试"""
    
    @pytest.mark.asyncio
    async def test_deploy_model_success(
        self,
        model_manager: ModelManager,
        sample_model_config: ModelConfig,
        mock_k8s_client: Mock
    ):
        """测试成功部署模型"""
        # Arrange
        expected_deployment = DeploymentInfo(
            model_id=sample_model_config.model_id,
            status="running"
        )
        mock_k8s_client.create_deployment.return_value = expected_deployment
        
        # Act
        result = await model_manager.deploy_model(sample_model_config)
        
        # Assert
        assert result.model_id == sample_model_config.model_id
        assert result.status == "running"
        mock_k8s_client.create_deployment.assert_called_once_with(
            sample_model_config
        )
    
    @pytest.mark.asyncio
    async def test_deploy_model_with_invalid_config_raises_error(
        self,
        model_manager: ModelManager
    ):
        """测试使用无效配置部署模型时抛出错误"""
        # Arrange
        invalid_config = ModelConfig(
            model_id="",  # 无效的空ID
            name="测试模型",
            version="1.0.0",
            model_type="tcm_diagnosis",
            docker_image="test/model:1.0.0"
        )
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await model_manager.deploy_model(invalid_config)
```

#### 集成测试
```python
import pytest
from httpx import AsyncClient
from ai_model_service.api.app import create_app

@pytest.mark.asyncio
class TestModelAPI:
    """模型API集成测试"""
    
    async def test_deploy_model_endpoint(self):
        """测试部署模型API端点"""
        # Arrange
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "config": {
                    "model_id": "test_model",
                    "name": "测试模型",
                    "version": "1.0.0",
                    "model_type": "tcm_diagnosis",
                    "docker_image": "test/model:1.0.0"
                }
            }
            
            # Act
            response = await client.post("/api/v1/models/deploy", json=payload)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert "deployment_id" in data
            assert data["message"] == "模型部署成功"
```

## 📊 性能规范

### 1. 性能要求

#### 响应时间
- API响应时间 < 200ms (P95)
- 模型推理时间 < 5s (P95)
- 健康检查响应时间 < 50ms

#### 吞吐量
- API QPS > 1000
- 并发推理请求 > 100

#### 资源使用
- 内存使用率 < 80%
- CPU使用率 < 70%
- 磁盘使用率 < 85%

### 2. 性能优化

#### 异步编程
```python
import asyncio
from asyncio import Semaphore

class ModelManager:
    """模型管理器"""
    
    def __init__(self, max_concurrent_deployments: int = 10):
        self._deployment_semaphore = Semaphore(max_concurrent_deployments)
    
    async def deploy_model(self, config: ModelConfig) -> DeploymentInfo:
        """限制并发部署数量"""
        async with self._deployment_semaphore:
            return await self._do_deploy(config)
```

#### 缓存策略
```python
from functools import lru_cache
from typing import Optional
import time

class ModelStatusCache:
    """模型状态缓存"""
    
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self._cache: Dict[str, Tuple[DeploymentInfo, float]] = {}
    
    def get(self, model_id: str) -> Optional[DeploymentInfo]:
        """获取缓存的状态"""
        if model_id in self._cache:
            info, timestamp = self._cache[model_id]
            if time.time() - timestamp < self.ttl:
                return info
            else:
                del self._cache[model_id]
        return None
    
    def set(self, model_id: str, info: DeploymentInfo) -> None:
        """设置缓存"""
        self._cache[model_id] = (info, time.time())
```

## 🔒 安全规范

### 1. 输入验证
```python
from pydantic import validator, Field
import re

class ModelConfig(BaseModel):
    """模型配置"""
    
    model_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$')
    docker_image: str = Field(..., regex=r'^[a-zA-Z0-9._/-]+:[a-zA-Z0-9._-]+$')
    
    @validator('docker_image')
    def validate_docker_image(cls, v: str) -> str:
        """验证Docker镜像格式"""
        # 防止镜像注入攻击
        if any(char in v for char in ['&', '|', ';', '`', '$']):
            raise ValueError('Docker镜像名称包含非法字符')
        return v
```

### 2. 敏感信息处理
```python
import os
from typing import Optional

class SecretManager:
    """密钥管理器"""
    
    @staticmethod
    def get_secret(key: str) -> Optional[str]:
        """安全获取密钥"""
        # 优先从环境变量获取
        value = os.getenv(key)
        if value:
            return value
            
        # 从Kubernetes Secret获取
        try:
            with open(f'/var/secrets/{key}', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """遮蔽敏感数据"""
        sensitive_keys = {'password', 'token', 'key', 'secret'}
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked_data[key] = '***'
                
        return masked_data
```

## 📝 提交规范

### 1. Git 提交信息
```bash
# ✅ 好的提交信息
feat: 添加模型批量推理API端点

- 实现批量推理请求处理
- 添加并发控制和超时机制
- 更新API文档和测试用例

Closes #123

# ✅ 提交类型
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式化
refactor: 重构
test:     测试相关
chore:    构建工具、依赖更新
```

### 2. 代码审查清单

#### 审查要点
- [ ] 代码符合项目规范
- [ ] 包含充分的测试
- [ ] 文档已更新
- [ ] 性能影响已评估
- [ ] 安全风险已考虑
- [ ] 向后兼容性已确认

## 🛠️ 工具配置

### 1. 开发工具配置

#### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py313']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 88
target-version = "py313"
select = ["E", "F", "W", "C", "N", "UP", "S", "B", "A", "C4", "T20"]
```

### 2. CI/CD 配置

#### GitHub Actions
```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install UV
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync --dev
      
      - name: Run code quality checks
        run: |
          uv run black --check src tests
          uv run isort --check-only src tests
          uv run ruff check src tests
          uv run mypy src
          uv run bandit -r src
      
      - name: Run tests
        run: uv run pytest --cov=ai_model_service
```

## 📚 参考资源

- [PEP 8 - Python代码风格指南](https://pep8.org/)
- [Google Python风格指南](https://google.github.io/styleguide/pyguide.html)
- [Clean Code原则](https://clean-code-developer.com/)
- [Python类型注解指南](https://docs.python.org/3/library/typing.html)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)
- [FastAPI最佳实践](https://fastapi.tiangolo.com/tutorial/)