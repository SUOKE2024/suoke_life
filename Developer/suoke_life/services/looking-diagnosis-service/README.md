# 望诊服务 (Looking Diagnosis Service)

索克生活四诊微服务系统的望诊组件，负责实现中医望诊功能，特别是舌诊和面诊分析。

## 功能概述

望诊服务提供以下核心功能：

- **舌象分析**：处理舌头图像，识别舌质、舌苔、舌体形态等特征
- **面象分析**：分析面部特征，包括面色、表情等
- **体态分析**：分析人体体态，提供姿势相关诊断
- **TCM辨证**：基于望诊结果，提供中医辨证分析
- **健康建议**：生成基于望诊结果的健康建议
- **数据持久化**：保存诊断结果到MongoDB数据库
- **历史记录查询**：提供历史诊断记录查询功能
- **四诊协调集成**：与四诊协调服务对接，上报诊断结果
- **API完整性**：提供完整的RESTful API接口

## 技术栈

- Node.js + Express
- TypeScript
- MongoDB (数据存储)
- Sharp (图像处理)
- TensorFlow.js (AI模型)
- Docker & Kubernetes (容器化部署)

## 项目结构

```
looking-diagnosis-service/
├── src/                        # 源代码
│   ├── controllers/            # 控制器
│   │   ├── face-analysis.controller.ts       # 面诊控制器
│   │   ├── tongue-diagnosis.controller.ts    # 舌诊控制器
│   │   └── coordinator-webhook.controller.ts # 四诊协调webhook控制器
│   ├── middlewares/            # 中间件
│   ├── models/                 # 数据模型
│   │   ├── diagnosis/          # 诊断数据结构
│   │   └── database/           # 数据库模型
│   ├── services/               # 业务逻辑服务
│   │   ├── image-processing/   # 图像处理服务
│   │   ├── tongue-diagnosis/   # 舌诊服务
│   │   ├── face-analysis/      # 面诊服务
│   │   └── four-diagnosis-coordinator/ # 四诊协调服务客户端
│   ├── repositories/           # 数据访问层
│   │   ├── tongue-diagnosis.repository.ts # 舌诊数据存储库
│   │   └── face-diagnosis.repository.ts   # 面诊数据存储库
│   ├── routes/                 # 路由定义
│   ├── utils/                  # 工具函数
│   ├── interfaces/             # 类型接口定义
│   ├── config/                 # 配置文件
│   │   └── database.ts         # 数据库配置
│   └── server.ts               # 服务入口
├── models/                     # AI模型
├── data/                       # 数据存储
│   ├── images/                 # 图像存储
│   └── results/                # 结果存储
├── tests/                      # 测试代码
├── dist/                       # 编译输出
├── .env                        # 环境变量
├── .env.example                # 环境变量示例
├── Dockerfile                  # Docker构建文件
├── docker-compose.yml          # Docker Compose配置
├── package.json                # 项目依赖
└── tsconfig.json               # TypeScript配置
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
cd looking-diagnosis-service
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
docker build -t looking-diagnosis-service:latest .

# 运行容器
docker run -p 3011:3011 --env-file .env looking-diagnosis-service:latest
```

## API文档

### 舌诊分析API

#### 分析舌象

```
POST /api/looking-diagnosis/tongue
```

**请求体**:

```json
{
  "imageBase64": "base64编码的图像数据",
  "sessionId": "诊断会话ID",
  "metadata": {
    "captureTime": "2023-03-15T08:30:00Z",
    "lightingCondition": "自然光"
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "diagnosisId": "ld-tongue-1678940400000",
    "sessionId": "session-123",
    "timestamp": "2023-03-16T08:30:00Z",
    "features": {
      "tongueColor": "淡红",
      "tongueShape": "正常",
      "tongueCoating": "薄白",
      "moisture": "适中",
      "cracks": false,
      "spots": false,
      "teethMarks": false,
      "deviation": false
    },
    "tcmImplications": [
      {
        "concept": "正常",
        "confidence": 0.9
      }
    ],
    "recommendations": [
      "您的舌象表现正常，继续保持良好的生活习惯。",
      "建议保持规律作息，合理饮食。"
    ],
    "metadata": {
      "captureTime": "2023-03-15T08:30:00Z",
      "lightingCondition": "自然光",
      "processingSteps": [
        "图像预处理",
        "舌头区域提取",
        "图像增强",
        "特征提取",
        "TCM辨证分析",
        "建议生成"
      ]
    }
  }
}
```

