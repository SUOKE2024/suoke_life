# 索克生活（Suoke Life）平台架构说明

## 一、整体架构概览

索克生活平台采用"多智能体+多模态RAG+知识图谱+区块链"融合架构，前后端分离，微服务化部署，支持端-云协同推理。

- **前端**：React Native跨平台App，支持多模态采集、消息交互、健康数据可视化。
- **后端**：Python FastAPI微服务，核心为RAG服务、知识图谱服务、四诊诊断服务、区块链健康数据服务等。
- **多智能体**：小艾、小克、老克、索儿分工协作，分布式自主决策。
- **多模态能力**：支持文本、图片、音频、视频等多模态输入，自动特征提取与融合。
- **数据流**：采集→特征提取→RAG推理→知识图谱→健康建议→数据存证。

## 二、核心模块说明

### 1. 多模态RAG服务
- 支持文本+图片/音频/视频联合推理。
- 关键文件：`services/rag-service/internal/multimodal/feature_extractors.py`、`api/enhanced_api_gateway.py`
- 特征提取：OCR（easyocr）、ASR（whisper）、视频帧抽取（opencv）。

### 2. 智能体协作与决策
- 四大智能体通过API/消息总线协同，分工明确。
- 典型场景：健康问诊、体质辨识、健康管理、生活方式建议。

### 3. 知识图谱与推理引擎
- 中医知识结构化、图谱化，支持自动推理与规则自进化。
- 关键文件：`services/rag-service/internal/kg/knowledge_graph_enhancer.py`、`knowledge_reasoning_engine.py`

### 4. 区块链健康数据管理
- 健康数据可信存证、零知识验证。
- 关键文件：`services/blockchain-service/`

## 三、数据流与典型流程

1. 用户通过App采集/上传多模态数据（文本、图片、音频、视频）。
2. 前端调用RAG多模态接口，后端自动提取特征。
3. RAG服务联合知识图谱推理，生成健康建议。
4. 结果返回前端展示，并可存证到区块链。

## 四、开发规范与协作
- 代码风格：前端TypeScript+ESLint，后端Python+黑格式化。
- 重要变更需同步更新`README.md`、`openapi.yaml`、架构文档。
- 详细开发规范见`docs/DEVELOPMENT_GUIDE.md`。

## 五、快速入口
- 多模态API文档：`services/rag-service/api/rest/openapi.yaml`
- 典型用例、数据流、接口示例见`README.md`

## 六、联系方式
- 技术团队邮箱：tech@suokelife.com
- 欢迎新成员和外部合作方加入，共建智能健康生态！ 