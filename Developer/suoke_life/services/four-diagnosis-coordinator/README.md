# 四诊协调服务 (Four Diagnosis Coordinator)

索克生活四诊体系的核心协调服务，负责集成望闻问切四诊数据，生成综合诊断结果。

## 功能概述

四诊协调服务提供以下核心功能：

- **数据集成**：整合来自望、闻、问、切四诊微服务的诊断数据
- **诊断协调**：基于四诊数据进行综合分析与协调
- **权重动态调整**：根据数据质量和可用性动态调整各诊法权重
- **综合辨证**：生成基于多源数据的综合中医辨证结果
- **健康方案生成**：基于综合辨证结果提供健康调理方案
- **微服务协调**：管理四诊微服务之间的通信和数据流
- **数据持久化**：保存诊断结果到MongoDB数据库
- **历史记录查询**：提供历史诊断记录查询功能
- **API完整性**：提供完整的RESTful API接口

## 技术栈

- Node.js + Express
- TypeScript
- MongoDB (数据存储)
- Redis (缓存和消息队列)
- TensorFlow.js (AI推理)
- Docker & Kubernetes (容器化部署)

## 项目结构

```
four-diagnosis-coordinator/
├── src/                       # 源代码
│   ├── controllers/           # 控制器
│   │   ├── coordinator.controller.ts    # 协调器控制器
│   │   └── webhook.controller.ts        # 微服务回调控制器
│   ├── middlewares/           # 中间件
│   ├── models/                # 数据模型
│   │   ├── diagnosis/         # 诊断数据结构
│   │   └── database/          # 数据库模型
│   ├── services/              # 业务逻辑服务
│   │   ├── coordinator/       # 协调服务
│   │   ├── integration/       # 四诊集成服务
│   │   ├── looking/           # 望诊集成服务
│   │   ├── smelling/          # 闻诊集成服务
│   │   ├── inquiry/           # 问诊集成服务
│   │   └── palpation/         # 切诊集成服务
│   ├── repositories/          # 数据访问层
│   ├── routes/                # 路由定义
│   ├── utils/                 # 工具函数
│   ├── interfaces/            # 类型接口定义
│   ├── config/                # 配置文件
│   │   └── database.ts        # 数据库配置
│   └── server.ts              # 服务入口
├── models/                    # AI模型
├── data/                      # 数据存储
├── tests/                     # 测试代码
├── dist/                      # 编译输出
├── .env                       # 环境变量
├── .env.example               # 环境变量示例
├── Dockerfile                 # Docker构建文件
├── docker-compose.yml         # Docker Compose配置
├── package.json               # 项目依赖
└── tsconfig.json              # TypeScript配置
```

## 安装与运行

### 前置条件

- Node.js v14.0+
- MongoDB
- Redis
- Docker (可选)

### 本地开发

1. 克隆仓库并安装依赖

```bash
git clone <repository-url>
cd four-diagnosis-coordinator
npm install
```

2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件设置必要的环境变量
```

3. 启动服务

```bash
# 开发模式
npm run dev

# 生产模式
npm run build
npm start
```

### Docker部署

```bash
# 构建镜像
docker build -t four-diagnosis-coordinator:latest .

