# 认证服务测试文档

本文档提供了认证服务(auth-service)的测试说明，包括测试类型、覆盖率、环境配置和执行方法。

## 测试类型

认证服务测试包括以下类型：

1. **单元测试**: 测试独立模块的功能
   - 安全模块测试 (`test/unit/security/`)
   - 服务层测试 (`test/unit/service/`)
   - 仓储层测试 (`test/unit/repository/`)

2. **集成测试**: 测试多个组件之间的交互
   - API集成测试 (`test/integration/`)

## 测试覆盖率

### 当前覆盖率

| 模块              | 覆盖率  | 备注                           |
|------------------|--------|------------------------------|
| 安全模块           | 92%    | JWT(87%), MFA(93%), 密码(98%)  |
| 服务层             | -      | 待完成                         |
| 仓储层             | 14%    | 未完成（AuditLogEnum未定义）     |
| 整体覆盖率         | -      | 待计算                         |

## 测试环境配置

### 依赖安装

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-freezegun

# 安装服务依赖
pip install -r requirements.txt
```

### 测试数据库配置

默认情况下，测试会使用以下配置：

- PostgreSQL: `localhost:5432/auth_test` (用户名: postgres, 密码: postgres)
- Redis: `localhost:6379` (数据库: 1)

可以通过环境变量自定义：

```bash
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_NAME=auth_test
export TEST_DB_USER=postgres
export TEST_DB_PASSWORD=postgres

export TEST_REDIS_HOST=localhost
export TEST_REDIS_PORT=6379
export TEST_REDIS_DB=1
```

## 测试执行

### 运行所有测试

```bash
# 运行所有测试
python -m pytest

# 运行并显示覆盖率报告
python -m pytest --cov=internal --cov-report=term
```

### 运行特定测试

```bash
# 运行安全模块测试
python -m pytest test/unit/security

# 运行服务层测试
python -m pytest test/unit/service

# 运行仓储层测试
python -m pytest test/unit/repository

# 运行集成测试
python -m pytest test/integration
```

### 生成HTML覆盖率报告

```bash
python -m pytest --cov=internal --cov-report=html
# 报告将生成在htmlcov/目录
```

## 已知问题和解决方案

1. **aioredis兼容性问题**
   - **问题**: aioredis模块中的TimeoutError类与Python内置的TimeoutError类冲突
   - **解决方案**: 使用redis库代替aioredis，并重写异步方法为同步方法

2. **缺少模型定义**
   - **问题**: AuditActionEnum等枚举类型缺失
   - **解决方案**: 在model/user.py中添加必要的枚举类型定义

## 改进建议

1. **提高测试覆盖率**
   - 完成所有单元测试
   - 专注于低覆盖率的模块（仓储层）

2. **模拟外部依赖**
   - 为数据库和Redis完善更好的模拟机制
   - 避免在测试中使用真实的外部服务

3. **改进测试数据管理**
   - 创建更丰富的测试数据生成器
   - 使用工厂模式创建测试数据

4. **集成CI/CD测试**
   - 设置GitHub Actions自动运行测试
   - 添加测试覆盖率阈值检查

5. **Python 3.13兼容性**
   - 将所有使用datetime.utcnow()的代码更新为datetime.now(datetime.UTC)
   - 替换所有不兼容的库

6. **测试性能优化**
   - 使用SQLite内存数据库加速测试
   - 优化慢测试

## 下一步工作

1. 完成用户仓储层的单元测试
2. 完成令牌仓储层的单元测试
3. 完成审计日志仓储层的单元测试
4. 解决AuditActionEnum缺失问题
5. 增加端到端API测试
6. 提高整体测试覆盖率至85%以上 