# 代理协调器服务测试计划

## 1. 单元测试

- **范围**: 所有内部包的功能
- **工具**: Go内置测试框架
- **自动化**: 通过GitHub Actions在每次推送时运行
- **覆盖率目标**: 至少80%代码覆盖率

## 2. 集成测试

- **范围**: API端点、持久化层、外部服务集成
- **环境**: 本地测试环境或CI/CD流水线
- **数据**: 使用测试数据库和模拟外部服务
- **频率**: 每次合并请求提交

## 3. 性能测试

- **类型**:
  - 负载测试(标准负载)
  - 压力测试(最大负载)
  - 耐久测试(长时间运行)
  - 突发负载测试(短时间高负载)
  
- **指标**:
  - 响应时间
  - 吞吐量(RPS)
  - 错误率
  - 资源使用(CPU、内存、网络)
  
- **工具**: wrk, hey, Prometheus+Grafana

## 4. 安全测试

- **内容**:
  - API认证测试
  - 速率限制测试
  - 输入验证测试
  - 依赖扫描

## 5. 回归测试

- **时机**: 在每个主要功能完成后
- **内容**: 确保新功能不影响现有功能

## 6. 验收测试

- **标准**:
  - 功能验收: 所有API返回预期结果
  - 性能验收: 在预期负载下响应时间<100ms
  - 稳定性验收: 7天无故障运行
  - 资源验收: 满足资源使用目标

## 测试环境设置

### 本地测试环境
```bash
# 设置测试环境
export CONFIG_PATH=internal/api/testdata/test_config.json
export PORT=3007

# 运行服务
go run cmd/main.go
```

### CI/CD测试环境
- 使用GitHub Actions或Jenkins
- 自动化构建、测试和部署
- 每个PR自动运行测试套件

## 运行测试

### 单元测试
```bash
go test -v ./...
```

### 覆盖率测试
```bash
go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
go tool cover -html=coverage.out -o coverage.html
```

### 性能测试
```bash
./scripts/benchmark/load_test.sh
``` 