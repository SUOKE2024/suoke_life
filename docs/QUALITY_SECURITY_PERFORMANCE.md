# 索克生活项目 - 代码质量、安全扫描与性能测试指南

## 概述

本文档详细介绍了索克生活健康管理平台的代码质量检查、安全扫描和性能测试的完整解决方案。我们采用现代化的工具链和最佳实践，确保代码质量、系统安全和性能表现达到生产级别标准。

## 🎯 核心目标

- **代码质量**: 通过静态分析、格式化检查和测试覆盖率确保代码质量
- **安全保障**: 通过多层次安全扫描识别和修复潜在安全漏洞
- **性能优化**: 通过负载测试和性能监控确保系统性能表现

## 📊 工具链架构

### 代码质量检查工具

| 工具 | 用途 | 语言 | 配置文件 |
|------|------|------|----------|
| **SonarQube** | 代码质量综合分析 | Python/JS | `sonar-project.properties` |
| **Black** | Python代码格式化 | Python | `pyproject.toml` |
| **isort** | Python导入排序 | Python | `pyproject.toml` |
| **Flake8** | Python代码风格检查 | Python | `.flake8` |
| **Pylint** | Python静态分析 | Python | `.pylintrc` |
| **MyPy** | Python类型检查 | Python | `mypy.ini` |
| **ESLint** | JavaScript/TypeScript检查 | JS/TS | `.eslintrc.json` |
| **Prettier** | JavaScript/TypeScript格式化 | JS/TS | `.prettierrc.js` |

### 安全扫描工具

| 工具 | 用途 | 扫描范围 | 配置文件 |
|------|------|----------|----------|
| **Snyk** | 依赖漏洞和代码安全扫描 | 全栈 | `.snyk` |
| **Safety** | Python依赖安全检查 | Python | - |
| **Bandit** | Python代码安全分析 | Python | - |
| **GitLeaks** | 敏感信息泄露检测 | 全栈 | `.gitleaks.toml` |

### 性能测试工具

| 工具 | 用途 | 测试类型 | 配置文件 |
|------|------|----------|----------|
| **K6** | 负载和性能测试 | HTTP API | `k6/performance-tests/` |
| **Pytest** | 单元测试和集成测试 | Python | `pytest.ini` |
| **Jest** | JavaScript单元测试 | JS/TS | `jest.config.js` |

## 🔧 环境配置

### 1. SonarQube部署

#### Kubernetes部署

```bash
# 部署SonarQube到Kubernetes集群
kubectl apply -f k8s/sonarqube/sonarqube-deployment.yaml

# 检查部署状态
kubectl get pods -n sonarqube
kubectl get services -n sonarqube

# 访问SonarQube Web界面
kubectl port-forward -n sonarqube svc/sonarqube 9000:9000
```

#### 本地Docker部署

```bash
# 使用Docker Compose启动SonarQube
docker-compose -f docker-compose.additional-services.yml up -d sonarqube

# 访问 http://localhost:9000
# 默认登录: admin/admin
```

### 2. 开发环境设置

```bash
# 安装Python依赖
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 安装开发工具
uv pip install pytest pytest-cov pylint flake8 mypy black isort bandit safety

# 安装Node.js依赖
npm install

# 安装K6 (macOS)
brew install k6

# 安装K6 (Ubuntu/Debian)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## 🚀 使用指南

### 代码质量检查

#### 本地运行

```bash
# 运行完整的代码质量检查
./scripts/run-quality-checks.sh

# 跳过代码格式化
./scripts/run-quality-checks.sh --no-format

# 查看帮助信息
./scripts/run-quality-checks.sh --help
```

#### 单独运行各工具

```bash
# Python代码格式化
source .venv/bin/activate
black services/ tests/
isort services/ tests/

# Python静态分析
flake8 services/ tests/
pylint services/
mypy services/

# JavaScript/TypeScript检查
npm run lint
npm run type-check

# 运行测试
pytest tests/ --cov=services
npm test
```

#### SonarQube分析

```bash
# 使用SonarQube Scanner
docker run --rm \
  -e SONAR_HOST_URL="https://sonarqube.suoke.life" \
  -e SONAR_LOGIN="your-token" \
  -v "$PWD:/usr/src" \
  sonarsource/sonar-scanner-cli:latest
```

### 安全扫描

#### 本地安全检查

```bash
# 安装Snyk CLI
npm install -g snyk
snyk auth your-token

# Python依赖安全扫描
safety check
bandit -r services/

# Snyk扫描
snyk test --file=requirements.txt
snyk test --file=package.json
snyk code test
snyk container test your-image:tag
snyk iac test k8s/

