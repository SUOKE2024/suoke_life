# 索克生活五诊系统 (Five Diagnosis System)

## 🌟 系统概述

索克生活五诊系统是一个基于人工智能的现代化中医诊断平台，将传统中医的"四诊合参"扩展为创新的"五诊合参"体系。系统融合了望、闻、问、切四诊与独创的"算诊"功能，构建了完整的智能健康诊断生态。

### 🔮 核心创新 - 算诊功能

**算诊**是本系统的核心创新，全球首个完整的数字化算诊系统，包含：
- **子午流注分析** - 基于十二经络时间医学的健康分析
- **八字体质分析** - 根据出生时间分析个人体质特征
- **八卦配属分析** - 运用易学理论进行健康状态分析
- **五运六气分析** - 基于运气学说的疾病预测和调养指导

### 🏗️ 系统架构

```
五诊系统架构
├── 🔮 算诊服务 (8003) - 核心创新
├── 👁️ 望诊服务 (8080) - 计算机视觉
├── 👂 闻诊服务 (8000) - 音频AI分析
├── 💬 问诊服务 (8001) - NLP智能问诊
├── 🤲 切诊服务 (8002) - 传感器诊断
├── 🌐 API网关 (80) - 统一入口
└── 📊 监控系统 - 完整运维
```

## 🚀 快速开始

### 环境要求

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Python** >= 3.11
- **内存** >= 8GB
- **磁盘** >= 50GB

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/suoke-life/suoke_life.git
cd suoke_life/services/diagnostic-services

# 2. 配置环境变量
cp five-diagnosis.env.example .env
# 编辑 .env 文件，设置密码和密钥

# 3. 启动所有服务
docker-compose -f docker-compose.five-diagnosis.yml up -d

# 4. 检查服务状态
docker-compose -f docker-compose.five-diagnosis.yml ps

# 5. 查看日志
docker-compose -f docker-compose.five-diagnosis.yml logs -f
```

### 验证部署

```bash
# 检查各服务健康状态
curl http://localhost:8003/ping    # 算诊服务
curl http://localhost:8080/health  # 望诊服务
curl http://localhost:8000/health  # 闻诊服务
curl http://localhost:8001/health  # 问诊服务
curl http://localhost:8002/health  # 切诊服务

