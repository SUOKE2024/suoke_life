# 索克生活无障碍服务测试指南

本文档提供了索克生活无障碍服务的详细测试指南，重点关注后台数据采集服务和危机报警服务的测试方法、场景和问题解决方案。

## 目录

- [环境准备](#环境准备)
- [单元测试](#单元测试)
- [后台数据采集服务测试](#后台数据采集服务测试)
- [危机报警服务测试](#危机报警服务测试)
- [平台适配层测试](#平台适配层测试)
- [集成测试](#集成测试)
- [常见问题解决](#常见问题解决)

## 环境准备

### 安装依赖

```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 特殊平台注意事项

#### Apple M系列芯片

在Apple M系列芯片上，mediapipe库存在兼容性问题。有两种方式处理：

1. 跳过mediapipe依赖：设置环境变量`TEST_ENVIRONMENT=true`
2. 使用兼容版本的PyTorch：安装PyTorch 2.7.0+版本

```bash
# 使用测试环境启动测试
TEST_ENVIRONMENT=true python -m pytest test
```

## 单元测试

单元测试使用Python标准的`pytest`框架，位于`test/`目录下。

### 运行所有测试

```bash
python -m pytest test
```

### 运行特定模块测试

```bash
python -m pytest test/test_background_collection.py
python -m pytest test/test_battery_bridge.py
```

### 生成测试覆盖率报告

```bash
python -m pytest --cov=internal test/
```

## 后台数据采集服务测试

后台数据采集服务(`BackgroundCollectionService`)的测试主要关注以下方面：

### 用户同意管理测试

```bash
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_register_user_consent
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_revoke_user_consent
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_get_user_consent_status
```

这些测试验证用户同意的注册、撤销和状态查询功能，确保数据采集遵循用户授权规则。

### 数据采集功能测试

```bash
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_collect_pulse_data
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_collect_sleep_data
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_collect_activity_data
```

验证不同类型数据的采集功能是否正常工作。

### 电池管理测试

```bash
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_battery_management
```

测试服务如何根据电池状态动态调整采集频率。在测试环境中，可以通过环境变量模拟不同电池状态：

```bash
MOCK_BATTERY_LEVEL=10 TEST_ENVIRONMENT=true python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_battery_management
```

### 用户状态检测测试

```bash
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_user_state_detection
```

验证服务能否正确识别用户的活跃、闲置或睡眠状态，并相应调整采集策略。

## 危机报警服务测试

危机报警服务(`CrisisAlertService`)的测试主要关注以下功能点：

### 警报级别测试

```bash
python -m pytest test/test_crisis_alert.py::TestCrisisAlertService::test_alert_levels
```

验证四级警报机制（信息、警告、危险、严重）是否正确处理不同级别的健康异常。

### 数据分析引擎测试

```bash
python -m pytest test/test_crisis_alert.py::TestCrisisAlertService::test_analyze_pulse_data
python -m pytest test/test_crisis_alert.py::TestCrisisAlertService::test_analyze_sleep_data
```

测试针对不同数据类型的分析算法是否能正确识别异常情况。

### 阈值设置测试

```bash
python -m pytest test/test_crisis_alert.py::TestCrisisAlertService::test_set_user_thresholds
```

验证用户个性化阈值设置功能。

### 智能体协作测试

```bash
python -m pytest test/test_crisis_alert.py::TestCrisisAlertService::test_agent_integration
```

测试危机报警服务与四大智能体的协作交互。

## 平台适配层测试

平台适配层测试主要关注不同操作系统和设备的兼容性：

### 电池桥接测试

```bash
python -m pytest test/test_battery_bridge.py
```

测试电池信息获取接口在不同平台的兼容性和可靠性。

### 缓存机制测试

```bash
python -m pytest test/test_battery_bridge.py::TestBatteryBridge::test_cache_expiry
```

验证缓存过期和刷新机制是否正常工作。

## 集成测试

集成测试验证多个服务组件之间的协作：

```bash
python test/integration_test.py
```

此测试验证以下集成场景：

1. 后台数据采集服务与危机报警服务的协作
2. 危机报警服务与智能体协作系统的集成
3. 平台桥接层与业务服务层的交互

## 常见问题解决

### 1. mediapipe依赖问题

**症状**：在安装或运行测试时出现mediapipe相关错误

**解决方案**：
```bash
# 使用测试环境模式运行
TEST_ENVIRONMENT=true python -m pytest test
```

### 2. 电池桥接测试失败

**症状**：电池桥接测试失败，通常是平台特定实现问题

**解决方案**：
```bash
# 确保设置测试环境
TEST_ENVIRONMENT=true python -m pytest test/test_battery_bridge.py

# 如果仍然失败，可以单独测试缓存机制
TEST_ENVIRONMENT=true python -m pytest test/test_battery_bridge.py::TestBatteryBridge::test_cache_expiry
```

### 3. gRPC导入问题

**症状**：导入accessibility_pb2或accessibility_pb2_grpc时出错

**解决方案**：
```bash
# 重新生成gRPC代码
cd api/grpc
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. accessibility.proto

# 修正导入路径
# 将import accessibility_pb2 修改为 from api.grpc import accessibility_pb2
```

### 4. 服务启动失败

**症状**：运行启动脚本时服务无法启动

**解决方案**：
```bash
# 检查日志目录权限
LOGGING_FILE=./logs/service.log ./scripts/start_service.sh

# 如果是依赖问题
TEST_ENVIRONMENT=true ./scripts/start_service.sh
```

### 5. 测试超时问题

**症状**：某些测试用例运行时间过长或超时

**解决方案**：
```bash
# 使用-v参数查看详细输出
python -m pytest -v test/test_background_collection.py

# 单独运行超时的测试用例
python -m pytest test/test_background_collection.py::TestBackgroundCollectionService::test_collection_worker -v
```

---

## 贡献测试用例

我们鼓励团队成员添加新的测试用例，特别是针对以下方面：

1. 极端场景测试（如电池极低、网络不稳定等）
2. 不同用户状态下的数据采集行为
3. 健康数据异常检测的边界情况
4. 多平台兼容性测试

添加新测试用例时，请确保：

1. 遵循现有测试命名和组织方式
2. 添加详细的测试文档注释
3. 确保测试用例独立且可重复执行
4. 提交前运行全部测试，确保不破坏现有功能

## 联系支持

如有任何测试相关问题，请联系无障碍服务团队：accessibility-team@suoke.life 