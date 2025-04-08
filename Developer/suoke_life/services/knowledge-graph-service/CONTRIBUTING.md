# 索克生活知识图谱服务贡献指南

感谢您对索克生活知识图谱服务的贡献兴趣！本文档提供了参与项目开发的指南。

## 开发环境设置

### 前提条件

- Go 1.20+
- Docker和Docker Compose (用于本地测试)
- Neo4j 4.4+ (可通过Docker运行)
- Git

### 本地开发环境设置

1. 克隆仓库：

```bash
git clone https://github.com/suoke-life/knowledge-graph-service.git
cd knowledge-graph-service
```

2. 安装依赖：

```bash
go mod download
```

3. 设置环境变量（本地开发）：

```bash
cp configs/config.example.yaml configs/config.local.yaml
# 编辑config.local.yaml设置本地配置
```

4. 使用Docker Compose启动依赖服务（Neo4j和Redis）：

```bash
docker-compose -f docker-compose.dev.yaml up -d
```

5. 构建和运行服务：

```bash
go build -o kg-service ./cmd/server
./kg-service
```

## 代码规范

### Go代码风格指南

- 遵循[Effective Go](https://golang.org/doc/effective_go)和[Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)中的建议
- 使用`gofmt`或`goimports`格式化代码
- 使用[golangci-lint](https://golangci-lint.run/)进行代码检查

### 命名约定

- 包名：使用小写单词，不使用下划线或混合大小写
- 文件名：使用下划线分隔的小写单词（如`node_repository.go`）
- 接口名：通常以"er"结尾（如`NodeRepository`）
- 结构体：使用驼峰命名法（如`NodeService`）
- 常量：使用全大写下划线分隔命名（如`DEFAULT_BATCH_SIZE`）

### 项目结构

遵循Clean Architecture和Go项目标准结构：

```
.
├── cmd/                  # 可执行命令
│   ├── server/           # API服务器入口
│   └── importer/         # 数据导入工具
├── internal/             # 内部包
│   ├── api/              # API处理程序
│   ├── config/           # 配置
│   ├── database/         # 数据库连接
│   ├── domain/           # 领域模型
│   │   ├── entities/     # 实体定义
│   │   ├── repositories/ # 存储库接口
│   ├── infrastructure/   # 基础设施
│   │   ├── repositories/ # 存储库实现
├── pkg/                  # 公共包
```

### 错误处理

- 使用意义明确的错误信息
- 对于公共API，使用`errors.New`或`fmt.Errorf`创建有描述性的错误
- 内部错误优先使用`pkg/errors`包进行错误包装
- 避免使用`panic`，除非是不可恢复的错误

### 日志记录

- 使用结构化日志（我们使用`logrus`）
- 适当的日志级别：
  - `Debug`：调试信息
  - `Info`：重要操作（启动、关闭等）
  - `Warn`：需要关注但不是错误的问题
  - `Error`：运行时错误
  - `Fatal`：导致程序终止的错误

## 提交流程

### 分支和版本管理

- `main`分支：稳定版本，生产就绪代码
- `develop`分支：开发分支，包含下一版本的功能
- 功能分支：从`develop`分支创建，命名为`feature/描述`
- 修复分支：从`main`分支创建，命名为`hotfix/描述`

### 提交信息规范

请遵循[约定式提交](https://www.conventionalcommits.org/)格式：

```
<类型>(<范围>): <描述>

[可选的正文]

[可选的页脚]
```

类型包括：
- `feat`：新功能
- `fix`：bug修复
- `docs`：文档更改
- `style`：不影响代码含义的变化（空白、格式化等）
- `refactor`：代码重构
- `perf`：性能改进
- `test`：测试相关
- `chore`：构建过程或辅助工具的变动

示例：
```
feat(api): 添加节点批量创建API

添加了节点批量创建API，提高大规模数据导入效率。

Closes #123
```

### 代码审查流程

1. 创建一个功能分支
2. 提交更改
3. 创建一个指向`develop`分支的Pull Request
4. 确保所有测试通过
5. 等待代码审查
6. 根据反馈进行必要的修改
7. 代码审查通过后，分支将被合并

## 测试

### 测试规范

- 单元测试：测试单个函数或方法
- 集成测试：测试组件之间的交互
- 端到端测试：测试整个API流程

### 运行测试

```bash
# 运行所有测试
go test ./...

# 运行特定包的测试
go test ./internal/api/...

# 运行测试并查看覆盖率
go test -cover ./...

# 生成覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### 测试要求

- 所有新功能必须包含测试
- 修复bug时，添加一个测试用例来验证修复
- 保持测试覆盖率在70%以上

## 文档规范

- 所有导出的函数、类型和变量必须有文档注释
- 复杂的函数应该包括示例
- API变更必须更新相应的API文档
- 使用[Go Doc](https://pkg.go.dev/)格式的文档注释

## 工具和资源

- [golangci-lint](https://golangci-lint.run/) - 代码检查工具
- [mockery](https://github.com/vektra/mockery) - 生成测试模拟
- [swag](https://github.com/swaggo/swag) - Swagger API文档生成

## 联系我们

如有问题或需要进一步的指导，请联系：

- 技术团队：dev@suoke.life
- 项目维护者：技术架构团队 