# 玉米迷宫服务 (Corn Maze Service)

玉米迷宫寻宝游戏微服务 - 索克生活APP的核心组件之一。该服务提供玉米迷宫探索、AR宝藏收集和团队协作功能。

## 📋 功能概述

- **迷宫管理**：创建、查询和自动生成迷宫
- **宝藏系统**：宝藏管理、AR互动和奖励机制
- **植物生长**：玉米种植、生长周期管理
- **团队协作**：团队管理、成员互动、排行榜
- **多模式AR互动**：图像识别、地理位置探索、手势互动、实时AR留言
- **老克NPC互动**：智能引导、知识问答、任务发布、农事指导

## 🛠️ 技术栈

- **后端框架**：Express (Node.js)
- **数据库**：MongoDB (Mongoose ORM)
- **实时通信**：Socket.io
- **图像处理**：Sharp
- **文件上传**：Multer
- **认证机制**：JWT
- **日志**：Winston
- **NPC引擎**：基于知识图谱的对话系统

## 🚀 快速开始

### 前置条件

- Node.js 14+
- MongoDB 4.4+
- npm 6+

### 安装

1. 克隆仓库
```bash
git clone <repository-url>
cd services/corn-maze-service
```

2. 安装依赖
```bash
npm install
```

3. 创建环境配置
```bash
cp .env.example .env
```
编辑`.env`文件，设置必要的环境变量。

4. 启动服务
```bash
# 开发模式
npm run dev

# 生产模式
npm start
```

### 构建与部署

```bash
# 构建项目
npm run build

# 编译后的文件在dist/目录
```

## 📚 API文档

API文档可通过以下方式访问：

- 本地开发: http://localhost:3000/public/docs
- 线上环境: https://api.suoke.life/corn-maze/docs

## 🌟 AR增强功能

### 多模式AR识别

服务支持多种AR识别模式：

1. **基于标记的识别**：传统AR标记扫描
2. **图像识别**：基于机器学习的图像内容识别
3. **地理位置发现**：基于GPS/定位的宝藏发现
4. **手势互动**：通过特定手势与AR内容互动
5. **环境感知**：利用深度相机进行空间映射和障碍识别

### API端点

| 路径 | 方法 | 描述 |
|------|------|------|
| `/api/ar/scan/image` | POST | 图像识别扫描 |
| `/api/ar/discover/location` | GET | 地理位置发现宝藏 |
| `/api/ar/treasures/:id/collect/gesture` | POST | 手势互动收集宝藏 |
| `/api/ar/teams/:teamId/hunt/:mazeId` | POST | 启动团队同步寻宝 |
| `/api/ar/treasures/:id/share` | POST | 分享宝藏给其他用户 |
| `/api/ar/messages` | GET | 获取附近AR留言 |
| `/api/ar/messages` | POST | 创建AR留言 |
| `/api/ar/npc/interact` | POST | 与老克NPC进行互动 |
| `/api/ar/environment/scan` | POST | 提交环境扫描数据 |
| `/api/ar/demo/:dataType` | POST | 加载演示数据(仅管理员) |

### 集成指南

Flutter集成文档位于 `docs/ar-flutter-integration.md`。

### 实时功能

通过WebSocket支持以下实时功能：

- 团队寻宝同步
- 实时位置共享
- 宝藏发现通知
- AR留言推送
- NPC实时对话
- 环境数据同步

## 🧠 老克NPC系统

### 功能概述

老克是玉米迷宫中的虚拟向导，提供：

- **知识问答**：回答有关玉米种植、农业知识的问题
- **任务发布**：分配与玉米迷宫相关的任务和挑战
- **故事讲述**：分享玉米文化和索克生活理念
- **农事指导**：根据实时环境数据提供农作物管理建议

### 交互方式

- **文本对话**：基于自然语言处理的文本交流
- **语音互动**：支持语音识别和合成的对话体验
- **AR投影**：在物理迷宫中投影老克的虚拟形象
- **手势识别**：通过手势启动特定对话主题

### 集成服务

老克NPC系统集成了以下服务：

- **知识图谱服务**：提供结构化农业知识
- **对话管理服务**：处理多轮对话逻辑
- **任务管理系统**：跟踪用户任务完成情况

## 🔄 数据模型

### 核心数据模型

- **Maze**: 迷宫结构与属性
- **Treasure**: 宝藏定义、奖励和AR交互
- **Plant**: 玉米植物生长状态
- **Team**: 团队组织与成员管理
- **ARMessage**: AR留言系统
- **NPCInteraction**: NPC交互历史与状态
- **Quest**: 任务定义与进度跟踪

## 👥 贡献指南

请参阅 `CONTRIBUTING.md` 了解如何为项目做出贡献。

## 📄 许可证

本项目为索克生活APP的私有组件，未经授权不得使用或分发。

## 🔗 相关资源

- [Flutter前端仓库](#)
- [主API网关](#)
- [项目文档库](#)

## 📞 联系方式

有问题或建议？请联系项目维护者：
- 技术支持: tech@suoke.life
- 项目管理: pm@suoke.life
