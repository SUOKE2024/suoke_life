# 问诊服务 (Inquiry Service)

## 概述

问诊服务是索克生活（Suoke Life）平台的核心诊断服务之一，负责通过智能对话收集用户的健康信息，提取症状，进行中医证型匹配，并评估健康风险。

## 服务架构

### 核心模块

1. **对话管理器 (DialogueManager)**
   - 管理问诊会话的生命周期
   - 处理用户交互
   - 生成智能回复和跟进问题

2. **症状提取器 (SymptomExtractor)**
   - 从用户文本中提取症状信息
   - 识别症状严重程度和持续时间
   - 检测否定词和上下文信息
   - 支持与知识库集成的增强提取

3. **中医证型映射器 (TCMPatternMapper)**
   - 将症状映射到中医证型
   - 考虑用户体质类型
   - 计算证型匹配度

4. **健康风险评估器 (HealthRiskAssessor)**
   - 基于症状、病史和体质评估健康风险
   - 区分即时风险和长期风险
   - 生成个性化预防策略

5. **中医知识库 (TCMKnowledgeBase)**
   - 管理证型、症状、映射关系等中医知识
   - 支持症状验证和模糊匹配
   - 提供治疗建议和体质调理策略

## API接口

### 1. StartInquirySession
开始新的问诊会话

### 2. InteractWithUser
处理用户交互，返回AI响应

### 3. EndInquirySession
结束会话并生成问诊总结

### 4. ExtractSymptoms
从文本中提取症状信息

### 5. MapToTCMPatterns
将症状映射到中医证型

### 6. AssessHealthRisks
评估健康风险并生成预防策略

### 7. AnalyzeMedicalHistory
分析用户病史信息

### 8. BatchAnalyzeInquiryData
批量分析问诊数据

## 快速开始

### 环境要求
- Python 3.13.3+
- UV (现代 Python 包管理器)
- gRPC

### 安装依赖

#### 使用 UV (推荐)
```bash
# 安装生产依赖
uv sync --no-dev

# 安装开发依赖
uv sync --dev
```

#### 使用 Make (简化操作)
```bash
# 开发环境设置
make dev-setup

# 或分步安装
make dev-install
make pre-commit-install
```

### 启动服务

1. 使用启动脚本：
```bash
python3 start_server.py
```

2. 使用 Make：
```bash
make run
```

3. 开发模式（自动重载）：
```bash
make dev-run
```

### 运行测试

```bash
# 使用 Make
make test

# 带覆盖率报告
make test-cov

# 集成测试
make test-integration

# 直接使用 pytest
python -m pytest test/ -v
```

### 代码质量检查

```bash
# 代码检查
make lint

# 代码格式化
make format

# 运行 pre-commit 钩子
make pre-commit-run

# 健康检查
make health
```

## 配置说明

服务配置文件位于 `