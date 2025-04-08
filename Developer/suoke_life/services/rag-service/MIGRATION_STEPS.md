# RAG服务从Python/Node.js到Go的迁移步骤

本文档记录了将RAG服务从Python/Node.js重构为Go的完整步骤，便于项目团队成员了解迁移进度和后续工作。

## 已完成工作

1. ✅ **Go代码开发**
   - 完整实现了RAG服务的API接口和核心功能
   - 创建了合适的项目结构和模块化设计
   - 编写了单元测试确保功能正确性

2. ✅ **部署配置更新**
   - 更新了Kubernetes部署文件
   - 创建了专门的Go版Dockerfile
   - 更正了命名空间为"suoke-prod"

3. ✅ **CI/CD流程更新**
   - 创建了专门的Go CI/CD工作流程文件(go-ci.yml)
   - 增加了Go特有的代码检查、测试和构建步骤
   - 配置了构建和部署Go应用的流程

4. ✅ **迁移准备**
   - 创建了归档旧代码的脚本(archive_old_code.sh)
   - 创建了Go代码迁移脚本(move_go_code.sh)
   - 增加了部署验证脚本(verify_go_deployment.sh)

## 执行迁移步骤

请按照以下步骤完成最终迁移：

1. **归档旧代码**
   ```bash
   cd services/rag-service
   ./scripts/archive_old_code.sh
   ```

2. **删除原Python源代码**
   ```bash
   rm -rf src requirements.txt mypy.ini .pylintrc test-app.py
   ```

3. **移动Go代码到根目录**
   ```bash
   ./mv_script/move_go_code.sh
   ```

4. **更新Dockerfile**
   ```bash
   mv Dockerfile.go Dockerfile
   ```

5. **确保脚本具有执行权限**
   ```bash
   chmod +x ./scripts/verify_go_deployment.sh
   ```

6. **提交更改到代码库**
   ```bash
   git add .
   git commit -m "完成RAG服务从Python/Node.js到Go的迁移"
   git push
   ```

## 验证部署

1. **在开发环境验证**
   ```bash
   ./scripts/verify_go_deployment.sh --env=dev
   ```

2. **在预发布环境验证**
   ```bash
   ./scripts/verify_go_deployment.sh --env=staging
   ```

3. **在生产环境验证**
   ```bash
   ./scripts/verify_go_deployment.sh --env=prod
   ```

## 注意事项

- 确保在迁移过程中保持服务可用，建议先在非生产环境完成测试
- 请保留归档代码一段时间，直到确认Go版本稳定运行
- 如遇问题，可随时回滚到归档的Python/Node.js版本
- 按照云原生最佳实践，确保所有配置都通过Kubernetes配置管理，避免硬编码

## 最新重构：标准化目录结构 (2024-06-XX)

为解决目录结构冗余问题，我们进行了标准化目录结构重构，具体步骤如下:

### 1. 目录结构标准化

将项目结构重新组织为符合Go项目标准结构:

```
services/rag-service/
├── cmd/                    # 命令行入口
│   └── main.go            # 主程序入口
├── internal/               # 内部包（不对外暴露）
│   ├── api/               # API定义
│   ├── config/            # 配置管理
│   ├── handlers/          # 请求处理器
│   ├── middleware/        # 中间件
│   ├── models/            # 数据模型
│   ├── rag/               # RAG核心功能
│   ├── storage/           # 存储相关
│   │   └── vector_store/  # 向量存储
│   ├── embeddings/        # 嵌入模型
│   └── utils/             # 工具函数
├── pkg/                    # 可对外暴露的包
├── tests/                  # 测试文件
├── scripts/                # 辅助脚本
├── docs/                   # 文档
└── deployment/             # 部署配置
```

### 2. 导入路径更新

更新所有导入路径，从原始路径:
- `github.com/suoke/suoke_life/services/rag-service/go-src/...`
- `github.com/suoke/suoke_life/services/rag-service/rag/...`

到新路径:
- `github.com/suoke/suoke_life/services/rag-service/internal/...`

### 3. 执行重构步骤

为了简化重构过程，我们提供了自动化脚本。按照以下步骤执行重构：

```bash
# 1. 确保在rag-service根目录
cd services/rag-service

# 2. 确保重构脚本有执行权限
chmod +x scripts/restructure.sh

# 3. 执行重构脚本
./scripts/restructure.sh

# 4. 验证重构结果
go mod tidy
go build ./cmd
```

### 4. 验证步骤

1. 运行测试确保功能正常
```bash
go test ./internal/...
```

2. 启动服务验证
```bash
cd cmd && go run main.go
```

3. 检查API端点是否正常工作
```bash
curl http://localhost:8080/health
```

### 5. 清理步骤

在确认新结构正常工作后，可以删除冗余目录:

```bash
# 备份go-src目录
mv go-src go-src-backup

# 如果一切正常，可以删除备份
# rm -rf go-src-backup
```

## 历史迁移记录

// ... existing code ... 