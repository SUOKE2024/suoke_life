# 无障碍服务测试套件

## 概述

本测试套件为索克生活无障碍服务重构项目提供全面的测试覆盖，包括单元测试、集成测试、性能测试和端到端测试。

## 测试结构

```
test/
├── test_service_implementations.py  # 单元测试
├── test_integration.py             # 集成测试
├── test_performance.py             # 性能测试
├── test_e2e.py                     # 端到端测试
├── run_tests.py                    # 测试运行脚本
└── README.md                       # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install pytest pytest-asyncio pytest-cov psutil
```

### 2. 运行所有测试

```bash
python test/run_tests.py --type all
```

### 3. 查看测试报告

```bash
python test/run_tests.py --type all --report
```

## 测试类型详解

### 1. 单元测试 (test_service_implementations.py)

**目的**: 测试各个服务实现的核心功能

**覆盖范围**:
- 导盲服务 (BlindAssistanceServiceImpl)
- 语音辅助服务 (VoiceAssistanceServiceImpl)
- 手语识别服务 (SignLanguageServiceImpl)
- 屏幕阅读服务 (ScreenReadingServiceImpl)
- 内容转换服务 (ContentConversionServiceImpl)

**运行方式**:
```bash
python test/run_tests.py --type unit
```

**测试示例**:
```python
@pytest.mark.asyncio
async def test_blind_assistance_analyze_scene():
    # 测试场景分析功能
    result = await service.analyze_scene(image_data, user_id, preferences, location)
    assert result['confidence'] > 0.8
    assert 'scene_type' in result
```

### 2. 集成测试 (test_integration.py)

**目的**: 测试服务间协调和完整业务流程

**覆盖范围**:
- 服务协调器功能
- 跨服务数据流
- 服务间依赖关系
- 完整业务场景

**运行方式**:
```bash
python test/run_tests.py --type integration
```

**测试场景**:
- 多服务协调场景
- 数据流转测试
- 错误传播测试
- 服务降级测试

### 3. 性能测试 (test_performance.py)

**目的**: 验证系统性能指标和扩展能力

**覆盖范围**:
- 并发性能测试
- 内存使用测试
- 启动时间测试
- 缓存性能测试
- 水平扩展测试

**运行方式**:
```bash
python test/run_tests.py --type performance
```

**性能指标**:
- QPS > 50 (50个并发用户时)
- 成功率 > 99%
- 平均响应时间 < 500ms
- 内存增长 < 300MB
- 启动时间 < 5s

### 4. 端到端测试 (test_e2e.py)

**目的**: 测试真实用户场景和API兼容性

**覆盖范围**:
- 完整用户场景
- API向后兼容性
- 真实数据流处理
- 多语言支持

**运行方式**:
```bash
python test/run_tests.py --type e2e
```

**用户场景**:
- 盲人用户导航场景
- 聋人用户交流场景
- 老年用户辅助场景
- 多语言用户场景

## 测试运行脚本

### 基本用法

```bash
# 运行所有测试
python test/run_tests.py --type all

# 运行特定类型测试
python test/run_tests.py --type unit
python test/run_tests.py --type integration
python test/run_tests.py --type performance
python test/run_tests.py --type e2e

# 运行测试覆盖率分析
python test/run_tests.py --type coverage
```

### 高级选项

```bash
# 运行特定测试文件
python test/run_tests.py --file test_service_implementations.py

# 运行特定测试函数
python test/run_tests.py --file test_service_implementations.py --function test_blind_assistance_service

# 生成测试报告
python test/run_tests.py --type all --report

# 检查测试依赖
python test/run_tests.py --check-deps

# 详细输出
python test/run_tests.py --type all --verbose
```

### 帮助信息

```bash
python test/run_tests.py --help
```

## 测试报告

### HTML报告

运行测试时使用 `--report` 参数会生成HTML格式的测试报告：

```bash
python test/run_tests.py --type all --report
```

报告文件：
- `test_report.html` - 详细的HTML测试报告
- `test_results.xml` - JUnit格式的XML报告

### 覆盖率报告

运行覆盖率测试会生成代码覆盖率报告：

```bash
python test/run_tests.py --type coverage
```

报告文件：
- `htmlcov/index.html` - HTML格式覆盖率报告
- 终端输出覆盖率摘要

## 测试配置

### 环境变量

```bash
# 设置测试环境
export ENVIRONMENT=test

# 设置日志级别
export LOG_LEVEL=DEBUG

# 设置测试数据目录
export TEST_DATA_DIR=/path/to/test/data
```

### pytest配置

在项目根目录的 `pytest.ini` 文件中配置：

```ini
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short
```

## 持续集成

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov psutil
    - name: Run tests
      run: python test/run_tests.py --type all --report
```

## 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保在正确的目录运行测试
   cd services/accessibility-service
   python test/run_tests.py --type all
   ```

2. **依赖缺失**
   ```bash
   # 检查并安装缺失的依赖
   python test/run_tests.py --check-deps
   ```

3. **异步测试问题**
   ```bash
   # 确保安装了 pytest-asyncio
   pip install pytest-asyncio
   ```

4. **性能测试失败**
   ```bash
   # 性能测试可能受系统负载影响，可以调整阈值或在空闲时运行
   python test/run_tests.py --type performance
   ```

### 调试技巧

1. **详细输出**
   ```bash
   python test/run_tests.py --type unit --verbose
   ```

2. **运行单个测试**
   ```bash
   python test/run_tests.py --file test_service_implementations.py --function test_specific_function
   ```

3. **使用pdb调试**
   ```bash
   python -m pytest test/test_service_implementations.py::test_function -s --pdb
   ```

## 贡献指南

### 添加新测试

1. **单元测试**: 在 `test_service_implementations.py` 中添加新的测试方法
2. **集成测试**: 在 `test_integration.py` 中添加新的测试场景
3. **性能测试**: 在 `test_performance.py` 中添加新的性能基准
4. **端到端测试**: 在 `test_e2e.py` 中添加新的用户场景

### 测试命名规范

- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`
- 异步测试: 使用 `@pytest.mark.asyncio` 装饰器

### 测试最佳实践

1. **独立性**: 每个测试应该独立运行
2. **可重复性**: 测试结果应该可重复
3. **清晰性**: 测试意图应该清晰明确
4. **覆盖性**: 测试应该覆盖正常和异常情况
5. **性能**: 测试应该快速执行

## 联系方式

如有测试相关问题，请联系开发团队或在项目仓库中提交Issue。 