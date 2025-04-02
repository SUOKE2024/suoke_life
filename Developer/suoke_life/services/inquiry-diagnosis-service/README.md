# 索克生活问诊诊断微服务

## 项目简介

问诊诊断微服务是"索克生活"应用的核心微服务之一，负责处理用户的健康咨询、中医问诊和辨证诊断功能。该服务将传统中医四诊（望闻问切）与现代AI技术相结合，提供智能化的中医辨证诊断和个性化的健康调理建议。

## 特性

- **智能问诊**：支持自然语言交互的中医问诊流程
- **中医辨证**：基于症状和四诊数据进行智能辨证分析
- **体质辨识**：分析用户体质类型并提供相应建议
- **健康管理**：记录用户健康数据并提供个性化管理方案
- **知识增强**：集成中医理论知识图谱，提升诊断准确性
- **四诊协调**：与其他微服务协同，整合望诊、闻诊和切诊数据

## 技术栈

- Node.js + TypeScript
- Express.js
- MongoDB
- Docker & Kubernetes
- RabbitMQ / Kafka
- Redis

## 系统要求

- Node.js v16.x 或更高版本
- MongoDB v4.x 或更高版本
- Docker 和 Docker Compose（用于本地开发）
- Kubernetes（用于生产部署）

## 安装与运行

### 使用Docker（推荐）

1. 克隆项目仓库
```bash
git clone https://github.com/suoke-life/inquiry-diagnosis-service.git
cd inquiry-diagnosis-service
```

2. 使用Docker Compose启动服务
```bash
docker-compose up -d
```

### 手动安装

1. 克隆项目仓库
```bash
git clone https://github.com/suoke-life/inquiry-diagnosis-service.git
cd inquiry-diagnosis-service
```

2. 安装依赖
```bash
npm install
```

3. 创建并配置.env文件
```bash
cp .env.example .env
# 编辑.env文件设置正确的环境变量
```

4. 启动服务
```bash
# 开发模式
npm run dev

# 生产模式
npm run build
npm start
```

## API文档

本服务集成了Swagger/OpenAPI文档，提供详细的API参考和交互式测试界面。

### 快速安装Swagger

您可以使用提供的安装脚本快速设置Swagger：

```bash
./install-swagger.sh
```

### 访问API文档

启动服务后，访问以下URL查看API文档：

```
http://localhost:3007/api-docs
```

### API文档特性

- 完整的端点描述和参数说明
- 请求/响应模型和示例
- 交互式API测试功能
- 权限和认证说明
- 错误码和响应格式参考

### 安全性配置

在生产环境中，API文档默认受到基本认证保护。您可以通过环境变量配置：

```
ENABLE_API_DOCS=true
API_DOCS_BASIC_AUTH=true
API_DOCS_USERNAME=your_username
API_DOCS_PASSWORD=your_password
```

### 为API添加文档

文档使用JSDoc风格的注释。示例：

```typescript
/**
 * @swagger
 * /api/resource:
 *   get:
 *     summary: 获取资源列表
 *     tags: [资源]
 *     responses:
 *       200:
 *         description: 成功获取资源列表
 */
```

更多详细信息请参考`docs/API_DOCS_GUIDE.md`和`docs/SWAGGER_ANNOTATION_GUIDE.md`文档。

## 测试

### 运行单元测试
```bash
npm test
```

### 运行集成测试
```bash
npm run test:integration
```

### 运行覆盖率测试
```bash
npm run test:coverage
```

### API测试

您可以使用Swagger UI进行交互式API测试。详细指南请参考`docs/swagger-test.md`文档。

## CI/CD

本项目使用GitHub Actions进行持续集成和部署。每次提交到主分支时，将自动触发以下流程：

1. 代码lint和格式检查
2. 单元测试和集成测试
3. 代码覆盖率分析
4. Docker镜像构建
5. 部署到测试环境

## 贡献指南

请参阅[CONTRIBUTING.md](CONTRIBUTING.md)文件了解贡献流程和代码规范。

## 许可协议

本项目采用MIT许可协议 - 详情请参阅[LICENSE](LICENSE)文件。

## 联系方式

- 项目维护者: 技术团队 <tech@suoke.life>
- 问题报告: [GitHub Issues](https://github.com/suoke-life/inquiry-diagnosis-service/issues)