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

| 模块              | 覆盖率  | 备注                                  |
|------------------|--------|--------------------------------------|
| 安全模块           | 92%    | JWT(87%), MFA(93%), 密码(98%)         |
| 服务层             | 8%     | auth_service(10%), oauth_service(6%) |
| 仓储层             | 88%    | audit_repository(88%), token_repository(11%), user_repository(13%) |
| 整体覆盖率         | 22%    | 需要继续改进                           |

## 测试环境配置

### 依赖安装

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-freezegun pytest-env

# 安装服务依赖
pip install fastapi pydantic sqlalchemy asyncpg redis passlib python-jose[cryptography] pyotp qrcode pillow
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
   - **解决方案**: 使用redis库代替aioredis，已在conftest.py中实现

2. **模块导入问题**
   - **问题**: 缺少internal.db.session模块
   - **解决方案**: 已创建internal/db/session.py模块

3. **Python 3.13兼容性警告**
   - **问题**: datetime.utcnow()在Python 3.13中已弃用
   - **解决方案**: 需要将所有实例替换为datetime.now(datetime.UTC)

## 改进建议

1. **提高测试覆盖率**
   - 添加token_repository的单元测试
   - 添加user_repository的单元测试
   - 改进服务层测试

2. **修复集成测试**
   - 解决cmd.server导入错误
   - 实现虚拟服务器启动以支持API测试

3. **改进测试数据管理**
   - 创建更丰富的测试数据生成器
   - 使用工厂模式创建测试数据

4. **集成CI/CD测试**
   - 设置GitHub Actions自动运行测试
   - 添加测试覆盖率阈值检查

5. **Python 3.13兼容性**
   - 将所有使用datetime.utcnow()的代码更新为datetime.now(datetime.UTC)
   - 替换所有不兼容的库

## 下一步工作

1. 完成token_repository的单元测试
2. 完成user_repository的单元测试
3. 修复服务层测试中的import错误
4. 为集成测试创建必要的模拟服务
5. 提高整体测试覆盖率至70%以上
6. 解决所有Python 3.13兼容性警告 