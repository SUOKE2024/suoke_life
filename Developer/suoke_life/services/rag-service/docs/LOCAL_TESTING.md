# 本地测试与自动部署指南

本文档介绍如何在本地进行测试，并在测试通过后自动触发CI/CD流程。

## 脚本概述

我们提供两个主要脚本来支持本地测试和自动部署流程：

1. **run_local_tests.sh** - 执行本地代码检查、单元测试和Docker构建
2. **test_and_deploy.sh** - 运行本地测试，并在测试通过后提交代码并触发CI/CD

## 本地测试流程

本地测试脚本会执行以下检查：

- 代码格式检查 (Black)
- 类型检查 (MyPy)
- 代码风格检查 (Pylint)
- 单元测试 (Pytest)
- Docker镜像构建测试
- 功能验证测试 (可选)

### 执行本地测试

只想执行测试而不提交代码时，使用以下命令：

```bash
cd services/rag-service
./scripts/run_local_tests.sh
```

脚本会详细报告每个测试阶段的结果，并在测试失败时提供修复建议。

## 测试并自动部署流程

当您想要在本地测试通过后自动提交代码并触发CI/CD流程时，可以使用测试并部署脚本。

### 使用方法

```bash
cd services/rag-service
./scripts/test_and_deploy.sh <分支名> "<提交消息>" [Y/N]
```

参数说明：
- `<分支名>` - 要提交代码的分支名称，例如 `feature/new-feature` 或 `release/1.0.0`
- `"<提交消息>"` - Git提交信息，必须用引号包围
- `[Y/N]` - 可选参数，是否自动推送到远程仓库，默认为N

### 示例

#### 开发新功能

```bash
# 执行测试并将代码提交到feature分支，但不推送
./scripts/test_and_deploy.sh feature/optimize-retrieval "优化检索性能"

# 执行测试并将代码提交到feature分支，并自动推送触发CI/CD
./scripts/test_and_deploy.sh feature/optimize-retrieval "优化检索性能" Y
```

#### 准备发布版本

```bash
# 执行测试并将代码提交到release分支，并自动推送触发全流程部署
./scripts/test_and_deploy.sh release/1.2.0 "准备1.2.0版本发布" Y
```

## 分支策略与CI/CD触发规则

不同的分支会触发不同的CI/CD流程：

| 分支类型 | CI/CD流程 | 自动部署环境 |
|---------|----------|------------|
| `feature/*` | 代码检查、测试、安全扫描 | 无自动部署 |
| `main` | 完整CI/CD流程 | 开发环境 |
| `release/*` | 完整CI/CD流程 | 预发布环境和生产环境 |

## 故障排查

### 常见问题

1. **测试脚本无法执行**
   ```bash
   chmod +x scripts/run_local_tests.sh scripts/test_and_deploy.sh
   ```

2. **缺少依赖**
   ```bash
   pip install -r requirements.txt
   pip install black mypy pylint pytest pytest-cov locust
   ```

3. **Docker构建失败**
   - 确保Docker守护进程正在运行
   - 检查Dockerfile语法
   - 查看空间是否足够

4. **测试失败**
   - 按照错误信息修复代码问题
   - 运行特定测试: `python -m pytest tests/test_specific.py`

## 最佳实践

1. **经常运行本地测试**
   - 每天开始工作前运行一次测试
   - 完成重要功能后运行测试
   - 合并其他开发者代码后运行测试

2. **小步提交**
   - 保持提交内容小而集中
   - 每个提交解决一个明确的问题
   - 写清晰的提交信息

3. **分支管理**
   - 严格遵循分支命名规范
   - feature分支完成后及时清理
   - 不要直接在main或release分支上开发

4. **CI/CD监控**
   - 推送代码后立即检查CI/CD流程状态
   - 出现失败立即修复，避免影响团队其他成员 