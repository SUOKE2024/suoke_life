# RAG服务重构测试计划

本文档详细说明了RAG服务从`go-src`目录结构重构到标准Go项目结构后的测试计划和步骤。测试分为自动化测试和手动验证两部分。

## 自动化测试

我们提供了自动化测试脚本`scripts/test_restructure.sh`，该脚本会执行以下测试：

1. **目录结构验证**：确保所有必要的目录和文件正确创建
2. **模块路径验证**：确保go.mod文件中的模块路径已正确更新
3. **导入路径验证**：确保所有Go文件中的导入路径已更新
4. **代码编译测试**：确保重构后的代码可以正常编译
5. **配置加载测试**：确保配置文件可以正常加载
6. **单元测试**：执行所有单元测试（如果存在）
7. **服务启动测试**：简单测试服务是否可以正常启动

### 运行自动化测试

```bash
cd /Users/songxu/Developer/suoke_life/services/rag-service
chmod +x scripts/test_restructure.sh
./scripts/test_restructure.sh
```

## 手动验证测试

除了自动化测试外，还应进行以下手动验证：

### 1. API功能测试

启动服务并测试核心API端点是否正常工作：

```bash
# 启动服务
cd /Users/songxu/Developer/suoke_life/services/rag-service
go run cmd/main.go

# 在另一个终端测试健康检查API
curl http://localhost:8080/health

# 测试RAG查询API
curl -X POST http://localhost:8080/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "测试查询", "topK": 3}'

# 测试嵌入生成API
curl -X POST http://localhost:8080/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本"}'
```

### 2. 日志输出验证

验证日志输出是否正常工作：

- 检查控制台日志输出格式是否正确
- 检查日志文件是否正常创建和写入
- 确认不同日志级别的消息是否按预期显示

### 3. 容器化测试

验证使用Docker构建和运行服务：

```bash
# 构建Docker镜像
docker build -t rag-service .

# 运行容器
docker run -p 8080:8080 --env-file .env rag-service

# 测试容器中的服务
curl http://localhost:8080/health
```

### 4. 高负载测试

如果可能，执行简单的负载测试确保服务在重构后性能正常：

```bash
# 使用ab工具进行简单的负载测试
ab -n 1000 -c 10 http://localhost:8080/health
```

## 回滚计划

如果测试过程中发现重大问题，可以使用恢复脚本恢复到原始状态：

```bash
cd /Users/songxu/Developer/suoke_life/services/rag-service
chmod +x scripts/restore.sh
./scripts/restore.sh
```

## 测试报告模板

在完成测试后，建议填写以下测试报告：

```
# RAG服务重构测试报告

日期：YYYY-MM-DD
测试人员：XXX

## 自动化测试结果
- 目录结构验证: [通过/失败]
- 模块路径验证: [通过/失败]
- 导入路径验证: [通过/失败]
- 代码编译测试: [通过/失败]
- 配置加载测试: [通过/失败]
- 单元测试: [通过/失败]
- 服务启动测试: [通过/失败]

## 手动验证结果
- API功能测试: [通过/失败]
- 日志输出验证: [通过/失败]
- 容器化测试: [通过/失败]
- 高负载测试: [通过/失败]

## 问题记录
1. [问题描述和解决方案]
2. ...

## 结论
[整体测试结论和建议]
```

## 最终部署建议

如果测试全部通过，建议执行以下步骤完成重构：

1. 备份`go-src`目录：`mv go-src go-src-backup`
2. 删除根目录下的冗余模块：`rm -rf vector_store utils rag models handlers embeddings core database config api`
3. 更新文档，记录重构完成日期和测试结果
4. 提交所有更改到代码仓库 