# 索克生活 - 测试与监控指南

本文档提供了索克生活（SUOKE.LIFE）微服务架构中的测试和监控指南，帮助开发者和运维人员了解如何进行有效的测试和系统监控。

## 目录

1. [测试类型与工具](#1-测试类型与工具)
2. [如何运行测试](#2-如何运行测试)
3. [持续集成与部署](#3-持续集成与部署)
4. [性能监控](#4-性能监控)
5. [日志管理](#5-日志管理)
6. [报警机制](#6-报警机制)
7. [故障排除](#7-故障排除)

## 1. 测试类型与工具

索克生活项目采用以下测试类型和工具：

### 1.1 单元测试

- **范围**：测试单个函数和方法的功能
- **工具**：Go 标准测试库，testify 库
- **位置**：各服务 `internal` 目录中的 `*_test.go` 文件
- **命令**：`./tests/run_unit_tests.sh`

### 1.2 集成测试

- **范围**：测试多个组件的交互
- **工具**：自定义 Bash 脚本和 curl 命令
- **位置**：`./tests/integration/*.sh`
- **命令**：`./tests/run_integration_tests.sh`

### 1.3 性能测试

- **范围**：测试 API 性能和响应时间
- **工具**：Apache Benchmark (ab)
- **位置**：`./tests/performance_benchmark.sh`
- **命令**：`./tests/performance_benchmark.sh -e /endpoint -c 10 -n 100`

### 1.4 API 测试

- **范围**：测试 API 功能和响应
- **工具**：自定义 Bash 脚本
- **位置**：`./tests/api_tester.sh`
- **命令**：`./tests/api_tester.sh <command> [args]`

## 2. 如何运行测试

### 2.1 统一测试命令

我们提供了一个统一的测试命令脚本，可以运行所有类型的测试：

```bash
# 运行所有测试
./tests/run_tests.sh

# 运行特定类型的测试
./tests/run_tests.sh unit
./tests/run_tests.sh integration
./tests/run_tests.sh performance
./tests/run_tests.sh api

# 带参数运行测试
./tests/run_tests.sh performance -c 50 -n 1000 -e '/users'
./tests/run_tests.sh api auth:login testuser password
```

### 2.2 单元测试

单元测试可以针对特定服务或全部服务运行：

```bash
# 运行所有服务的单元测试
./tests/run_unit_tests.sh

# 运行特定服务的单元测试
./tests/run_unit_tests.sh --service auth-service

# 生成测试覆盖率报告
./tests/run_unit_tests.sh --coverage
```

### 2.3 集成测试

集成测试会启动所有服务并执行端到端测试：

```bash
# 运行所有集成测试
./tests/run_integration_tests.sh

# 保持服务运行（测试完成后不停止服务）
./tests/run_integration_tests.sh --no-stop

# 指定自定义 Docker Compose 文件
./tests/run_integration_tests.sh --compose-file ./custom-compose.yml
```

### 2.4 性能测试

性能测试可以用于测试 API 的性能和负载能力：

```bash
# 测试健康检查端点
./tests/performance_benchmark.sh

# 测试用户登录 API
./tests/performance_benchmark.sh -m POST -e "/auth/login" -d '{"username":"test","password":"test123"}' -c 20 -n 200

# 保存结果到自定义目录
./tests/performance_benchmark.sh -o ./my_results
```

### 2.5 API 测试

API 测试工具提供了一个简单的界面来测试 API 端点：

```bash
# 显示帮助信息
./tests/api_tester.sh help

# 注册新用户
./tests/api_tester.sh auth:register testuser user@example.com password

# 登录（会自动保存令牌）
./tests/api_tester.sh auth:login testuser password

# 获取用户信息
./tests/api_tester.sh users:get <user_id>

# 切换环境
./tests/api_tester.sh -e prod health
```

## 3. 持续集成与部署

本项目使用 GitHub Actions 进行持续集成和部署。CI/CD 流程包括：

1. 代码质量检查（使用 golangci-lint）
2. 单元测试
3. 构建服务
4. 创建 Docker 镜像
5. 运行集成测试
6. 部署到开发环境（当合并到 `dev` 分支）
7. 部署到生产环境（当合并到 `main` 分支）

详细配置可以查看 `.github/workflows/ci.yml` 文件。

## 4. 性能监控

### 4.1 指标收集

我们使用 Prometheus 收集各服务的性能指标。每个服务都暴露以下指标：

- HTTP 请求总数
- 请求持续时间（直方图）
- 响应大小（直方图） 
- 错误计数
- 活跃请求数
- 数据库操作持续时间

指标端点：`/metrics`（由各服务提供）

### 4.2 监控面板

我们使用 Grafana 提供可视化监控面板，包括：

- 服务健康状态面板
- API 性能面板
- 资源使用情况面板
- 错误率面板

Grafana 登录地址：http://monitoring.suoke.life:3000

### 4.3 健康检查

每个服务都提供健康检查端点：

- API 网关: http://118.31.223.213/health
- 用户服务: http://118.31.223.213/api/users/health
- 认证服务: http://118.31.223.213/api/auth/health

## 5. 日志管理

### 5.1 日志格式

所有服务都使用结构化 JSON 日志格式，包含以下字段：

- timestamp: 日志时间
- level: 日志级别（debug, info, warn, error, fatal）
- service: 服务名称
- msg: 日志消息
- request_id: 请求 ID（用于跟踪请求）
- additional_fields: 根据具体日志类型添加的其他字段

### 5.2 日志聚合

日志聚合使用 ELK 栈（Elasticsearch, Logstash, Kibana）：

- 所有服务日志会写入 `/var/log/suoke/<service-name>/`
- Filebeat 收集日志并发送到 Logstash
- Logstash 解析并发送到 Elasticsearch
- Kibana 提供日志可视化和搜索

Kibana 地址：http://logs.suoke.life:5601

### 5.3 日志级别

可以通过环境变量或配置文件调整日志级别：

```
LOG_LEVEL=debug|info|warn|error
```

## 6. 报警机制

### 6.1 报警规则

系统配置了以下报警规则：

- 服务不可用（健康检查失败）
- 高错误率（>1%）
- 高响应时间（P95 > 500ms）
- 高 CPU 使用率（>80%）
- 高内存使用率（>80%）
- 磁盘空间不足（<10%）

### 6.2 报警渠道

报警会通过以下渠道发送：

- 电子邮件（ops@suoke.life）
- 钉钉（运维群）
- 短信（紧急情况）

## 7. 故障排除

### 7.1 常见问题

1. **服务启动失败**
   - 检查日志：`docker logs <container_id>`
   - 检查配置文件格式是否正确
   - 检查端口是否被占用

2. **API 返回 500 错误**
   - 检查服务日志
   - 检查数据库连接
   - 验证请求参数和格式

3. **性能问题**
   - 运行性能测试脚本
   - 检查数据库查询性能
   - 检查网络延迟

### 7.2 服务重启

如需重启服务，可以使用以下命令：

```bash
# 重启单个服务
docker-compose restart <service-name>

# 重启所有服务
docker-compose restart

# 完全重建服务
docker-compose down && docker-compose up -d
```

### 7.3 备份与恢复

数据库自动备份设置：

- 每日自动备份：凌晨 2 点
- 备份保留期：30 天
- 备份位置：/var/backups/suoke/ 和 远程 S3 存储

恢复数据库：

```bash
# 恢复 MySQL 数据
./scripts/restore_db.sh <backup_date>
```

---

如有任何问题，请联系技术团队：dev@suoke.life 