# 敏感信息检测
gitleaks detect --source . --verbose
```

#### CI/CD集成

安全扫描已集成到GitHub Actions工作流中，每次提交和PR都会自动运行：

```yaml
# .github/workflows/quality-security-performance.yml
- name: Snyk Python依赖扫描
  run: |
    snyk test --file=requirements.txt \
      --json --json-file-output=snyk-python-report.json \
      --severity-threshold=medium
```

### 性能测试

#### 本地性能测试

```bash
# 运行所有性能测试
./scripts/run-performance-tests.sh all

# 运行特定测试
./scripts/run-performance-tests.sh auth
./scripts/run-performance-tests.sh health-data
./scripts/run-performance-tests.sh agent-spike

# 自定义负载测试
./scripts/run-performance-tests.sh custom --users 100 --duration 10m

# 查看帮助信息
./scripts/run-performance-tests.sh --help
```

#### K6测试场景

1. **认证服务负载测试**
   - 测试用户注册、登录、令牌刷新等流程
   - 目标: 95%请求响应时间 < 300ms

2. **健康数据服务压力测试**
   - 测试健康数据上传和查询性能
   - 目标: 95%请求响应时间 < 800ms

3. **智能体协同峰值测试**
   - 测试智能体协同诊断的峰值处理能力
   - 目标: 95%请求响应时间 < 1000ms

4. **中医诊断容量测试**
   - 测试五诊合参诊断的容量限制
   - 目标: 95%请求响应时间 < 600ms

5. **系统稳定性测试**
   - 长时间运行测试系统稳定性
   - 目标: 错误率 < 0.1%

## 📈 质量门禁标准

### 代码质量门禁

| 指标 | 阈值 | 工具 |
|------|------|------|
| 测试覆盖率 | ≥ 80% | pytest-cov |
| 代码重复率 | ≤ 3% | SonarQube |
| 代码复杂度 | ≤ 10 | SonarQube |
| 技术债务 | ≤ 5% | SonarQube |
| 代码异味 | 0个阻断级别 | SonarQube |

### 安全门禁标准

| 类型 | 阈值 | 说明 |
|------|------|------|
| 高危漏洞 | 0个 | 必须修复所有高危漏洞 |
| 中危漏洞 | ≤ 2个 | 中危漏洞需要评估和计划修复 |
| 低危漏洞 | ≤ 10个 | 低危漏洞可以延后修复 |
| 代码安全问题 | ≤ 5个 | Bandit检测的代码安全问题 |
| 容器漏洞 | ≤ 1个高危 | 容器镜像安全扫描 |

### 性能门禁标准

| 服务 | 95%响应时间 | 错误率 | 吞吐量 |
|------|-------------|--------|--------|
| 认证服务 | < 300ms | < 0.1% | > 1000 RPS |
| 健康数据服务 | < 800ms | < 0.1% | > 500 RPS |
| 智能体协同 | < 1000ms | < 0.1% | > 100 RPS |
| 中医诊断 | < 600ms | < 0.1% | > 200 RPS |

## 🔄 CI/CD集成

### GitHub Actions工作流

我们的CI/CD流水线包含三个主要阶段：

1. **代码质量检查** (`code-quality`)
   - 代码格式化检查
   - 静态分析
   - 单元测试和覆盖率
   - SonarQube扫描

2. **安全扫描** (`security-scan`)
   - 依赖漏洞扫描
   - 代码安全分析
   - 容器镜像扫描
   - 基础设施安全检查

3. **性能测试** (`performance-test`)
   - 负载测试
   - 压力测试
   - 稳定性测试
   - 性能报告生成

### 触发条件

- **Push到main/develop分支**: 运行完整测试套件
- **Pull Request**: 运行完整测试套件
- **定时任务**: 每天凌晨2点运行完整测试
- **手动触发**: 支持选择性运行特定测试类型

### 环境变量配置

在GitHub仓库设置中配置以下Secrets：

```bash
# SonarQube
SONAR_TOKEN=your-sonarqube-token

# Snyk
SNYK_TOKEN=your-snyk-token

