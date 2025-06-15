# 索克生活认证服务测试指南

本文档介绍了如何运行索克生活（Suoke Life）认证服务的各种测试。

## 目录结构

```
test/
  ├── unit/                 # 单元测试
  │   ├── security/         # 安全模块测试
  │   ├── repository/       # 仓储模块测试
  │   ├── service/          # 服务模块测试
  │   └── delivery/         # 交付模块测试
  ├── integration/          # 集成测试
  │   ├── repository/       # 仓储模块集成测试
  │   ├── service/          # 服务模块集成测试
  │   ├── delivery/         # 交付模块集成测试
  │   ├── setup.py          # 集成测试环境设置
  │   └── cleanup.py        # 集成测试环境清理
  └── results/              # 测试结果和覆盖率报告
      ├── jwt_coverage/     # JWT模块覆盖率报告
      ├── repository_coverage/ # 仓储模块覆盖率报告
      ├── integration/      # 集成测试覆盖率报告
      └── all_coverage/     # 所有单元测试覆盖率报告
```

## 运行测试

我们提供了多个脚本来运行不同类型的测试。

### 环境准备

在运行测试前，确保已安装所有依赖：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 运行所有单元测试

使用以下命令运行所有单元测试并生成覆盖率报告：

```bash
./scripts/run_all_tests.sh
```

此脚本将会：
1. 运行安全模块测试（JWT等）
2. 运行仓储模块测试（用户、令牌仓储等）
3. 如果存在则运行服务模块和交付模块测试
4. 生成整体覆盖率报告

### 运行安全模块测试

只运行安全模块的测试：

```bash
./scripts/run_security_tests.sh
```

### 运行仓储模块测试

只运行仓储模块的测试：

```bash
./scripts/run_repository_tests.sh
```

### 运行集成测试

集成测试需要外部依赖如PostgreSQL和Redis。使用以下命令运行：

```bash
./scripts/run_integration_tests.sh
```

**注意：** 运行集成测试前，请确保：
1. PostgreSQL 服务已启动
2. Redis 服务已启动
3. 环境变量已正确设置（脚本会自动加载 `setup_test_env.sh` 中的环境变量）

如果没有这些服务，脚本会提供使用Docker启动这些服务的命令。

## 测试覆盖率

测试完成后，覆盖率报告将生成在 `test/results/` 目录中。您可以使用浏览器打开HTML报告查看详细覆盖率信息：

```bash
open test/results/all_coverage/index.html
```

## 当前覆盖率统计

| 模块 | 覆盖率 |
|------|--------|
| 安全模块 (JWT) | 87% |
| 仓储模块 (总体) | 81% |
| - 令牌仓储 | 95% |
| - OAuth仓储 | 93% |
| - 审计仓储 | 88% |
| - 用户仓储 | 57% |

## 添加新测试

添加新测试时，请遵循以下指南：

1. 将测试文件放在对应模块的目录下
2. 文件名以 `test_` 开头
3. 测试类名以 `Test` 开头
4. 测试方法名以 `test_` 开头
5. 使用 pytest fixtures 进行依赖注入
6. 为异步测试添加 `@pytest.mark.asyncio` 装饰器

示例：

```python
import pytest

@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_user_success(self, async_db_session, mock_redis):
        # 测试代码
        pass
```

## 问题排查

如果测试失败，请检查：

1. 所有依赖是否已安装
2. 环境变量是否正确设置
3. 外部服务（数据库、Redis）是否正常运行
4. 查看具体的错误消息和堆栈跟踪 