# 运行容器
docker run -p 3010:3010 --env-file .env four-diagnosis-coordinator:latest
```

## API文档

### 诊断会话API

#### 创建诊断会话

```
POST /api/coordinator/sessions
```

**请求体**:

```json
{
  "userId": "user123",
  "metadata": {
    "age": 35,
    "gender": "female",
    "chiefComplaint": "头痛、失眠、易怒"
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "sessionId": "session-123456",
    "userId": "user123",
    "createdAt": "2023-03-15T08:30:00Z",
    "status": "active",
    "metadata": {
      "age": 35,
      "gender": "female",
      "chiefComplaint": "头痛、失眠、易怒"
    }
  }
}
```

#### 获取综合诊断结果

```
GET /api/coordinator/sessions/{sessionId}/diagnosis
```

**响应**:

```json
{
  "success": true,
  "data": {
    "sessionId": "session-123456",
    "userId": "user123",
    "timestamp": "2023-03-15T12:34:56Z",
    "status": "completed",
    "diagnosisComponents": {
      "looking": {
        "available": true,
        "diagnosisId": "ld-123456",
        "confidence": 0.85,
        "patterns": ["肝郁化火", "心肝血虚"]
      },
      "smelling": {
        "available": false
      },
      "inquiry": {
        "available": true,
        "diagnosisId": "id-123456",
        "confidence": 0.92,
        "patterns": ["肝郁气滞", "心肝血虚"]
      },
      "palpation": {
        "available": true,
        "diagnosisId": "pd-123456",
        "confidence": 0.78,
        "patterns": ["肝郁气滞", "肝阳上亢"]
      }
    },
    "integratedDiagnosis": {
      "primaryPattern": "肝郁气滞",
      "secondaryPatterns": ["肝阳上亢", "心肝血虚"],
      "confidence": 0.88,
      "description": "肝郁气滞导致肝阳上亢，同时伴有心肝血虚证",
      "reasoning": "舌质紫暗、脉弦、情绪波动大，且伴有头痛、失眠、易怒等症状，综合分析为肝郁气滞为主证"
    },
    "recommendations": {
      "lifestyle": [
        "保持情绪舒畅，避免过度紧张和压力",
        "规律作息，避免熬夜"
      ],
      "diet": [
        "宜食用菊花、玫瑰花、薄荷等疏肝理气食材",
        "避免辛辣刺激性食物和酒类"
      ],
      "remedies": [
        "可服用逍遥丸或柴胡疏肝散调理",
        "针灸建议取太冲、合谷、百会等穴位"
      ]
    },
    "metadata": {
      "diagnosisMethod": "四诊合参",
      "algorithmVersion": "1.2.3",
      "weightDistribution": {
        "looking": 0.3,
        "smelling": 0.0,
        "inquiry": 0.4,
        "palpation": 0.3
      }
    }
  }
}
```

#### 获取诊断历史记录

```
GET /api/coordinator/users/{userId}/sessions?limit=10&offset=0
```

### 微服务调用API

#### 提交诊断结果

```
POST /api/coordinator/results/{diagnosisType}
```

**请求头**:

```
X-API-KEY: 您的API密钥
```

**请求体**:

```json
{
  "sessionId": "session-123456",
  "userId": "user123",
  "diagnosisId": "ld-123456",
  "diagnosisType": "looking",
  "patterns": ["肝郁化火", "心肝血虚"],
  "confidence": 0.85,
  "rawData": { ... }  // 原始诊断数据
}
```

## 微服务通信流程

协调服务与各诊断服务的通信流程如下：

1. **结果推送模式**：各诊断服务完成诊断后，主动将结果推送至协调服务
2. **结果拉取模式**：协调服务通过API调用主动从各诊断服务拉取结果
3. **Webhook模式**：协调服务通过webhook向各诊断服务请求数据

## 综合诊断算法

综合诊断使用以下策略：

1. **加权平均法**：根据各诊法可信度分配权重
2. **证型频率分析**：分析各诊法中共同出现的证型
3. **模式匹配算法**：将症状组合与标准证型模式匹配
4. **置信度阈值**：设置最低置信度要求，低于阈值的诊断被降权或忽略
5. **冲突解决策略**：处理不同诊法产生的矛盾结果

## 安全与认证

协调服务使用以下安全措施：

1. **API密钥认证**：所有微服务通信必须使用API密钥
2. **JWT用户认证**：用户访问需要JWT token
3. **HTTPS加密**：所有API通信使用HTTPS加密
4. **IP白名单**：限制可访问微服务API的IP地址

## 故障排除

常见问题及解决方案：

1. **微服务通信失败**: 检查API密钥和网络连接
2. **数据整合错误**: 检查数据格式是否符合协议
3. **Redis连接问题**: 检查Redis服务配置
4. **MongoDB连接失败**: 检查MongoDB连接配置
5. **算法模型加载失败**: 确保模型文件存在于正确路径

## 开发与贡献

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE)

## 联系方式

索克生活团队 - info@suoke.life 