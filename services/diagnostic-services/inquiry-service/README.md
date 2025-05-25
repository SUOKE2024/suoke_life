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
- Python 3.8+
- gRPC
- PyYAML

### 安装依赖
```bash
pip install grpcio grpcio-tools pyyaml python-dotenv
```

### 启动服务

1. 使用启动脚本：
```bash
python3 start_server.py
```

2. 或直接运行：
```bash
cd inquiry-service
python3 -m cmd.server
```

### 运行测试
```bash
python3 test_inquiry_service.py
```

### 测试其他功能
```bash
# 测试批量分析
python3 test_inquiry_service.py --batch

# 测试病史分析
python3 test_inquiry_service.py --history
```

## 配置说明

服务配置文件位于 `config/config.yaml`，主要配置项：

- `server.port`: gRPC服务端口（默认: 50052）
- `tcm_knowledge.auto_create_sample_data`: 自动创建示例数据
- `health_risk_assessment.min_confidence`: 最小置信度阈值
- `symptom_extraction.max_symptoms_per_text`: 每次提取的最大症状数

## 知识库数据

中医知识库数据存储在 `data/tcm_knowledge/` 目录下：

- `patterns.yaml`: 证型数据
- `symptoms.yaml`: 症状数据
- `symptom_pattern_mapping.yaml`: 症状-证型映射
- `pattern_categories.yaml`: 证型分类
- `body_locations.yaml`: 身体部位数据

## 开发模式

服务支持Mock模式，用于开发和测试：

```bash
export USE_MOCK_MODE=true
python3 start_server.py
```

## 主要特性

1. **智能症状提取**
   - 基于规则和关键词的症状识别
   - 否定词检测
   - 症状严重程度和持续时间分析

2. **中医理论集成**
   - 完整的证型分类体系
   - 症状与证型的智能匹配
   - 体质类型考虑

3. **综合风险评估**
   - 多维度风险分析（症状、病史、体质）
   - 即时和长期风险区分
   - 个性化预防策略

4. **知识驱动**
   - 可扩展的知识库架构
   - 支持自定义症状和证型
   - 灵活的映射规则

## 项目结构

```
inquiry-service/
├── api/grpc/              # gRPC接口定义
├── cmd/server.py          # 服务启动入口
├── config/                # 配置文件
├── data/                  # 知识库数据
├── internal/              # 内部实现
│   ├── delivery/          # gRPC服务实现
│   ├── dialogue/          # 对话管理
│   ├── llm/              # LLM相关模块
│   │   ├── symptom_extractor.py
│   │   ├── tcm_pattern_mapper.py
│   │   └── health_risk_assessor.py
│   ├── knowledge/         # 知识库
│   │   └── tcm_knowledge_base.py
│   └── repository/        # 数据存储
├── test_inquiry_service.py # 测试脚本
└── start_server.py        # 简化启动脚本
```

## 注意事项

1. 服务默认在50052端口运行
2. 首次运行会自动创建示例知识库数据
3. 生产环境应使用完整的知识库数据
4. 建议定期更新知识库以提高准确性

## 许可证

本项目遵循项目根目录的LICENSE文件中定义的许可证。 