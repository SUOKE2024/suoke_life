# RAG服务目录结构

本文档描述了RAG服务的标准目录结构。

## 目录结构

```
services/rag-service/
├── cmd/                    # 命令行入口
│   ├── main.go            # 主程序入口
│   └── execute.go         # 执行函数
├── internal/               # 内部包（不对外暴露）
│   ├── api/               # API定义
│   ├── config/            # 配置管理
│   ├── handlers/          # 请求处理器
│   ├── middleware/        # 中间件
│   ├── models/            # 数据模型
│   ├── rag/               # RAG核心功能
│   ├── storage/           # 存储相关
│   │   └── vector_store/  # 向量存储
│   ├── embeddings/        # 嵌入模型
│   └── utils/             # 工具函数
├── pkg/                    # 可对外暴露的包
├── tests/                  # 测试文件
├── scripts/                # 辅助脚本
├── docs/                   # 文档
└── deployment/             # 部署配置
```

## 模块说明

- **cmd**: 包含应用程序的入口点
- **internal**: 内部实现，不对外部包可见
  - **api**: 定义API接口和路由
  - **config**: 配置加载和管理
  - **handlers**: HTTP请求处理
  - **middleware**: HTTP中间件
  - **models**: 数据模型定义
  - **rag**: RAG核心逻辑
  - **storage**: 存储相关功能
  - **embeddings**: 嵌入模型实现
  - **utils**: 工具函数
- **pkg**: 可对外暴露的包，供其他服务使用
- **tests**: 单元测试和集成测试
- **scripts**: 辅助脚本
- **docs**: 文档
- **deployment**: 部署配置
