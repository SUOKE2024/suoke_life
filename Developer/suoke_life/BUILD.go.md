# 索克生活APP - 代理协调器服务 (Go版) 构建指南

## 开发环境准备

1. 安装Go 1.20或更高版本
   ```bash
   # 检查Go版本
   go version
   
   # 如果需要安装或更新
   # macOS (使用Homebrew)
   brew install go
   
   # Linux (Ubuntu/Debian)
   wget https://go.dev/dl/go1.20.linux-amd64.tar.gz
   sudo tar -C /usr/local -xzf go1.20.linux-amd64.tar.gz
   export PATH=$PATH:/usr/local/go/bin
   ```

2. 设置GOPATH和GOROOT (如果尚未设置)
   ```bash
   # 将这些行添加到您的~/.bashrc或~/.zshrc文件中
   export GOPATH=$HOME/go
   export PATH=$PATH:$GOPATH/bin
   ```

## 本地构建与运行

### 克隆代码库
```bash
git clone <repository-url>
cd services/agent-coordinator-service
```

### 安装依赖
```bash
go mod tidy
```

### 配置
```bash
# 复制配置文件
cp .env.example .env

# 编辑.env文件，根据需要调整配置
vi .env
```

### 本地编译
```bash
# 开发模式编译
go build -o bin/agent-coordinator-service ./cmd/main.go

# 生产模式编译（优化的二进制文件）
go build -ldflags="-s -w" -o bin/agent-coordinator-service ./cmd/main.go
```

### 运行服务
```bash
# 开发模式运行
./bin/agent-coordinator-service

# 或者直接使用go run
go run cmd/main.go
```

## Docker构建与运行

### 构建Docker镜像
```bash
# 使用Go专用Dockerfile构建
docker build -t agent-coordinator-service:go-1.0 -f Dockerfile.go .
```

### 运行Docker容器
```bash
# 基本运行
docker run -p 3007:3007 agent-coordinator-service:go-1.0

# 使用环境变量
docker run -p 3007:3007 \
  -e PORT=3007 \
  -e LOG_LEVEL=debug \
  agent-coordinator-service:go-1.0

# 挂载配置文件
docker run -p 3007:3007 \
  -v $(pwd)/config:/app/config \
  agent-coordinator-service:go-1.0
```

## 生产环境部署

### 推送到容器仓库
```bash
# 标记镜像
docker tag agent-coordinator-service:go-1.0 suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service:go-1.0

# 登录到容器仓库
docker login --username=<阿里云账号> suoke-registry.cn-hangzhou.cr.aliyuncs.com

# 推送镜像
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service:go-1.0
```

### 使用Helm部署到Kubernetes
```bash
# 测试环境部署
helm upgrade --install agent-coordinator-test ./helm/agent-coordinator \
  --namespace suoke-test \
  --set image.repository=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service \
  --set image.tag=go-1.0 \
  --set environment=testing \
  --set replicaCount=1

# 生产环境部署
helm upgrade --install agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --set image.repository=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service \
  --set image.tag=go-1.0 \
  --set environment=production \
  --set replicaCount=2
```

## 测试构建

### 运行单元测试
```bash
go test ./... -v
```

### 运行基准测试
```bash
go test -bench=. ./...
```

### 运行覆盖率测试
```bash
go test -cover ./...

# 或生成覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## 疑难解答

### 常见问题

1. 依赖问题
   ```bash
   # 更新所有依赖
   go get -u ./...
   
   # 清理模块缓存
   go clean -modcache
   ```

2. 权限问题
   ```bash
   # 确保执行文件有执行权限
   chmod +x bin/agent-coordinator-service
   ```

3. 端口占用
   ```bash
   # 查找占用端口的进程
   lsof -i :3007
   
   # 终止占用端口的进程
   kill -9 <PID>
   ```

4. 日志级别调整
   - 设置环境变量`LOG_LEVEL=debug`可以获取更详细的日志
   - 生产环境中建议使用`LOG_LEVEL=info`或`LOG_LEVEL=warn`

## 性能优化建议

1. 使用`GOMAXPROCS`环境变量控制Go运行时使用的处理器数量
   ```bash
   export GOMAXPROCS=4
   ```

2. 使用分析工具找出性能瓶颈
   ```bash
   go tool pprof -http=:8081 http://localhost:3007/debug/pprof/profile
   ```

3. 内存优化
   - 使用对象池减少垃圾回收压力
   - 避免不必要的大对象分配
   - 定期运行`GOGC=off`进行性能比较测试

## 安全建议

1. 在生产环境中始终启用API认证
   ```
   ENABLE_API_AUTH=true
   API_KEY=<安全的、随机生成的密钥>
   ```

2. 使用HTTPS协议，可以在Nginx或Kubernetes Ingress中配置SSL

3. 定期更新依赖以防止安全漏洞
   ```bash
   go list -m -u all
   ```

4. 使用容器安全扫描工具检查Docker镜像
   ```bash
   docker scan agent-coordinator-service:go-1.0
   ``` 