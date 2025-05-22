# Python 3.12 升级路线图

## 项目概述

索克生活(Suoke Life)项目目前使用多个Python版本(3.9/3.10/3.11)。本升级计划旨在将所有服务统一升级到Python 3.12，以便利用最新特性和性能改进。

## 已完成工作

1. ✅ 创建兼容性检查脚本 `scripts/check_python312_compatibility.py`
2. ✅ 创建Dockerfile更新脚本 `scripts/update_dockerfiles.py`  
3. ✅ 创建GitHub工作流更新脚本 `scripts/update_github_workflows.py`
4. ✅ 创建主协调脚本 `scripts/upgrade_python312.py`
5. ✅ 创建改进版兼容性检查脚本 `scripts/check_dependency_compatibility.py`
6. ✅ 创建测试验证脚本 `scripts/test_python312_compatibility.py`
7. ✅ 创建依赖修复脚本 `scripts/fix_python312_dependencies.py`
8. ✅ 创建手动依赖修复脚本 `scripts/manual_fixes_python312.py`
9. ✅ 创建升级监控脚本 `scripts/monitor_python312_upgrade.py`
10. ✅ 更新28个Dockerfile中的Python基础镜像为3.12
11. ✅ 更新4个GitHub工作流配置为Python 3.12
12. ✅ 自动修复16个服务的52个依赖项问题
13. ✅ 手动修复9个服务的20个依赖项问题

## 当前状态

通过依赖兼容性检测，已处理以下不兼容问题：

1. **依赖包版本不兼容**：已升级部分依赖包到支持Python 3.12的版本
   - numpy、scipy等科学计算库已升级到最新版本
   - torch、torchvision等深度学习框架已升级
   - sqlalchemy、asyncpg等数据库依赖已升级

2. **无法升级的依赖项**：对于某些尚无Python 3.12兼容版本的库，已在要求文件中添加注释标记
   - tensorflow-lite、tflite-runtime等依赖暂不支持Python 3.12
   - pysnark、zokrates等特定领域库需要后续单独处理

3. **格式错误的依赖项**：修复了包含注释的依赖项定义
   - 例如：`asyncpg>=0.27.0,<0.28.0  # PostgreSQL async client` → `asyncpg>=0.29.0,<1.0.0`

## 升级环境准备

1. **Python 3.12安装**
   ```bash
   # macOS (使用Homebrew)
   brew install python@3.12
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install software-properties-common
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt install python3.12 python3.12-venv python3.12-dev
   
   # CentOS/RHEL
   sudo dnf install python3.12
   ```

2. **虚拟环境设置**
   ```bash
   # 创建Python 3.12虚拟环境
   python3.12 -m venv py312-env
   
   # 激活虚拟环境
   source py312-env/bin/activate
   
   # 安装基本工具
   pip install --upgrade pip setuptools wheel
   ```

3. **容器环境准备**
   ```bash
   # 创建测试容器环境(Docker)
   docker pull python:3.12-slim
   ```

## 分阶段部署计划

根据服务依赖关系和重要性，我们将按照以下四个阶段进行部署：

### 阶段1: 基础服务(第1周)

**目标服务:**
- api-gateway
- auth-service
- message-bus

**执行计划:**
1. 在测试环境部署Python 3.12版本
2. 运行单元测试和集成测试
3. 监控服务性能和稳定性(48小时)
4. 确认无问题后部署到生产环境

**命令:**
```bash
# 部署测试环境
python3 scripts/deploy_python312.py --stage 1 --env test

# 运行测试
python3 scripts/test_python312_compatibility.py --services api-gateway auth-service message-bus

# 监控服务(运行48小时)
python3 scripts/monitor_python312_upgrade.py --stage 1 --duration 172800 --interval 300
```

### 阶段2: 核心业务服务(第2周)

**目标服务:**
- user-service
- health-data-service
- med-knowledge
- medical-service

**执行计划:**
1. 在测试环境部署Python 3.12版本
2. 运行单元测试和集成测试
3. 验证与阶段1服务的交互
4. 监控服务性能和稳定性(48小时)
5. 确认无问题后部署到生产环境

**命令:**
```bash
# 部署测试环境
python3 scripts/deploy_python312.py --stage 2 --env test

# 运行测试
python3 scripts/test_python312_compatibility.py --services user-service health-data-service med-knowledge medical-service

# 监控服务(运行48小时)
python3 scripts/monitor_python312_upgrade.py --stage 2 --duration 172800 --interval 300
```

### 阶段3: 智能体服务(第3周)

**目标服务:**
- rag-service
- agent-services/laoke-service
- agent-services/soer-service
- agent-services/xiaoai-service
- agent-services/xiaoke-service

**执行计划:**
1. 在测试环境部署Python 3.12版本
2. 运行单元测试和集成测试
3. 执行端到端测试验证智能体功能
4. 监控服务性能和稳定性(72小时)
5. 确认无问题后部署到生产环境

