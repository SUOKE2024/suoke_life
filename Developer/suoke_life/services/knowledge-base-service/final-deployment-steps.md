# 知识库服务部署完整解决方案

本文档详细说明了知识库服务的完整部署步骤和解决方案。

## 1. 准备依赖服务

在部署知识库服务前，需要确保以下依赖服务已经正常运行：

### PostgreSQL 数据库

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: suoke-prod
spec:
  serviceName: "postgres-service"
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: POSTGRES_DB
          value: "suoke"
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: postgres-data-postgres-0
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: suoke-prod
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None
```

### Milvus 向量数据库

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: milvus
  namespace: suoke-prod
spec:
  serviceName: "milvus-service"
  replicas: 1
  selector:
    matchLabels:
      app: milvus
  template:
    metadata:
      labels:
        app: milvus
    spec:
      containers:
      - name: milvus
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/milvus:v2.2.11
        ports:
        - containerPort: 19530
          name: milvus
        volumeMounts:
        - name: milvus-data
          mountPath: /var/lib/milvus
      volumes:
      - name: milvus-data
        persistentVolumeClaim:
          claimName: milvus-data-milvus-0
---
apiVersion: v1
kind: Service
metadata:
  name: milvus-service
  namespace: suoke-prod
spec:
  selector:
    app: milvus
  ports:
  - port: 19530
    targetPort: 19530
  type: ClusterIP
```

### 解决方案步骤

1. 首先解决Milvus崩溃问题
   - 检查Milvus日志确定根本原因
   - 可能需要增加资源限制或修改配置参数
   - 如有必要，考虑使用simpler-milvus镜像

2. 确保PostgreSQL数据库正常运行
   - 验证用户权限和数据库存在
   - 确认连接字符串的正确性
   - 执行数据库初始化脚本

## 2. 构建并推送知识库服务镜像

```bash
# 构建镜像
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service:latest .

# 登录到阿里云容器镜像服务
docker login suoke-registry.cn-hangzhou.cr.aliyuncs.com --username [USERNAME] --password [PASSWORD]

# 推送镜像
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service:latest
```

## 3. 部署知识库服务

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-base-service
  namespace: suoke-prod
  labels:
    app: knowledge-base-service
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: knowledge-base-service
  template:
    metadata:
      labels:
        app: knowledge-base-service
        version: v1
    spec:
      containers:
      - name: knowledge-base-service
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3002
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: PORT
          value: "3002"
        - name: APP_HOST
          value: "0.0.0.0"
        - name: DB_CONNECTION_STRING
          value: "postgresql://$(DATABASE_USER):$(DATABASE_PASSWORD)@postgres-service:5432/suoke?sslmode=disable"
        - name: DATABASE_HOST
          value: "postgres-service"
        - name: DATABASE_PORT
          value: "5432"
        - name: DATABASE_NAME
          value: "suoke"
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: DATABASE_SSL_MODE
          value: "disable"
        - name: VECTOR_STORE_HOST
          value: "milvus-service"
        - name: VECTOR_STORE_PORT
          value: "19530"
        - name: EMBEDDING_MODEL_URL
          value: "http://embedding-service:8000/embed"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        - name: tmp
          mountPath: /app/tmp
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 15
          timeoutSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: knowledge-base-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: knowledge-base-logs-pvc
      - name: tmp
        emptyDir: {}
      imagePullSecrets:
      - name: aliyun-docker-registry
      - name: suoke-registry-secret
```

## 4. 验证部署

```bash
# 检查服务状态
kubectl get pods -l app=knowledge-base-service -n suoke-prod

# 查看服务日志
kubectl logs -l app=knowledge-base-service -n suoke-prod

# 测试服务接口
kubectl port-forward service/knowledge-base-service 3002:80 -n suoke-prod
curl http://localhost:3002/api/v1/health
```

## 附录：故障排查

1. 镜像拉取失败
   - 检查镜像名称和标签是否正确
   - 验证镜像仓库凭证是否有效
   - 确认网络连接是否正常

2. 容器启动失败
   - 检查环境变量是否正确配置
   - 验证依赖服务是否可达
   - 查看应用日志获取详细错误信息

3. 服务健康检查失败
   - 确认健康检查端点是否正确
   - 检查应用是否正确处理健康检查请求
   - 调整健康检查参数，如超时和初始延迟