# 通知
SLACK_WEBHOOK_URL=your-slack-webhook
EMAIL_USERNAME=your-email
EMAIL_PASSWORD=your-email-password
NOTIFICATION_EMAIL=team@suoke.life
```

## 📊 报告和监控

### 质量报告

1. **SonarQube仪表板**
   - 访问: https://sonarqube.suoke.life
   - 实时代码质量指标
   - 历史趋势分析
   - 问题跟踪和修复建议

2. **本地质量报告**
   - HTML报告: `reports/quality-report.html`
   - 覆盖率报告: `reports/htmlcov/index.html`
   - 静态分析报告: `reports/`目录下各工具报告

### 安全报告

1. **Snyk仪表板**
   - 在线漏洞管理
   - 修复建议和PR自动创建
   - 许可证合规检查

2. **本地安全报告**
   - 安全摘要: `security-summary.json`
   - 详细报告: 各工具生成的JSON报告

### 性能报告

1. **K6性能报告**
   - HTML报告: `performance-results/performance-report.html`
   - CSV数据: `performance-results/performance-summary.csv`
   - 详细指标: JSON格式的测试结果

2. **性能监控集成**
   - Grafana仪表板
   - Prometheus指标收集
   - 告警和通知

## 🛠️ 故障排除

### 常见问题

#### SonarQube相关

**问题**: SonarQube扫描失败
```bash
# 检查SonarQube服务状态
kubectl get pods -n sonarqube

# 查看日志
kubectl logs -n sonarqube deployment/sonarqube

# 重启服务
kubectl rollout restart deployment/sonarqube -n sonarqube
```

**问题**: 质量门禁失败
- 检查SonarQube项目配置
- 调整质量门禁阈值
- 修复代码质量问题

#### 安全扫描相关

**问题**: Snyk认证失败
```bash
# 重新认证
snyk auth your-new-token

# 检查认证状态
snyk config get api
```

**问题**: 误报安全问题
- 在`.snyk`文件中添加忽略规则
- 设置合理的过期时间
- 添加详细的忽略原因

#### 性能测试相关

**问题**: K6测试失败
```bash
# 检查服务状态
curl -f http://localhost:8001/health

# 查看K6详细输出
k6 run --verbose your-test.js

# 检查资源限制
top
free -h
```

**问题**: 性能阈值不合理
- 根据实际业务需求调整阈值
- 考虑硬件资源限制
- 分析历史性能数据

### 调试技巧

1. **启用详细日志**
   ```bash
   # Python调试
   export PYTHONPATH=.
   export LOG_LEVEL=DEBUG
   
   # K6调试
   k6 run --verbose --http-debug=full your-test.js
   ```

2. **本地环境测试**
   ```bash
   # 启动本地服务
   docker-compose up -d
   
   # 运行单个测试
   ./scripts/run-quality-checks.sh --no-format
   ./scripts/run-performance-tests.sh auth
   ```

3. **CI/CD调试**
   - 查看GitHub Actions日志
   - 下载构建产物
   - 本地复现CI环境

## 📚 最佳实践

### 代码质量

1. **提交前检查**
   - 使用pre-commit hooks
   - 运行本地质量检查脚本
   - 确保测试通过

2. **代码审查**
   - 关注SonarQube报告
   - 检查测试覆盖率
   - 验证代码风格一致性

3. **持续改进**
   - 定期审查质量门禁标准
   - 更新工具和配置
   - 团队培训和知识分享

### 安全实践

1. **安全开发**
   - 遵循安全编码规范
   - 定期更新依赖
   - 使用安全的配置

2. **漏洞管理**
   - 及时修复高危漏洞
   - 建立漏洞响应流程
   - 定期安全评估

3. **合规要求**
   - 遵循HIPAA、GDPR等法规
   - 实施数据加密
   - 建立审计日志

### 性能优化

1. **性能测试策略**
   - 早期性能测试
   - 持续性能监控
   - 性能回归检测

2. **优化方法**
   - 数据库查询优化
   - 缓存策略实施
   - 异步处理优化

3. **监控告警**
   - 设置性能基线
   - 建立告警机制
   - 性能趋势分析

## 🔗 相关资源

### 官方文档

- [SonarQube文档](https://docs.sonarqube.org/)
- [Snyk文档](https://docs.snyk.io/)
- [K6文档](https://k6.io/docs/)
- [GitHub Actions文档](https://docs.github.com/en/actions)

### 工具配置

- [SonarQube Python插件](https://docs.sonarqube.org/latest/analysis/languages/python/)
- [ESLint配置指南](https://eslint.org/docs/user-guide/configuring/)
- [K6测试脚本示例](https://k6.io/docs/examples/)

### 社区资源

- [Python代码质量工具对比](https://realpython.com/python-code-quality/)
- [JavaScript安全最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [性能测试最佳实践](https://k6.io/docs/testing-guides/performance-testing/)

---

## 📞 支持和反馈

如有问题或建议，请通过以下方式联系：

- **技术支持**: tech-support@suoke.life
- **GitHub Issues**: [项目Issues页面](https://github.com/suoke-life/suoke-life/issues)
- **团队Slack**: #suoke-life-dev

---

*本文档持续更新，最后更新时间: 2024年1月* 