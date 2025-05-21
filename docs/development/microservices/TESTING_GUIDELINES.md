# 索克生活APP微服务测试标准化指南

## 目录

- [测试策略概述](#测试策略概述)
- [测试类型与范围](#测试类型与范围)
- [测试环境管理](#测试环境管理)
- [单元测试规范](#单元测试规范)
- [集成测试规范](#集成测试规范)
- [契约测试规范](#契约测试规范)
- [端到端测试规范](#端到端测试规范)
- [性能测试规范](#性能测试规范)
- [安全测试规范](#安全测试规范)
- [测试数据管理](#测试数据管理)
- [测试代码质量](#测试代码质量)
- [持续集成测试](#持续集成测试)
- [测试报告与指标](#测试报告与指标)

## 测试策略概述

索克生活APP微服务的测试策略基于测试金字塔原则，从下到上包括：

1. **单元测试**：测试单个组件的功能，速度快、数量多
2. **集成测试**：测试组件之间的交互，速度中等、数量适中
3. **端到端测试**：测试整个系统流程，速度慢、数量少

测试分布建议比例：70% 单元测试，20% 集成测试，10% 端到端测试。

### 测试责任分工

| 测试类型 | 责任方 | 执行频率 | 环境 |
|---------|-------|---------|------|
| 单元测试 | 开发人员 | 每次代码提交 | 开发环境 |
| 集成测试 | 开发人员 | 每次代码提交 | CI环境 |
| 契约测试 | 开发人员 | 每次接口变更 | CI环境 |
| 端到端测试 | QA团队/开发人员 | 每日/每次发布 | 测试环境 |
| 性能测试 | 性能测试专家 | 每次发布 | 性能测试环境 |
| 安全测试 | 安全团队 | 每次发布 | 专用安全测试环境 |

## 测试类型与范围

### 必须测试的内容

每个微服务必须确保以下方面得到充分测试：

1. **核心业务逻辑**：所有关键业务流程和规则
2. **异常处理**：错误条件、边界情况和异常流程
3. **数据验证**：输入验证、数据转换和格式化
4. **安全控制**：认证、授权和数据保护机制
5. **外部依赖**：与其他服务和系统的集成点
6. **性能指标**：关键操作的响应时间和资源使用
7. **可观测性**：日志、监控和追踪机制

### 测试范围界定

针对不同的代码变更，应执行不同范围的测试：

| 变更类型 | 单元测试 | 集成测试 | 端到端测试 | 性能测试 | 安全测试 |
|---------|---------|---------|-----------|---------|---------|
| 修复Bug | ✅ 相关组件 | ✅ 受影响功能 | ⚪ 选择性 | ⚪ 仅性能Bug | ⚪ 仅安全Bug |
| 新功能 | ✅ 全覆盖 | ✅ 全覆盖 | ✅ 关键流程 | ✅ 关键接口 | ✅ 基础扫描 |
| 重构 | ✅ 全覆盖 | ✅ 全覆盖 | ✅ 回归测试 | ✅ 基准对比 | ⚪ 选择性 |
| 配置变更 | ⚪ 选择性 | ✅ 受影响功能 | ⚪ 选择性 | ⚪ 选择性 | ⚪ 选择性 |
| 依赖升级 | ✅ 使用依赖的组件 | ✅ 相关集成点 | ⚪ 关键流程 | ✅ 基准对比 | ✅ 漏洞扫描 |

## 测试环境管理

### 标准测试环境

索克生活APP微服务采用以下标准测试环境：

1. **本地环境**（开发人员机器）
   - 目的：开发和单元测试
   - 依赖管理：使用Docker模拟外部服务
   - 数据库：本地测试数据库
   - 特点：快速、隔离、自包含

2. **CI环境**（持续集成）
   - 目的：自动化测试和构建验证
   - 依赖管理：模拟服务和测试双打
   - 数据库：专用CI测试数据库
   - 特点：自动化、可重复、临时性

3. **集成测试环境**
   - 目的：集成测试和API测试
   - 依赖管理：实际服务实例（测试版）
   - 数据库：隔离的集成测试数据库
   - 特点：近似生产、服务间可通信

4. **预生产环境**
   - 目的：端到端测试和性能测试
   - 依赖管理：完整服务集
   - 数据库：与生产结构相同（匿名数据）
   - 特点：与生产配置一致

### 环境配置管理

使用环境变量和配置文件管理不同环境的配置：

```yaml
# config.test.yaml 示例
environment: test
logging:
  level: debug
  format: json
database:
  host: test-db.suokelife.internal
  name: auth_db_test
  user: test_user
services:
  user_service: http://user-service.test.svc:8080
  health_service: http://health-service.test.svc:8080
```

### 测试数据隔离

每个测试环境应有自己的数据隔离策略：

1. **单元测试**：使用内存数据库或测试双打
2. **集成测试**：独立的测试数据库架构，测试前重置
3. **端到端测试**：预定义的测试数据集，测试后清理

## 单元测试规范

### 测试框架选择

根据服务技术栈选择测试框架：

- **Python服务**：pytest
- **Node.js服务**：Jest

### 单元测试命名规范

测试文件和函数命名应遵循明确的约定：

- **测试文件**：`{被测模块}_test.py` 或 `test_{被测模块}.py`
- **测试函数**：`test_应该做什么_当什么条件时`

```python
# user_service_test.py
def test_should_return_user_when_id_exists():
    # 测试代码

def test_should_raise_error_when_user_not_found():
    # 测试代码
```

### 测试结构 (AAA模式)

所有单元测试应遵循Arrange-Act-Assert模式：

```python
def test_should_calculate_correct_total_price():
    # Arrange - 准备测试数据和环境
    cart = ShoppingCart()
    cart.add_item(Item("apple", 1.0), quantity=3)
    cart.add_item(Item("banana", 0.5), quantity=2)
    
    # Act - 执行被测操作
    total = cart.calculate_total()
    
    # Assert - 验证结果
    assert total == 4.0, f"Expected total to be 4.0, got {total}"
```

### 模拟外部依赖

使用测试双打替代外部依赖：

```python
from unittest.mock import Mock, patch

def test_user_service_calls_repository():
    # 创建Mock对象
    mock_repo = Mock()
    mock_repo.get_user_by_id.return_value = {"id": "123", "name": "Test User"}
    
    # 注入Mock
    service = UserService(repository=mock_repo)
    
    # 执行测试
    result = service.get_user_profile("123")
    
    # 验证交互
    mock_repo.get_user_by_id.assert_called_once_with("123")
    assert result["name"] == "Test User"
```

### 参数化测试

使用参数化测试处理多个测试案例：

```python
import pytest

@pytest.mark.parametrize("input_value,expected_result", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25)
])
def test_square_function(input_value, expected_result):
    assert square(input_value) == expected_result
```

### 测试覆盖率要求

单元测试覆盖率目标：

- **语句覆盖率**：≥90%
- **分支覆盖率**：≥85%
- **核心业务逻辑**：100%

使用测试覆盖工具跟踪覆盖率：

```bash
# Python项目
pytest --cov=myapp --cov-report=xml --cov-report=term

```

## 集成测试规范

### 集成测试范围

集成测试应关注以下方面：

1. **组件集成**：验证内部组件的协作
2. **数据库集成**：验证数据持久化和检索
3. **外部服务集成**：验证与外部API的交互
4. **消息队列集成**：验证消息生产和消费

### 测试隔离策略

集成测试应使用以下隔离策略：

1. **数据库隔离**：专用测试数据库或架构
2. **服务隔离**：测试容器或独立测试实例
3. **外部依赖隔离**：测试双打或托管测试服务

### 数据库集成测试

使用测试容器进行数据库集成测试：

```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    container = PostgresContainer("postgres:13")
    container.start()
    yield container
    container.stop()

@pytest.fixture(scope="function")
def db_session(postgres_container):
    # 设置数据库连接
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string)
    
    # 创建表结构
    Base.metadata.create_all(engine)
    
    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # 清理
    session.close()
    Base.metadata.drop_all(engine)

def test_user_repository_integration(db_session):
    # 准备
    repo = UserRepository(db_session)
    new_user = User(username="testuser", email="test@example.com")
    
    # 执行
    repo.create(new_user)
    retrieved_user = repo.get_by_username("testuser")
    
    # 验证
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"
```

### 服务间集成测试

使用测试双打或实际服务实例进行服务间集成测试：

```python
def test_auth_service_integration_with_user_service():
    # 设置测试环境
    user_service_mock = MockUserService()
    user_service_mock.add_user("123", {"id": "123", "name": "Test User"})
    
    auth_service = AuthService(user_service=user_service_mock)
    
    # 执行测试
    token = auth_service.generate_token("123")
    user_info = auth_service.validate_token_and_get_user(token)
    
    # 验证
    assert user_info["id"] == "123"
    assert user_info["name"] == "Test User"
```

### API集成测试

使用HTTP客户端测试REST API接口：

```python
def test_auth_api_integration():
    # 设置测试客户端
    client = TestClient(app)
    
    # 注册用户
    register_response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test@123!"
    })
    assert register_response.status_code == 201
    
    # 登录
    login_response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "Test@123!"
    })
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    
    # 使用令牌获取用户资料
    profile_response = client.get("/api/v1/users/me", headers={
        "Authorization": f"Bearer {token_data['access_token']}"
    })
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["username"] == "testuser"
```