# 访问监控面板
open http://localhost:3000         # Grafana (admin/your_password)
open http://localhost:9090         # Prometheus
open http://localhost:16686        # Jaeger
open http://localhost:8090         # Traefik Dashboard
```

## 📋 服务详情

### 🔮 算诊服务 (Calculation Service)

**端口**: 8003 | **技术**: Python 3.11 + FastAPI

#### 核心功能
- **子午流注**: 十二经络时间医学分析
- **八字体质**: 个人体质特征分析
- **八卦配属**: 易学健康状态分析
- **五运六气**: 疾病预测和调养指导

#### API端点
```bash
POST /api/v1/calculation/comprehensive  # 综合算诊
POST /api/v1/calculation/ziwu           # 子午流注
POST /api/v1/calculation/constitution   # 八字体质
POST /api/v1/calculation/bagua          # 八卦配属
POST /api/v1/calculation/wuyun          # 五运六气
```

### 👁️ 望诊服务 (Look Service)

**端口**: 8080 | **技术**: Python 3.13.3 + OpenCV

#### 核心功能
- **面部诊断**: 基于CV的面部特征分析
- **舌诊分析**: 舌质舌苔智能识别
- **体态评估**: 体型体态健康评估
- **皮肤诊断**: 皮肤色泽纹理分析

#### API端点
```bash
POST /api/v1/look/face     # 面部诊断
POST /api/v1/look/tongue   # 舌诊分析
POST /api/v1/look/posture  # 体态评估
POST /api/v1/look/skin     # 皮肤诊断
```

### 👂 闻诊服务 (Listen Service)

**端口**: 8000 | **技术**: Python 3.13.3 + 音频AI

#### 核心功能
- **语音分析**: 声音特征健康分析
- **呼吸音诊断**: 呼吸模式音质分析
- **咳嗽分析**: 咳嗽声病理识别
- **心音分析**: 心跳节律音质评估

#### API端点
```bash
POST /api/v1/listen/voice   # 语音分析
POST /api/v1/listen/breath  # 呼吸音诊断
POST /api/v1/listen/cough   # 咳嗽分析
POST /api/v1/listen/heart   # 心音分析
```

### 💬 问诊服务 (Inquiry Service)

**端口**: 8001 | **技术**: Python 3.13.3 + NLP

#### 核心功能
- **智能问诊**: AI驱动症状收集
- **症状提取**: 智能症状信息提取
- **证型匹配**: 症状到证型映射
- **风险评估**: 健康风险评估

#### API端点
```bash
POST /api/v1/inquiry/session   # 开始问诊
POST /api/v1/inquiry/interact  # 问诊交互
POST /api/v1/inquiry/extract   # 症状提取
POST /api/v1/inquiry/assess    # 风险评估
```

### 🤲 切诊服务 (Palpation Service)

**端口**: 8002 | **技术**: Python 3.13.3 + 传感器

#### 核心功能
- **脉诊分析**: 传感器脉象识别
- **触觉诊断**: 皮肤温湿度弹性
- **压痛点检测**: 穴位压痛定位
- **体征监测**: 实时生理参数

#### API端点
```bash
POST /api/v1/palpation/pulse     # 脉诊分析
POST /api/v1/palpation/touch     # 触觉诊断
POST /api/v1/palpation/pressure  # 压痛点检测
POST /api/v1/palpation/vital     # 体征监测
```

## 🔧 配置管理

### 环境变量配置

系统使用环境变量进行配置管理，主要配置文件：

- `five-diagnosis.env.example` - 环境变量模板
- `five-diagnosis-config.yml` - 系统配置文件
- `docker-compose.five-diagnosis.yml` - 容器编排配置

### 关键配置项

```bash
# 数据库配置
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
MONGO_PASSWORD=your_mongo_password

# 安全配置
JWT_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# 服务配置
CALCULATION_SERVICE_PORT=8003
LOOK_SERVICE_PORT=8080
LISTEN_SERVICE_PORT=8000
INQUIRY_SERVICE_PORT=8001
PALPATION_SERVICE_PORT=8002
```

## 📊 监控运维

### 监控组件

- **Prometheus** (9090) - 指标收集
- **Grafana** (3000) - 可视化面板
- **Jaeger** (16686) - 链路追踪
- **ELK Stack** - 日志聚合分析

### 关键指标

```yaml
业务指标:
  - 诊断准确率
  - 用户满意度
  - 五诊融合成功率

技术指标:
  - 响应时间 (< 5秒)
  - 错误率 (< 0.1%)
  - 吞吐量 (1000+ QPS)

资源指标:
  - CPU使用率
  - 内存使用率
  - 磁盘IO
  - 网络带宽
```

### 健康检查

```bash
# 服务健康检查脚本
#!/bin/bash
services=("calculation:8003" "look:8080" "listen:8000" "inquiry:8001" "palpation:8002")

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $name service is healthy"
    else
        echo "❌ $name service is down"
    fi
done
```

## 🔒 安全特性

### 认证授权

- **JWT Token** 认证
- **RBAC** 权限控制
- **API密钥** 管理
- **OAuth2** 集成

### 数据安全

- **端到端加密** (AES-256-GCM)
- **传输加密** (TLS 1.3)
- **数据脱敏** 处理
- **审计日志** 记录

### 访问控制

- **IP白名单** 限制
- **API限流** 保护
- **CORS** 跨域控制
- **防火墙** 规则

## 🚀 性能优化

### 缓存策略

```yaml
缓存层级:
  L1: 内存缓存 (应用级)
  L2: Redis缓存 (分布式)
  L3: CDN缓存 (边缘)

