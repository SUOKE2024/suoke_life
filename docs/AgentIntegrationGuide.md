# 智能体服务集成指南

## 概述

本指南详细介绍了索克生活（Suoke Life）平台中四个智能体服务的集成方案，包括API接口、使用方法和最佳实践。

## 智能体服务架构

### 四大智能体
1. **小艾 (Xiaoai)** - 四诊协调智能体，负责中医四诊（望、闻、问、切）数据的协调和诊断分析
2. **小克 (Xiaoke)** - 医疗资源调度智能体，负责医疗资源调度、产品推荐和订单管理
3. **老克 (Laoke)** - 教育知识传播智能体，负责健康教育、知识传播和社区互动
4. **索儿 (Soer)** - 生活方式管理智能体，负责个性化健康计划、营养管理和生活方式优化

### 服务端口配置
```typescript
export const AGENT_SERVICE_PORTS = {
  xiaoai: 50051,  // 小艾服务 - 四诊协调
  xiaoke: 9083,   // 小克服务 - 资源调度
  laoke: 8080,    // 老克服务 - 知识传播
  soer: 8054      // 索儿服务 - 生活管理
};
```

## API客户端集成

### 1. 小艾服务 (xiaoaiApi)

#### 主要功能
- 诊断会话管理
- 多模态输入处理
- 健康记录查询
- 健康建议生成

#### 核心API方法
```typescript
// 创建诊断会话
const session = await xiaoaiApi.createDiagnosisSession({
  user_id: 'user123',
  session_type: 'comprehensive',
  initial_symptoms: ['头痛', '失眠']
});

// 多模态诊断输入
await xiaoaiApi.processMultimodalInput('session123', {
  modality_type: 'image',
  data: base64ImageData,
  metadata: { body_part: 'tongue' }
});

// 获取诊断分析
const analysis = await xiaoaiApi.getDiagnosisAnalysis('session123');
```

### 2. 小克服务 (xiaokeApi)

#### 主要功能
- 医疗资源调度
- 产品定制和推荐
- 订单管理
- 支付处理

#### 核心API方法
```typescript
// 资源调度
await xiaokeApi.scheduleResources({
  user_id: 'user123',
  resource_type: 'doctor_appointment',
  requirements: { specialty: '中医科', date: '2024-01-15' }
});

// 产品推荐
const products = await xiaokeApi.recommendProducts({
  user_id: 'user123',
  category: 'health_supplements',
  constitution_type: '阳虚质'
});

// 生成饮食计划
const dietPlan = await xiaokeApi.generateDietPlan({
  user_id: 'user123',
  constitution_type: '平和质',
  health_goals: ['减重', '改善睡眠']
});
```

### 3. 老克服务 (laokeApi)

#### 主要功能
- 知识文章管理
- 学习路径推荐
- 社区互动
- NPC交互

#### 核心API方法
```typescript
// 获取知识文章
const articles = await laokeApi.getKnowledgeArticles({
  category: '中医基础',
  difficulty_level: 'beginner',
  limit: 10
});

// 获取个性化学习路径
const learningPaths = await laokeApi.getPersonalizedLearningPaths({
  user_id: 'user123',
  interests: ['中医理论', '养生方法'],
  current_level: 'intermediate'
});

// 智能体交互
const response = await laokeApi.agentInteraction({
  user_id: 'user123',
  message: '请介绍一下五行理论',
  context: { session_id: 'chat123' }
});
```

### 4. 索儿服务 (soerApi)

#### 主要功能
- 健康计划生成
- 营养摄入跟踪
- 传感器数据分析
- 情绪状态分析

#### 核心API方法
```typescript
// 生成健康计划
const healthPlan = await soerApi.generateHealthPlan({
  user_id: 'user123',
  constitution_type: '平和质',
  health_goals: ['改善睡眠', '增强体质'],
  preferences: {
    exercise: ['瑜伽', '太极'],
    diet: ['清淡', '温补']
  },
  current_season: '春季'
});

// 跟踪营养摄入
const nutritionAnalysis = await soerApi.trackNutrition('user123', {
  user_id: 'user123',
  food_entries: [{
    food_name: '苹果',
    quantity: 1,
    unit: '个',
    timestamp: new Date().toISOString()
  }],
  analysis_type: 'daily'
});

// 分析传感器数据
const sensorAnalysis = await soerApi.analyzeSensorData('user123', {
  user_id: 'user123',
  data: [{
    sensor_type: 'heart_rate',
    device_id: 'apple_watch_001',
    data_points: [{
      timestamp: new Date().toISOString(),
      values: { bpm: 72 }
    }]
  }]
});
```

