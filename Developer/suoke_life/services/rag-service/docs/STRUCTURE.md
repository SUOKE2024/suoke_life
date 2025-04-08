# 项目目录结构

本文档说明了RAG服务的目录结构和各个组件的功能。

## 目录结构

```
services/rag-service/
├── cmd/                    # 命令行入口
│   └── main.go            # 主程序入口
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
├── deployment/             # 部署配置
│   ├── docker/            # Docker相关文件
│   └── k8s/               # Kubernetes配置
├── .env.example            # 环境变量示例
├── go.mod                  # Go模块定义
├── go.sum                  # 依赖校验
└── README.md               # 项目说明
```

## 组件说明

### cmd

包含应用程序的入口点，主要是main.go文件，负责配置加载、服务初始化和启动。

### internal

包含所有不对外暴露的内部包。

- **api**: 定义API接口和路由规范
- **config**: 配置加载和管理
- **handlers**: HTTP请求处理器
- **middleware**: HTTP中间件，如日志、认证、错误处理等
- **models**: 数据模型定义
- **rag**: RAG（检索增强生成）的核心实现
- **storage**: 数据存储相关
  - **vector_store**: 向量数据库存储实现
- **embeddings**: 文本嵌入向量生成模型
- **utils**: 通用工具函数

### pkg

可以对外暴露的包，供其他服务使用。

### tests

包含所有测试文件，包括单元测试和集成测试。

### scripts

包含用于构建、部署、数据处理等用途的脚本。

### docs

项目文档，包括API文档、架构说明等。

### deployment

部署相关配置文件。

- **docker**: Docker相关文件，包括Dockerfile和docker-compose.yml
- **k8s**: Kubernetes配置文件

## 代码组织原则

1. **依赖方向**: 代码依赖应该从外到内，例如cmd依赖internal，而internal/handlers依赖internal/rag。

2. **包封装**: 每个包应该只暴露必要的接口，隐藏实现细节。

3. **关注点分离**: 每个包应该只关注一个功能领域，例如配置、API处理等。

4. **依赖注入**: 通过构造函数或工厂方法传递依赖，而不是在包内部直接创建依赖。
