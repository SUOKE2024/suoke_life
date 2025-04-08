# 索克生活知识库服务测试指南

## 测试环境准备

1. 确保Docker和Docker Compose已安装
2. 确保Go 1.24或以上版本已安装

## 快速开始

```bash
# 启动必要的Docker服务
docker-compose up -d postgres etcd minio embedding-service

# 运行单元测试(跳过向量存储测试)
./scripts/docker-test.sh -u -s

# 运行基准测试(跳过向量存储测试)
./scripts/docker-test.sh -b -s
```

## 可用的测试脚本

1. **docker-test.sh**: 主要测试脚本，支持各种测试类型
   ```bash
   ./scripts/docker-test.sh [options]
   ```
   
   选项:
   - `-u` 运行单元测试
   - `-i` 运行集成测试
   - `-e` 运行端到端测试
   - `-b` 运行基准测试
   - `-c` 生成测试覆盖率
   - `-d` 测试完成后清理环境
   - `-a` 运行所有测试
   - `-s` 跳过向量存储测试(使用模拟实现)
   - `-h` 显示帮助信息

2. **run_local_tests.sh**: 简化版测试脚本，适合本地快速测试
   ```bash
   ./scripts/run_local_tests.sh
   ```

3. **run_doc_repo_test.sh**: 仅测试文档存储库
   ```bash
   ./scripts/run_doc_repo_test.sh
   ```

## 测试数据库配置

测试脚本会自动:
1. 创建`knowledge_base_test`测试数据库
2. 创建`testuser`用户并授予权限
3. 设置适当的环境变量

## 向量存储测试

1. **使用真实Milvus**: 
   需要成功拉取Milvus镜像并启动Milvus容器
   ```bash
   docker pull milvusdb/milvus:v2.4.2
   docker-compose up -d milvus
   ```

2. **使用模拟实现**:
   添加`-s`标志跳过真实向量存储测试
   ```bash
   ./scripts/docker-test.sh -a -s
   ```

## 常见问题解决

1. **PostgreSQL连接错误**:
   - 检查`testuser`用户是否存在且有权限
   - 检查端口映射是否正确
   - 尝试使用pgAdmin查看/管理PostgreSQL(http://localhost:8083)

2. **Milvus拉取失败**:
   - 设置Docker镜像代理
   - 使用`-s`标志跳过向量存储测试

3. **测试超时或失败**:
   - 检查各服务健康状态: `docker-compose ps`
   - 检查服务日志: `docker-compose logs <service-name>`

## 清理测试环境

```bash
# 停止所有容器
docker-compose down

# 或使用带清理标志的测试
./scripts/docker-test.sh -a -d
``` 