## 错误处理和重试机制

### 统一错误处理
```typescript
try {
  const result = await xiaoaiApi.createDiagnosisSession(data);
  return result;
} catch (error) {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.detail || '服务请求失败';
    throw new Error(message);
  }
  throw error;
}
```

### 网络重试配置
所有API客户端都配置了：
- 请求超时：30秒
- 自动重试：3次
- 指数退避策略

## 集成测试

### 运行集成测试
```typescript
import { runAgentIntegrationTest } from '../utils/agentIntegrationTest';

// 运行完整集成测试
const report = await runAgentIntegrationTest();

// 快速健康检查
const isHealthy = await quickHealthCheck();
```

### 测试用例
1. **连接测试** - 验证所有服务的健康状态
2. **基本功能测试** - 测试核心API方法
3. **性能测试** - 测量响应时间
4. **错误处理测试** - 验证错误场景处理

## 最佳实践

### 1. 服务调用顺序
建议的智能体调用流程：
1. 小艾：创建诊断会话，收集健康数据
2. 老克：提供相关健康知识和教育内容
3. 小克：推荐相应的医疗资源和产品
4. 索儿：生成个性化的健康管理计划

### 2. 数据类型一致性
- 使用 snake_case 格式与后端Python服务保持一致
- 时间戳统一使用ISO 8601格式
- 文件上传使用Base64编码

### 3. 状态管理
```typescript
// 使用React Context管理智能体状态
const AgentContext = createContext({
  xiaoaiSession: null,
  healthPlan: null,
  learningProgress: null,
  // ...
});
```

### 4. 缓存策略
- 诊断会话：本地存储，7天过期
- 健康计划：内存缓存，24小时过期
- 知识文章：本地存储，30天过期

## 安全考虑

### 1. 数据加密
- 所有敏感健康数据传输使用HTTPS
- 本地存储的健康数据进行加密
- 用户认证令牌定期刷新

### 2. 隐私保护
- 遵循最小数据原则
- 支持数据删除请求
- 用户数据匿名化处理

## 性能优化

### 1. 并发请求
```typescript
// 并行调用多个智能体服务
const [healthStatus, knowledgeArticles, recommendations] = await Promise.all([
  xiaoaiApi.healthCheck(),
  laokeApi.getKnowledgeArticles(params),
  xiaokeApi.recommendProducts(params)
]);
```

### 2. 请求去重
- 实现请求缓存机制
- 避免重复API调用
- 使用请求合并策略

## 监控和日志

### 1. 服务监控
```typescript
// 定期健康检查
setInterval(async () => {
  const isHealthy = await quickHealthCheck();
  if (!isHealthy) {
    // 发送告警通知
    console.error('智能体服务异常');
  }
}, 60000); // 每分钟检查一次
```

### 2. 请求日志
- 记录所有API请求和响应
- 监控响应时间和错误率
- 性能指标收集和分析

## 部署配置

### 开发环境
```yaml
services:
  xiaoai:
    image: suoke/xiaoai-service:latest
    ports:
      - "50051:50051"
  xiaoke:
    image: suoke/xiaoke-service:latest
    ports:
      - "9083:9083"
  laoke:
    image: suoke/laoke-service:latest
    ports:
      - "8080:8080"
  soer:
    image: suoke/soer-service:latest
    ports:
      - "8054:8054"
```

### 生产环境
- 使用负载均衡器分发请求
- 配置服务发现机制
- 实施容器编排和自动扩缩容

## 故障排除

### 常见问题
1. **连接超时** - 检查网络配置和防火墙设置
2. **认证失败** - 验证API密钥和用户权限
3. **数据格式错误** - 确认请求参数格式正确
4. **服务不可用** - 检查服务运行状态和资源占用

### 调试工具
- 使用浏览器开发者工具查看网络请求
- 查看服务日志文件
- 使用Postman测试API接口

## 版本兼容性

当前支持的API版本：
- 小艾服务：v1.0
- 小克服务：v1.0
- 老克服务：v1.0
- 索儿服务：v1.0

## 更新历史

### v1.0.0 (2025-05-23)
- 初始版本发布
- 完成四个智能体服务的基础集成
- 实现API客户端和错误处理机制
- 添加集成测试工具

## 支持和反馈

如有问题或建议，请通过以下方式联系：
- 技术支持邮箱：tech-support@suoke.life
- 开发者文档：https://docs.suoke.life
- GitHub Issues：https://github.com/suoke-life/frontend/issues