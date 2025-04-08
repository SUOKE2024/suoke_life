# 代理协调器服务测试文档

## 测试概述

代理协调器服务实现了全面的测试策略，包括单元测试、集成测试和基准测试。我们的目标是确保API的可靠性、稳定性和性能。

## 测试类型

### 单元测试

单元测试专注于测试单个组件的功能，特别是处理程序逻辑。这些测试使用模拟依赖项来隔离被测试的组件。

**目录**: `internal/handlers/*.test.go`

### 集成测试

集成测试验证API端点的完整请求-响应流程，确保各组件之间的正确交互。

**目录**: `internal/tests/integration/*.test.go`

### 基准测试

基准测试衡量关键功能的性能，帮助我们识别性能瓶颈并优化代码。

**目录**: `internal/tests/benchmark/*.test.go`

### 错误情况测试

错误情况测试验证系统对错误输入和边界条件的处理能力，确保系统在各种异常情况下表现出预期行为。

**目录**: `internal/tests/integration/*.test.go` (使用 `ErrorTestCase` 结构)

### 边界条件测试

边界条件测试关注系统在各种边界情况下的行为，如极大数据量、特殊字符输入、资源限制等。

**目录**: `internal/tests/integration/*.test.go` (使用 `BoundaryTestCase` 结构)

### 生命周期测试

生命周期测试模拟真实用户的完整操作流程，通过一系列相互关联的API调用来验证系统的端到端功能。

**目录**: `internal/tests/integration/*.test.go` (使用 `TestLifecycle` 函数)

## 测试工具

- **测试框架**: Go标准测试包 (`testing`)
- **断言库**: `github.com/stretchr/testify/assert`
- **模拟库**: `github.com/stretchr/testify/mock`
- **HTTP测试**: `net/http/httptest`
- **JSON处理**: 标准`encoding/json`包
- **测试工具包**: `internal/tests/testutils`，包含自定义测试工具和辅助函数

## 测试结构

### 测试工具包 (`internal/tests/testutils`)

包含通用测试函数和结构体，减少重复代码并简化测试编写。主要组件包括：

- **APITestCase**: 定义正常API测试用例
- **ErrorTestCase**: 定义错误情况测试用例
- **BoundaryTestCase**: 定义边界条件测试用例
- **RunAPITests**: 运行正常API测试集合
- **RunErrorTests**: 运行错误情况测试集合
- **RunBoundaryTests**: 运行边界条件测试集合

### 模拟组件 (`internal/tests/mocks`)

包含模拟存储库和服务的实现，用于替代真实依赖项进行测试。

## 运行测试

### 运行所有测试

```bash
./scripts/run_tests.sh -a -c
```

### 运行所有单元测试

```bash
./scripts/run_tests.sh -u
```

或者使用Go命令:

```bash
go test -v ./internal/handlers/...
```

### 运行集成测试

```bash
./scripts/run_tests.sh -i
```

### 运行基准测试

```bash
./scripts/run_tests.sh -b
```

### 运行错误情况测试

```bash
./scripts/run_tests.sh -e
```

### 运行边界条件测试

```bash
./scripts/run_tests.sh -y
```

### 运行生命周期测试

```bash
./scripts/run_tests.sh -l
```

### 运行特定测试

```bash
go test -v ./internal/handlers -run TestHealthCheck
```

### 生成测试覆盖率报告

```bash
./scripts/run_tests.sh -a -c
```

或者使用Go命令:

```bash
go test -coverprofile=coverage.out ./internal/handlers/...
go tool cover -html=coverage.out -o coverage.html
```

## 编写新测试

### 单元测试最佳实践

1. 每个测试函数只测试一个功能点
2. 使用描述性的测试函数名称 (如 `TestHealthCheck_ReturnsCorrectStatusCode`)
3. 为每个测试设置独立的测试环境
4. 使用断言库进行验证 (`assert.Equal`, `assert.Contains` 等)
5. 模拟外部依赖项

### 集成测试最佳实践

1. 测试完整的API调用流程
2. 验证HTTP状态码和响应体
3. 测试特定的用例场景（如创建-获取-更新-删除流程）
4. 利用 `testutils` 包减少重复代码

### 编写错误情况测试

1. 使用 `ErrorTestCase` 结构体定义测试用例
2. 指明预期的HTTP状态码和错误消息
3. 测试各种输入验证和边界条件
4. 使用 `RunErrorTests` 运行测试集合

### 编写边界条件测试

1. 使用 `BoundaryTestCase` 结构体定义测试用例
2. 实现自定义请求构建函数和断言函数
3. 测试极端情况和特殊输入
4. 使用 `RunBoundaryTests` 运行测试集合

### 编写生命周期测试

1. 在单个测试函数中模拟完整的用户操作流程
2. 按顺序执行创建、读取、更新、删除等操作
3. 验证每个步骤的响应和数据一致性
4. 确保测试结束时清理所有资源

### 编写基准测试

1. 使用 `testing.B` 参数
2. 在基准测试中，仅执行关键验证
3. 使用 `b.ResetTimer()` 避免包含设置时间
4. 考虑添加并行基准测试版本 (`b.RunParallel`)

## 自动化测试流程

### CI/CD 集成

服务已配置为在Pull Request和推送到主分支时自动运行测试。CI流程中包括：

1. 单元测试和覆盖率分析
2. 集成测试验证
3. 基准测试结果比较
4. 错误情况和边界条件测试

### 测试环境

1. **开发环境**: 开发人员在本地运行的测试
2. **CI环境**: 在自动化流程中运行的测试
3. **预生产环境**: 在部署到生产前的最终验证

## 测试报告

测试结果会自动生成报告并存储在CI/CD系统中。覆盖率报告也可以在构建过程中生成和归档。

## 故障排除

### 常见测试失败问题

1. **模拟对象未被调用**: 验证模拟对象的期望是否正确设置
2. **HTTP状态码不匹配**: 检查请求是否正确，路由是否注册
3. **JSON解析错误**: 验证响应格式是否与预期一致
4. **错误消息不匹配**: 检查错误字段路径和预期错误消息是否正确

### 调试技巧

1. 使用 `-v` 标志获取详细输出
2. 检查日志记录
3. 添加临时断言来隔离问题 