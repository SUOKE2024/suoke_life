# 触诊服务 (Touch Diagnosis Service)

本服务是索克生活四诊系统的组成部分，负责处理切诊（触诊）相关的功能，包括脉诊和腹诊数据的收集、存储和分析。

## 功能特点

- 脉诊数据收集和分析，支持多种脉象类型
- 腹诊数据收集和分析，支持多种腹诊发现类型
- 触诊数据整合分析
- 触诊历史记录查询
- 与四诊协调服务集成，支持四诊合参

## 技术栈

- Node.js
- Express
- TypeScript
- RESTful API

## 安装与运行

### 环境要求

- Node.js 16.x 或更高版本
- npm 7.x 或更高版本

### 安装依赖

```bash
npm install
```

### 配置环境变量

复制环境变量示例文件，并根据您的环境进行配置：

```bash
cp .env.example .env
```

### 构建项目

```bash
npm run build
```

### 启动服务

```bash
npm start
```

开发模式启动（支持热重载）：

```bash
npm run dev
```

## API 文档

### 脉诊相关接口

- `POST /api/touch-diagnosis/pulse` - 提交脉诊数据
- `GET /api/touch-diagnosis/:patientId` - 获取患者的触诊记录
- `GET /api/touch-diagnosis/:patientId/history` - 获取患者的触诊历史记录

### 腹诊相关接口

- `POST /api/touch-diagnosis/abdominal` - 提交腹诊数据

### 分析相关接口

- `POST /api/touch-diagnosis/analyze` - 分析触诊数据并生成结论

## 测试

```bash
npm test
```

## 许可证

© 2023 索克生活，保留所有权利。