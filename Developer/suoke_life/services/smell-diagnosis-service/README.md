# 闻诊服务 (Smell Diagnosis Service)

索克生活四诊微服务系统的闻诊组件，负责实现中医闻诊功能，例如气息分析与体味解析。

## 功能概述

闻诊服务提供以下核心功能：

- **气息分析**：分析用户呼吸气体，提取化学特征
- **体味解析**：分析体味特征和化学成分
- **气味数据采集**：通过电子鼻设备采集气味特征数据
- **TCM辨证**：基于闻诊结果，提供中医辨证分析
- **健康建议**：生成基于闻诊结果的健康建议
- **数据持久化**：保存诊断结果到MongoDB数据库
- **历史记录查询**：提供历史诊断记录查询功能
- **四诊协调集成**：与四诊协调服务对接，上报诊断结果
- **API完整性**：提供完整的RESTful API接口

## 技术栈

- Node.js + Express
- TypeScript
- MongoDB (数据存储)
- 电子鼻硬件API
- TensorFlow.js (AI模型)
- Docker & Kubernetes (容器化部署)

## 项目结构

```
smell-diagnosis-service/
├── src/                       # 源代码
│   ├── controllers/           # 控制器
│   │   ├── smell-analysis.controller.ts    # 闻诊控制器
│   │   └── coordinator-webhook.controller.ts # 四诊协调webhook控制器
│   ├── middlewares/           # 中间件
│   ├── models/                # 数据模型
│   │   ├── diagnosis/         # 诊断数据结构
│   │   └── database/          # 数据库模型
│   ├── services/              # 业务逻辑服务
│   │   ├── smell-analysis/    # 闻诊服务
│   │   ├── device-integration/ # 设备集成服务
│   │   └── four-diagnosis-coordinator/ # 四诊协调服务客户端
│   ├── repositories/          # 数据访问层
│   │   └── smell-diagnosis.repository.ts # 闻诊数据存储库
│   ├── routes/                # 路由定义
│   ├── utils/                 # 工具函数
│   ├── interfaces/            # 类型接口定义
│   ├── config/                # 配置文件
│   │   └── database.ts        # 数据库配置
│   └── server.ts              # 服务入口
├── models/                    # AI模型
├── data/                      # 数据存储
│   ├── raw/                   # 原始数据
│   └── results/               # 结果存储
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
- Docker (可选)

### 本地开发

1. 克隆仓库并安装依赖

```bash
git clone <repository-url>
cd smell-diagnosis-service
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
docker build -t smell-diagnosis-service:latest .

# 运行容器
docker run -p 3012:3012 --env-file .env smell-diagnosis-service:latest
```

## API文档

### 闻诊分析API

#### 分析气息

```
POST /api/smell-diagnosis/analyze
```

**请求体**:

```json
{
  "deviceId": "device-123",
  "sessionId": "诊断会话ID",
  "sampleData": {
    "compounds": [
      {"name": "乙醛", "concentration": 0.5},
      {"name": "氨", "concentration": 0.8}
    ],
    "metadata": {
      "sampleTime": "2023-03-15T08:30:00Z",
      "deviceType": "e-nose-v2"
    }
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "diagnosisId": "sd-20230315123456",
    "sessionId": "session-123",
    "timestamp": "2023-03-15T12:34:56Z",
    "features": {
      "compoundProfile": [
        {"name": "乙醛", "concentration": 0.5, "threshold": 0.4},
        {"name": "氨", "concentration": 0.8, "threshold": 0.3}
      ],
      "odorCharacteristics": {
        "intensity": 7,
        "quality": "酸性",
        "hedonics": -2
      }
    },
    "tcmImplications": [
      {
        "pattern": "湿热内蕴",
        "confidence": 0.85
      }
    ],
    "recommendations": [
      "建议清淡饮食，多喝水",
      "可适当食用薏米、绿豆等清热利湿的食物"
    ],
    "metadata": {
      "deviceId": "device-123",
      "sampleTime": "2023-03-15T08:30:00Z"
    }
  }
}
```

#### 获取闻诊历史记录

```
GET /api/smell-diagnosis/history?userId=user123&sessionId=session123&limit=10&offset=0
```

#### 获取特定闻诊记录

```
GET /api/smell-diagnosis/{diagnosisId}
```

### 四诊协调Webhook

```
POST /api/smell-diagnosis/webhook/coordinator
```

**请求头**:

```
X-API-KEY: 您的API密钥
```

**请求体**:

```json
{
  "sessionId": "session123",
  "userId": "user123",
  "requestType": "GET_SMELL_DIAGNOSIS"
}
```

## 存储结构

闻诊服务使用MongoDB存储诊断结果，主要集合包括：

- `smell_diagnoses`: 存储所有闻诊结果

## 与四诊协调服务集成

闻诊服务通过以下方式与四诊协调服务集成：

1. **结果上报**：每次完成闻诊分析后，自动将结果上报到四诊协调服务
2. **Webhook接收**：提供webhook端点接收来自四诊协调服务的请求
3. **综合诊断**：提供获取综合四诊结果的方法

## 故障排除

常见问题及解决方案：

1. **设备连接失败**: 检查电子鼻设备连接状态
2. **采样数据不完整**: 确保采样时间足够长
3. **AI模型加载失败**: 确保模型文件存在于正确路径
4. **数据库连接失败**: 检查MongoDB连接配置
5. **四诊协调服务通信失败**: 检查协调服务URL配置

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