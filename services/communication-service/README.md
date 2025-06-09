# Communication Service

这是一个合并后的微服务，包含以下原始服务：

- message-bus
- rag-service

## 架构说明

本服务通过合并多个相关微服务来简化架构，提高维护效率。

## 启动方式

```bash
docker build -t communication-service .
docker run -p 8000:8000 communication-service
```

## API文档

各子服务的API文档位于 `api/` 目录下。

## 子服务说明

### message-bus
- 代码位置: `communication_service/message_bus/`
- API文档: `api/message-bus/`
- 配置文件: `config/message-bus/`

### rag-service
- 代码位置: `communication_service/rag_service/`
- API文档: `api/rag-service/`
- 配置文件: `config/rag-service/`