缓存策略:
  算诊结果: 2小时
  图像分析: 30分钟
  音频分析: 1小时
  会话数据: 30分钟
```

### 负载均衡

- **轮询算法** 请求分发
- **健康检查** 自动摘除
- **熔断机制** 故障隔离
- **限流降级** 过载保护

### 数据库优化

- **读写分离** 提升性能
- **分库分表** 水平扩展
- **索引优化** 查询加速
- **连接池** 资源复用

## 📈 扩展部署

### Kubernetes部署

```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: five-diagnosis-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: five-diagnosis
  template:
    spec:
      containers:
      - name: calculation-service
        image: suoke/calculation-service:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

### 云原生特性

- **容器化部署** Docker支持
- **微服务架构** 独立扩展
- **服务网格** Istio集成
- **自动伸缩** HPA/VPA

## 🧪 测试验证

### 单元测试

```bash
# 运行所有服务的单元测试
cd calculation-service && python -m pytest tests/
cd look-service && python -m pytest tests/
cd listen-service && python -m pytest tests/
cd inquiry-service && python -m pytest tests/
cd palpation-service && python -m pytest tests/
```

### 集成测试

```bash
# API集成测试
python tests/integration/test_five_diagnosis_api.py

# 性能测试
python tests/performance/test_load.py

# 端到端测试
python tests/e2e/test_diagnosis_flow.py
```

### 测试覆盖率

```bash
# 生成测试覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term
```

## 🔧 故障排查

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8003
   
   # 检查Docker日志
   docker-compose logs calculation-service
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose exec postgres pg_isready
   
   # 检查连接配置
   echo $POSTGRES_PASSWORD
   ```

3. **Redis连接失败**
   ```bash
   # 检查Redis状态
   docker-compose exec redis redis-cli ping
   
   # 检查密码配置
   docker-compose exec redis redis-cli auth $REDIS_PASSWORD
   ```

### 日志分析

```bash
# 查看实时日志
docker-compose logs -f --tail=100

# 查看特定服务日志
docker-compose logs calculation-service

# 查看错误日志
docker-compose logs | grep ERROR
```

## 📚 API文档

### 统一响应格式

```json
{
  "success": true,
  "data": {
    "diagnosis_id": "diag_123456",
    "patient_id": "patient_123",
    "timestamp": "2024-01-15T10:00:00Z",
    "five_diagnosis_results": {
      "calculation": { /* 算诊结果 */ },
      "look": { /* 望诊结果 */ },
      "listen": { /* 闻诊结果 */ },
      "inquiry": { /* 问诊结果 */ },
      "palpation": { /* 切诊结果 */ }
    },
    "comprehensive_diagnosis": {
      "primary_pattern": "肝郁气滞",
      "confidence_score": 0.85,
      "treatment_principles": ["疏肝理气", "健脾化湿"]
    }
  },
  "message": "五诊分析完成",
  "error_code": null
}
```

### 在线文档

- **算诊服务**: http://localhost:8003/docs
- **望诊服务**: http://localhost:8080/docs
- **闻诊服务**: http://localhost:8000/docs
- **问诊服务**: http://localhost:8001/docs
- **切诊服务**: http://localhost:8002/docs

## 🤝 贡献指南

### 开发环境搭建

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置pre-commit
pre-commit install

# 3. 运行代码检查
ruff check .
mypy .
black .

# 4. 运行测试
pytest
```

### 代码规范

- **Python**: PEP 8 + Black格式化
- **API**: RESTful设计原则
- **文档**: 中英文双语注释
- **测试**: 覆盖率 > 80%

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系我们

- **项目主页**: https://github.com/suoke-life/suoke_life
- **技术文档**: https://docs.suoke.life
- **问题反馈**: https://github.com/suoke-life/suoke_life/issues
- **邮箱**: tech@suoke.life

---

**索克生活五诊系统 - 传统中医智慧与现代AI技术的完美融合** 🌿✨

*让健康管理从被动治疗转向主动预防，实现"治未病"的理想* 🎯 