**命令:**
```bash
# 部署测试环境
python3 scripts/deploy_python312.py --stage 3 --env test

# 运行测试
python3 scripts/test_python312_compatibility.py --services rag-service agent-services/laoke-service agent-services/soer-service agent-services/xiaoai-service agent-services/xiaoke-service

# 监控服务(运行72小时)
python3 scripts/monitor_python312_upgrade.py --stage 3 --duration 259200 --interval 300
```

### 阶段4: 辅助服务(第4周)

**目标服务:**
- accessibility-service
- blockchain-service
- corn-maze-service
- suoke-bench-service
- diagnostic-services/*

**执行计划:**
1. 在测试环境部署Python 3.12版本
2. 运行单元测试和集成测试
3. 监控服务性能和稳定性(48小时)
4. 确认无问题后部署到生产环境

**命令:**
```bash
# 部署测试环境
python3 scripts/deploy_python312.py --stage 4 --env test

# 运行测试
python3 scripts/test_python312_compatibility.py --services accessibility-service blockchain-service corn-maze-service suoke-bench-service diagnostic-services/listen-service diagnostic-services/inquiry-service diagnostic-services/palpation-service diagnostic-services/look-service

# 监控服务(运行48小时)
python3 scripts/monitor_python312_upgrade.py --stage 4 --duration 172800 --interval 300
```

## 监控计划

为确保升级过程平稳进行，我们将对每个阶段的服务进行全面监控：

### 监控指标

- **服务可用性**: 健康检查端点响应状态
- **响应时间**: 服务响应延迟
- **错误率**: 请求失败比例
- **资源使用**: CPU/内存使用率
- **依赖服务**: 上下游服务交互情况
- **业务指标**: 关键业务功能正常运行

### 监控工具

- **监控脚本**: 使用 `scripts/monitor_python312_upgrade.py` 进行服务健康监控
- **Prometheus/Grafana**: 用于收集和可视化性能指标
- **日志分析**: 分析服务日志中的异常和错误
- **告警设置**: 当监控指标超过阈值时发送告警

### 执行监控命令示例

```bash
# 监控单个服务(5分钟间隔，运行24小时)
python3 scripts/monitor_python312_upgrade.py --services api-gateway --interval 300 --duration 86400

# 监控一个阶段的所有服务(5分钟间隔，运行48小时)
python3 scripts/monitor_python312_upgrade.py --stage 1 --interval 300 --duration 172800
```

## 回滚计划

如果在升级过程中发现严重问题，将执行以下回滚流程：

1. **立即回滚**:
   - 对于非关键服务出现非阻塞性问题，记录问题并继续监控
   - 对于关键服务出现严重问题，立即执行回滚

2. **回滚步骤**:
   ```bash
   # 回滚特定服务
   python3 scripts/deploy_python312.py --rollback --services service-name
   
   # 回滚整个阶段
   python3 scripts/deploy_python312.py --rollback --stage 1
   ```

3. **回滚后验证**:
   - 确认服务已成功回滚到之前的Python版本
   - 验证服务功能和性能已恢复正常
   - 进行根本原因分析，解决问题后再次尝试升级

## 升级时间线

| 阶段 | 开始日期 | 结束日期 | 服务 | 状态 |
|------|----------|----------|------|------|
| 准备工作 | 2025-05-22 | 2025-05-24 | 所有服务 | ✅ 已完成 |
| 阶段1 | 2025-05-27 | 2025-05-31 | 基础服务 | ⏳ 计划中 |
| 阶段2 | 2025-06-03 | 2025-06-07 | 核心业务服务 | 📅 计划中 |
| 阶段3 | 2025-06-10 | 2025-06-14 | 智能体服务 | 📅 计划中 |
| 阶段4 | 2025-06-17 | 2025-06-21 | 辅助服务 | 📅 计划中 |
| 验证和优化 | 2025-06-24 | 2025-06-28 | 所有服务 | 📅 计划中 |

## 升级验证

完成所有升级后，将进行全面的系统验证：

1. **性能基准测试**:
   - 使用suoke-bench-service进行性能基准测试
   - 对比升级前后的性能差异

2. **负载测试**:
   - 在生产级负载下验证系统稳定性
   - 确认高峰期间的资源使用情况

3. **功能测试**:
   - 执行端到端功能测试
   - 验证所有核心业务流程

## 文档和培训

1. **更新文档**:
   - 更新开发环境设置指南
   - 更新CI/CD流程文档
   - 更新依赖管理策略

2. **团队培训**:
   - 介绍Python 3.12新特性
   - 分享升级经验和最佳实践

## 后续步骤

1. 完成回归测试并解决发现的问题
2. 更新开发环境和CI/CD系统
3. 执行分阶段部署计划
4. 持续监控服务健康状况
5. 定期汇报升级进度

---

## 更新记录

- **2025-05-22**: 初始创建升级路线图
- **2025-05-23**: 完成自动化脚本开发和依赖兼容性修复
- **2025-05-24**: 更新路线图，添加监控计划和分阶段部署详情 