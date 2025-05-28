# Python版本统一管理

## 概述

索克生活项目已将所有微服务的Python版本统一为 **Python 3.13.3**，以确保开发环境的一致性和最新特性的支持。

## 版本要求

- **Python版本**: 3.13.3
- **最低要求**: Python >= 3.13.3
- **推荐版本**: Python 3.13.3

## 统一更新内容

### 1. 项目配置文件

#### pyproject.toml
```toml
[project]
requires-python = ">=3.13.3"
classifiers = [
    "Programming Language :: Python :: 3.13",
]

[tool.black]
target-version = ['py313']

[tool.mypy]
python_version = "3.13"
```

#### Dockerfile
```dockerfile
FROM python:3.13.3-slim
```

### 2. CI/CD配置

#### GitHub Actions
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: "3.13.3"
```

#### GitLab CI
```yaml
image: python:3.13.3-slim
```

### 3. 开发环境

#### 虚拟环境创建
```bash
# 使用pyenv管理Python版本
pyenv install 3.13.3
pyenv local 3.13.3

# 创建虚拟环境
python -m venv venv_py313
source venv_py313/bin/activate  # Linux/macOS
# 或
venv_py313\Scripts\activate  # Windows
```

#### 依赖安装
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 微服务列表

以下微服务已统一更新为Python 3.13.3：

### 核心服务
- **API网关** (`services/api-gateway`)
- **认证服务** (`services/auth-service`)
- **用户服务** (`services/user-service`)
- **消息总线** (`services/message-bus`)
- **集成服务** (`services/integration-service`)

### 智能体服务
- **小艾服务** (`services/agent-services/xiaoai-service`)
- **小克服务** (`services/agent-services/xiaoke-service`)
- **老克服务** (`services/agent-services/laoke-service`)
- **索儿服务** (`services/agent-services/soer-service`)

### 业务服务
- **健康数据服务** (`services/health-data-service`)
- **医学知识服务** (`services/med-knowledge`)
- **RAG服务** (`services/rag-service`)
- **区块链服务** (`services/blockchain-service`)
- **医疗资源服务** (`services/medical-resource-service`)
- **索克评测服务** (`services/suoke-bench-service`)
- **玉米迷宫服务** (`services/corn-maze-service`)
- **无障碍服务** (`services/accessibility-service`)

### 诊断服务
- **问诊服务** (`services/diagnostic-services/inquiry-service`)
- **听诊服务** (`services/diagnostic-services/listen-service`)
- **望诊服务** (`services/diagnostic-services/look-service`)
- **触诊服务** (`services/diagnostic-services/palpation-service`)

## Python 3.13.3 新特性

### 性能改进
- **更快的启动时间**: 解释器启动速度提升
- **内存优化**: 更高效的内存管理
- **GIL优化**: 多线程性能改进

### 语言特性
- **改进的错误消息**: 更清晰的错误提示
- **类型提示增强**: 更强大的类型系统
- **模式匹配优化**: match语句性能提升

### 标准库更新
- **新增模块**: 新的标准库功能
- **API改进**: 现有模块的API增强
- **安全性提升**: 更好的安全特性

## 开发环境配置

### 1. 安装Python 3.13.3

#### macOS (使用Homebrew)
```bash
brew install python@3.13
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev
```

#### CentOS/RHEL
```bash
sudo dnf install python3.13 python3.13-venv python3.13-devel
```

#### Windows
从 [Python官网](https://www.python.org/downloads/) 下载安装包

### 2. 验证安装
```bash
python --version  # 应显示 Python 3.13.3
python -c "import sys; print(sys.version_info)"
```

### 3. 项目环境设置
```bash
# 克隆项目
git clone <repository-url>
cd suoke_life

# 创建虚拟环境
python -m venv venv_py313
source venv_py313/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 验证环境
python -c "import sys; print(f'Python {sys.version}')"
```

## 部署配置

### Docker部署
所有Dockerfile已更新为使用Python 3.13.3基础镜像：
```dockerfile
FROM python:3.13.3-slim
```

### Kubernetes部署
确保容器镜像使用正确的Python版本：
```yaml
spec:
  containers:
  - name: service-name
    image: your-registry/service-name:python3.13.3
```

## 测试验证

### 1. 单元测试
```bash
# 运行所有测试
python -m pytest

# 运行特定服务测试
cd services/xiaoai-service
python -m pytest tests/
```

### 2. 集成测试
```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
python -m pytest tests/integration/
```

### 3. 性能测试
```bash
# 运行性能基准测试
python -m pytest tests/performance/ -v
```

## 兼容性说明

### 向后兼容性
- Python 3.13.3 与 3.12.x 基本兼容
- 大部分第三方库已支持 Python 3.13
- 现有代码无需修改即可运行

### 依赖更新
- 所有依赖包已验证与 Python 3.13.3 兼容
- 部分包可能需要更新到最新版本
- 详见各服务的 `requirements.txt`

## 故障排除

### 常见问题

#### 1. 虚拟环境创建失败
```bash
# 确保安装了venv模块
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

#### 2. 依赖安装失败
```bash
# 更新pip和setuptools
pip install --upgrade pip setuptools wheel

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

#### 3. 导入错误
```bash
# 检查Python路径
python -c "import sys; print('\n'.join(sys.path))"

# 重新安装问题包
pip uninstall <package-name>
pip install <package-name>
```

### 性能问题
- 如遇到性能问题，检查是否启用了优化选项
- 确保使用了正确的Python解释器
- 监控内存和CPU使用情况

## 维护指南

### 版本更新流程
1. **评估新版本**: 检查Python新版本的特性和兼容性
2. **测试环境验证**: 在测试环境中验证新版本
3. **依赖兼容性检查**: 确保所有依赖包支持新版本
4. **批量更新**: 使用自动化脚本更新所有配置文件
5. **全面测试**: 运行完整的测试套件
6. **分阶段部署**: 逐步部署到生产环境

### 自动化更新
使用提供的更新脚本：
```bash
python scripts/update_python_version.py
```

### 监控和告警
- 监控各服务的Python版本一致性
- 设置告警检测版本不匹配
- 定期检查安全更新

## 相关文档

- [Python 3.13 官方文档](https://docs.python.org/3.13/)
- [Python 3.13 新特性](https://docs.python.org/3.13/whatsnew/3.13.html)
- [项目依赖管理](./DEPENDENCY_MANAGEMENT.md)
- [开发环境配置](./DEVELOPMENT_SETUP.md)
- [部署指南](./DEPLOYMENT_GUIDE.md)

## 更新历史

| 日期 | 版本 | 更新内容 | 更新者 |
|------|------|----------|--------|
| 2025-05-27 | 3.13.3 | 统一所有微服务Python版本 | 系统管理员 |

---

**注意**: 本文档会随着Python版本更新而持续维护，请定期查看最新版本。 