#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';

// 生成开发工具使用指南
function generateToolsGuide(): void {
  const content = `# 索克生活开发工具使用指南

## 🛠️ 新增开发工具概览

本项目在前端Bug修复过程中新增了多个开发工具，用于提升代码质量和开发效率。

### 1. Logger服务 (\`src/services/Logger.ts\`)

统一的日志管理服务，支持开发/生产环境区分。

#### 使用方法

\`\`\`typescript
import { Logger } from "../services/Logger";

Logger.info("用户登录成功", { userId: 123 });
Logger.warn("网络请求超时", { url: "/api/health" });
Logger.error("数据加载失败", error);

// 调试信息（仅开发环境）
Logger.debug("组件渲染状态", { state });
\`\`\`

#### 特性

- 🔧 开发环境控制台输出
- 📊 生产环境错误监控集成
- 💾 内存日志缓存
- ⏰ 时间戳和堆栈跟踪

### 2. 性能监控Hook (\`src/hooks/usePerformanceMonitor.ts\`)

组件渲染性能监控和内存使用跟踪。

#### 使用方法

\`\`\`typescript
import { usePerformanceMonitor } from "../hooks/usePerformanceMonitor";

function MyComponent() {
  const performanceMonitor = usePerformanceMonitor("MyComponent", {
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms
  });

  // 记录渲染性能
  performanceMonitor.recordRender();

  return <View>...</View>;
}
\`\`\`

#### 特性

- 📊 组件渲染时间监控
- 💾 内存使用情况跟踪
- ⚠️ 性能阈值警告
- 📈 开发环境性能指标记录

### 3. 内存泄漏检测工具 (\`src/utils/memoryLeakDetector.ts\`)

定时器和事件监听器泄漏检测。

#### 使用方法

\`\`\`typescript
import { MemoryLeakDetector } from "../utils/memoryLeakDetector";

// 在应用启动时初始化
MemoryLeakDetector.init();

// 在组件中使用
function MyComponent() {
  useEffect(() => {
    const timer = setInterval(() => {
      // 定时任务
    }, 1000);

    // 自动检测清理
    return () => clearInterval(timer);
  }, []);
}
\`\`\`

#### 特性

- 🔍 自动检测未清理的定时器
- 👂 监听器泄漏检测
- 📊 内存使用统计
- ⚠️ 开发环境警告提示

## 📚 API文档生成

### 自动生成API文档

\`\`\`bash
npm run generate:docs
\`\`\`

### 手动更新文档

\`\`\`bash
npm run docs:update
\`\`\`

## 🧪 测试工具

### 单元测试

\`\`\`bash
npm run test:unit
\`\`\`

### 集成测试

\`\`\`bash
npm run test:integration
\`\`\`

### E2E测试

\`\`\`bash
npm run test:e2e
\`\`\`

## 🚀 部署工具

### 构建生产版本

\`\`\`bash
npm run build:production
\`\`\`

### 部署到测试环境

\`\`\`bash
npm run deploy:staging
\`\`\`

### 部署到生产环境

\`\`\`bash
npm run deploy:production
\`\`\`

## 📊 性能分析

### Bundle分析

\`\`\`bash
npm run analyze:bundle
\`\`\`

### 性能测试

\`\`\`bash
npm run test:performance
\`\`\`

## 🔧 开发工具配置

### ESLint配置

项目使用严格的ESLint规则，确保代码质量：

- TypeScript严格模式
- React Hooks规则
- 无障碍性检查
- 性能优化建议

### Prettier配置

统一的代码格式化规则：

- 2空格缩进
- 单引号字符串
- 尾随逗号
- 分号结尾

### TypeScript配置

严格的类型检查配置：

- 严格模式启用
- 未使用变量检查
- 隐式any检查
- 空值检查

## 🎯 最佳实践

### 组件开发

1. 使用TypeScript接口定义Props
2. 实现性能监控
3. 添加错误边界
4. 编写单元测试

### 状态管理

1. 使用Redux Toolkit
2. 实现持久化存储
3. 添加中间件日志
4. 类型安全的Actions

### 网络请求

1. 统一的API客户端
2. 请求/响应拦截器
3. 错误处理机制
4. 缓存策略

### 性能优化

1. 组件懒加载
2. 图片优化
3. Bundle分割
4. 内存泄漏检测

---

*此文档由开发工具自动生成，最后更新时间：${new Date().toLocaleString()}*
`;

  const outputPath = path.join(process.cwd(), 'docs', 'development-tools-guide.md');
  
  // 确保docs目录存在
  const docsDir = path.dirname(outputPath);
  if (!fs.existsSync(docsDir)) {
    fs.mkdirSync(docsDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, content, 'utf-8');
  console.log(`✅ 开发工具使用指南已生成: ${outputPath}`);
}

// 生成API文档
function generateAPIDocumentation(): void {
  const apiDocs = `# 索克生活 API 文档

## 🌐 API概览

索克生活平台提供RESTful API，支持健康管理、智能诊断、用户管理等功能。

## 🔐 认证

所有API请求需要在请求头中包含JWT令牌：

\`\`\`
Authorization: Bearer <your-jwt-token>
\`\`\`

## 📋 API端点

### 用户管理

#### 用户注册
- **POST** \`/api/auth/register\`
- **描述**: 用户注册
- **请求体**:
  \`\`\`json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "phone": "string"
  }
  \`\`\`

#### 用户登录
- **POST** \`/api/auth/login\`
- **描述**: 用户登录
- **请求体**:
  \`\`\`json
  {
    "email": "string",
    "password": "string"
  }
  \`\`\`

### 健康数据

#### 获取健康档案
- **GET** \`/api/health/profile\`
- **描述**: 获取用户健康档案
- **响应**:
  \`\`\`json
  {
    "id": "string",
    "userId": "string",
    "basicInfo": {
      "height": "number",
      "weight": "number",
      "age": "number",
      "gender": "string"
    },
    "medicalHistory": "array",
    "allergies": "array"
  }
  \`\`\`

#### 上传健康数据
- **POST** \`/api/health/data\`
- **描述**: 上传健康监测数据
- **请求体**:
  \`\`\`json
  {
    "type": "string",
    "value": "number",
    "unit": "string",
    "timestamp": "string"
  }
  \`\`\`

### 智能诊断

#### 症状分析
- **POST** \`/api/diagnosis/symptoms\`
- **描述**: 基于症状进行智能分析
- **请求体**:
  \`\`\`json
  {
    "symptoms": ["string"],
    "duration": "string",
    "severity": "number"
  }
  \`\`\`

#### 获取诊断报告
- **GET** \`/api/diagnosis/report/:id\`
- **描述**: 获取诊断报告详情

### 智能体服务

#### 小艾对话
- **POST** \`/api/agents/xiaoai/chat\`
- **描述**: 与小艾智能体对话
- **请求体**:
  \`\`\`json
  {
    "message": "string",
    "context": "object"
  }
  \`\`\`

#### 小克咨询
- **POST** \`/api/agents/xiaoke/consult\`
- **描述**: 小克健康咨询
- **请求体**:
  \`\`\`json
  {
    "question": "string",
    "category": "string"
  }
  \`\`\`

## 📊 响应格式

### 成功响应
\`\`\`json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
\`\`\`

### 错误响应
\`\`\`json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
\`\`\`

## 🔄 状态码

- **200**: 请求成功
- **201**: 资源创建成功
- **400**: 请求参数错误
- **401**: 未授权访问
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 服务器内部错误

## 📝 使用示例

### JavaScript/TypeScript

\`\`\`typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.suokelife.com',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});

// 获取用户健康档案
const getHealthProfile = async () => {
  try {
    const response = await api.get('/api/health/profile');
    return response.data;
  } catch (error) {
    console.error('获取健康档案失败:', error);
  }
};
\`\`\`

### Python

\`\`\`python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 获取用户健康档案
response = requests.get(
    'https://api.suokelife.com/api/health/profile',
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(data)
\`\`\`

---

*此文档自动生成，最后更新时间：${new Date().toLocaleString()}*
`;

  const apiDocsPath = path.join(process.cwd(), 'docs', 'api-documentation.md');
  fs.writeFileSync(apiDocsPath, apiDocs, 'utf-8');
  console.log(`✅ API文档已生成: ${apiDocsPath}`);
}

// 主函数
function main(): void {
  console.log('📚 开始生成项目文档...');
  
  try {
    generateToolsGuide();
    generateAPIDocumentation();
    
    console.log('🎉 所有文档生成完成！');
  } catch (error) {
    console.error('❌ 文档生成失败:', error);
    process.exit(1);
  }
}

// 检查是否为直接执行
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { generateToolsGuide, generateAPIDocumentation };