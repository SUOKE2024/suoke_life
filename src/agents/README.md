# 索克生活四智能体系统

## 概述

索克生活四智能体系统是一个基于人工智能的健康管理平台，由四个独立但协作的智能体组成，每个智能体都有其专门的职责和能力。

## 智能体介绍

### 🤖 小艾 (XiaoaiAgent)

- **角色**: 健康助手 & 首页聊天频道版主
- **专长**: 中医四诊合参、健康分析、语音交互、无障碍服务
- **主要功能**:
  - 智能健康问诊
  - 中医诊断分析
  - 健康数据监测
  - 语音交互支持
  - 无障碍服务

### 🛒 小克 (XiaokeAgent)

- **角色**: SUOKE频道版主
- **专长**: 服务订阅、农产品预制、供应链管理、商业化服务
- **主要功能**:
  - 医生资源匹配
  - 服务推荐
  - 产品管理
  - 供应链管理
  - 预约管理
  - 支付处理

### 📚 老克 (LaokeAgent)

- **角色**: 探索频道版主
- **专长**: 知识传播、培训、博物馆导览、玉米迷宫NPC
- **主要功能**:
  - 中医知识搜索
  - 个性化学习路径
  - 培训课程管理
  - 博物馆导览
  - 专家咨询匹配

### 💝 索儿 (SoerAgent)

- **角色**: LIFE频道版主
- **专长**: 生活健康管理、陪伴服务、数据整合分析
- **主要功能**:
  - 生活方式管理
  - 情感支持
  - 习惯跟踪
  - 智能设备协调
  - 压力管理
  - 危机支持

## 快速开始

### 1. 创建智能体实例

```typescript
import { createAgent } from './index';

// 创建小艾智能体
const xiaoai = await createAgent('xiaoai');
await xiaoai.initialize();

// 创建小克智能体
const xiaoke = await createAgent('xiaoke');
await xiaoke.initialize();

// 创建老克智能体
const laoke = await createAgent('laoke');
await laoke.initialize();

// 创建索儿智能体
const soer = await createAgent('soer');
await soer.initialize();
```

### 2. 基本交互

```typescript
// 与小艾聊天
const response = await xiaoai.processMessage('你好，我想了解我的健康状况', {
  userId: 'user123',
});

// 小克服务推荐
const services = await xiaoke.processMessage('我需要预约医生', {
  userId: 'user123',
});

// 老克知识搜索
const knowledge = await laoke.processMessage('我想学习中医基础知识', {
  userId: 'user123',
});

// 索儿生活管理
const lifestyle = await soer.processMessage('帮我制定健康计划', {
  userId: 'user123',
});
```

### 3. 获取智能体信息

```typescript
// 获取智能体基本信息
console.log(xiaoai.getName()); // "小艾"
console.log(xiaoai.getDescription()); // "健康助手 & 首页聊天频道版主"
console.log(xiaoai.getCapabilities()); // ["chat", "voice_interaction", ...]

// 获取智能体状态
const status = await xiaoai.getHealthStatus();
console.log(status.status); // "healthy"
```

## 智能体协作

四个智能体可以协作处理复杂的用户需求：

```typescript
// 协作场景示例：用户健康咨询
const userQuery = '我最近感觉疲劳，想要全面的健康管理方案';
const userId = 'user123';

// 1. 小艾进行健康分析
const healthAnalysis = await xiaoai.processMessage(userQuery, { userId });

// 2. 小克推荐相关服务
const serviceRecommendation = await xiaoke.processMessage(
  `基于健康分析结果推荐服务: ${JSON.stringify(healthAnalysis.data)}`,
  { userId }
);

// 3. 老克提供知识支持
const knowledgeSupport = await laoke.processMessage(
  '提供关于疲劳管理的中医知识',
  { userId }
);

// 4. 索儿制定生活方式计划
const lifestylePlan = await soer.processMessage('制定改善疲劳的生活方式计划', {
  userId,
});
```

## 测试系统

我们提供了完整的测试套件来验证智能体系统：

```typescript
import { testAllAgents, testAgentCollaboration } from './test-agents';

// 测试所有智能体的基本功能
const basicTest = await testAllAgents();

// 测试智能体协作功能
const collaborationTest = await testAgentCollaboration();
```

### 运行测试

```bash
# 在项目根目录运行
npx ts-node src/agents/test-agents.ts
```

## 智能体能力

### 小艾能力

- `chat` - 聊天对话
- `voice_interaction` - 语音交互
- `four_diagnosis` - 中医四诊
- `health_analysis` - 健康分析
- `accessibility_services` - 无障碍服务
- `constitution_assessment` - 体质评估
- `medical_records` - 医疗记录
- `multilingual_support` - 多语言支持
- `tcm_diagnosis` - 中医诊断
- `intelligent_inquiry` - 智能问诊
- `algorithmic_diagnosis` - 算法诊断

### 小克能力

- `service_recommendation` - 服务推荐
- `doctor_matching` - 医生匹配
- `product_management` - 产品管理
- `supply_chain` - 供应链管理
- `appointment_booking` - 预约管理
- `subscription_management` - 订阅管理
- `agricultural_traceability` - 农产品溯源
- `third_party_integration` - 第三方集成
- `shop_management` - 商店管理
- `payment_processing` - 支付处理
- `logistics_management` - 物流管理

### 老克能力

- `knowledge_management` - 知识管理
- `education` - 教育培训
- `content_curation` - 内容策展
- `game_npc` - 游戏NPC
- `blog_management` - 博客管理
- `learning_paths` - 学习路径
- `tcm_knowledge_rag` - 中医知识RAG
- `community_management` - 社区管理
- `certification_system` - 认证系统
- `content_quality_assurance` - 内容质量保证
- `maze_game_guidance` - 迷宫游戏引导

### 索儿能力

- `lifestyle_management` - 生活方式管理
- `emotional_support` - 情感支持
- `habit_tracking` - 习惯跟踪
- `environmental_sensing` - 环境感知
- `wellness_planning` - 健康规划
- `behavior_intervention` - 行为干预
- `multi_device_integration` - 多设备集成
- `stress_management` - 压力管理
- `companionship` - 陪伴服务
- `crisis_support` - 危机支持

## 系统架构

```
索克生活四智能体系统
├── 小艾 (XiaoaiAgent) - 健康助手
├── 小克 (XiaokeAgent) - 商业服务
├── 老克 (LaokeAgent) - 知识教育
└── 索儿 (SoerAgent) - 生活陪伴

协作模式:
├── 顺序协作 (Sequential)
├── 并行协作 (Parallel)
├── 层次协作 (Hierarchical)
└── 共识协作 (Consensus)
```

## 注意事项

1. **初始化**: 使用智能体前必须先调用 `initialize()` 方法
2. **资源清理**: 使用完毕后应调用 `shutdown()` 方法清理资源
3. **错误处理**: 所有智能体方法都会返回包含 `success` 字段的响应对象
4. **类型安全**: 建议使用 TypeScript 以获得更好的类型安全性

## 开发指南

### 扩展智能体功能

要为智能体添加新功能，请：

1. 在对应的智能体实现类中添加新方法
2. 更新智能体的能力列表
3. 添加相应的测试用例
4. 更新文档

### 添加新的协作模式

要添加新的协作模式，请：

1. 在 `AgentCoordinator` 中定义新的协作策略
2. 实现协作逻辑
3. 添加测试用例
4. 更新文档

## 许可证

本项目遵循 MIT 许可证。详见 LICENSE 文件。