#### 获取舌诊历史记录

```
GET /api/looking-diagnosis/tongue/history?userId=user123&sessionId=session123&limit=10&offset=0
```

#### 获取特定舌诊记录

```
GET /api/looking-diagnosis/tongue/{diagnosisId}
```

### 面诊分析API

#### 分析面色

```
POST /api/looking-diagnosis/face
```

**请求体**:

```json
{
  "imageBase64": "base64编码的图像数据",
  "sessionId": "诊断会话ID",
  "metadata": {
    "captureTime": "2023-03-15T08:30:00Z",
    "lightingCondition": "自然光"
  }
}
```

#### 获取面诊历史记录

```
GET /api/looking-diagnosis/face/history?userId=user123&sessionId=session123&limit=10&offset=0
```

#### 获取特定面诊记录

```
GET /api/looking-diagnosis/face/{diagnosisId}
```

### 体态分析API

#### 分析体态

```
POST /api/looking-diagnosis/posture
```

**请求体**:

```json
{
  "imageBase64": "base64编码的图像数据",
  "sessionId": "诊断会话ID",
  "userId": "用户ID（可选）",
  "metadata": {
    "captureTime": "2023-03-15T08:30:00Z",
    "lightingCondition": "自然光"
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "diagnosisId": "ld-posture-1678940400000",
    "sessionId": "session-123",
    "timestamp": "2023-03-16T08:30:00Z",
    "features": {
      "overallPosture": "略前倾",
      "shoulderAlignment": "左高",
      "spineAlignment": "左侧弯曲",
      "hipAlignment": "对称",
      "hasForwardHeadPosture": true,
      "hasRoundedShoulders": true,
      "hasSwaybBack": false,
      "hasFlatBack": false,
      "posturalDeviation": 4,
      "comments": "存在轻度姿态异常，主要表现为头部前倾和圆肩。"
    },
    "tcmImplications": [
      {
        "concept": "气虚体质",
        "confidence": 0.85,
        "explanation": "肩部前倾(圆肩)往往与气虚体质相关，表现为精神不振、易疲劳。"
      },
      {
        "concept": "肝郁气滞",
        "confidence": 0.7,
        "explanation": "头部前倾姿势可能与肝郁气滞相关，常见颈肩部紧张不适。"
      }
    ],
    "recommendations": [
      "保持良好姿势，注意站立和坐姿的正确性。",
      "定期进行体态评估，跟踪姿势变化。",
      "注意头部姿势，避免长时间低头看手机或电脑，建议每工作一小时休息5-10分钟。",
      "可以尝试颈部后伸运动，每天3-5次，每次保持10秒。",
      "加强背部肌肉锻炼，如划船运动、俯卧撑等。",
      "建议适量参加有氧运动，如太极、慢跑等，增强体质。"
    ],
    "metadata": {
      "captureTime": "2023-03-15T08:30:00Z",
      "lightingCondition": "自然光",
      "processingSteps": [
        "图像预处理",
        "体态特征提取",
        "TCM辨证分析",
        "建议生成"
      ]
    }
  }
}
```

#### 获取体态分析历史记录

```
GET /api/looking-diagnosis/posture/history?userId=user123&sessionId=session123&limit=10&offset=0
```

#### 获取特定体态分析记录

```
GET /api/looking-diagnosis/posture/{diagnosisId}
```

### 四诊协调Webhook

```
POST /api/looking-diagnosis/webhook/coordinator
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
  "requestType": "GET_TONGUE_DIAGNOSIS"
}
```

## 存储结构

望诊服务使用MongoDB存储诊断结果，主要集合包括：

- `tongue_diagnoses`: 存储所有舌诊结果
- `face_diagnoses`: 存储所有面诊结果

## 与四诊协调服务集成

望诊服务通过以下方式与四诊协调服务集成：

1. **结果上报**：每次完成舌诊或面诊分析后，自动将结果上报到四诊协调服务
2. **Webhook接收**：提供webhook端点接收来自四诊协调服务的请求
3. **综合诊断**：提供获取综合四诊结果的方法

## 故障排除

常见问题及解决方案：

1. **图像处理失败**: 确保上传的图像清晰且格式正确
2. **服务连接超时**: 检查网络连接和服务状态
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