# 索克生活APP集成OpenAI Agents SDK指南

## 概述

本文档介绍了如何在索克生活APP中集成OpenAI Agents SDK，以支持更高级的智能体功能，包括工具调用、多智能体协作和实时响应生成。

## 技术架构更新

集成OpenAI Agents SDK后，索克生活APP的技术架构将有以下更新：

1. **智能体接口统一**：所有智能体（老克、望诊、脉诊等）将采用统一的OpenAI Assistants API风格接口
2. **工具调用标准化**：文件搜索、网络搜索等工具将支持OpenAI工具格式
3. **智能体间交接机制**：支持基于capabilities的智能体间任务交接
4. **响应流式生成**：支持类似OpenAI流式响应的实时生成机制

## 后端服务配置

集成OpenAI Agents SDK后，需要部署以下新服务：

### 1. 文件搜索服务

负责处理智能体的知识库查询请求，支持语义搜索和关键词搜索。

```yaml
文件：scripts/deploy/kubernetes/file-search-service.yaml
```

### 2. 网络搜索服务

负责处理智能体的网络搜索请求，获取最新的健康信息。此功能已整合到RAG服务中。

```yaml
文件：scripts/deploy/kubernetes/rag-service.yaml
```

### 3. 智能体协调服务

负责协调多个智能体之间的交互，处理交接请求。

```yaml
文件：scripts/deploy/kubernetes/agent-coordinator-service.yaml
```

### 4. 智能体配置更新

每个智能体的配置文件需要更新，以支持OpenAI Agents SDK风格。以老克智能体为例：

```yaml
文件：scripts/deploy/kubernetes/laoke-agent-config.yaml
```

## 前端集成指南

### 1. API客户端更新

前端需要更新API客户端，以支持新的API端点和响应格式：

```dart
// lib/core/api/openai_compatible_client.dart

class OpenAICompatibleClient {
  // 创建新线程
  Future<Thread> createThread();
  
  // 添加消息到线程
  Future<Message> addMessage(String threadId, String content);
  
  // 运行线程
  Future<Run> createRun(String threadId, {String assistantId});
  
  // 获取运行状态
  Future<Run> getRun(String threadId, String runId);
  
  // 获取线程消息
  Future<List<Message>> getMessages(String threadId);
  
  // 流式响应处理
  Stream<RunChunk> streamRun(String threadId, String runId);
}
```

### 2. 会话管理更新

会话状态管理需要支持OpenAI线程和运行概念：

```dart
// lib/core/models/conversation_state.dart

class ConversationState {
  final String threadId;
  final String currentRunId;
  final List<Message> messages;
  final RunStatus runStatus;
  final List<ToolCall> pendingToolCalls;
  final Agent currentAgent;
  
  // 判断是否需要工具调用
  bool get requiresToolCalls => 
      runStatus == RunStatus.requiresAction && 
      pendingToolCalls.isNotEmpty;
      
  // 判断是否已完成
  bool get isCompleted => 
      runStatus == RunStatus.completed || 
      runStatus == RunStatus.failed;
}
```

### 3. UI组件更新

UI组件需要更新以支持工具调用和智能体交接的显示：

```dart
// lib/presentation/chat/widgets/tool_call_card.dart

class ToolCallCard extends StatelessWidget {
  final ToolCall toolCall;
  final ToolCallStatus status;
  
  @override
  Widget build(BuildContext context) {
    return Card(
      // 工具调用显示UI
    );
  }
}

// lib/presentation/chat/widgets/agent_handoff_indicator.dart

class AgentHandoffIndicator extends StatelessWidget {
  final Agent previousAgent;
  final Agent newAgent;
  
  @override
  Widget build(BuildContext context) {
    return Container(
      // 智能体交接显示UI
    );
  }
}
```

## 部署步骤

1. 执行部署脚本：

```bash
./scripts/deploy_kubernetes_openai_agents.sh
```

2. 验证部署：

```bash
kubectl get pods -n suoke
kubectl get services -n suoke
```

3. 更新API网关配置：

```bash
kubectl apply -f scripts/deploy/kubernetes/api-gateway.yaml
```

## 测试验证

部署完成后，可以通过以下方式验证OpenAI Agents SDK集成：

1. 使用兼容端点发送请求：

```bash
curl -X POST https://api.suoke.life/api/v1/threads \
  -H "Content-Type: application/json"
```

2. 创建线程并发送消息：

```bash
curl -X POST https://api.suoke.life/api/v1/threads/thread_id/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "我最近感觉容易疲劳，应该怎么调理？"}'
```

3. 运行线程：

```bash
curl -X POST https://api.suoke.life/api/v1/threads/thread_id/runs \
  -H "Content-Type: application/json" \
  -d '{"assistant_id": "laoke"}'
```

## 注意事项

1. 集成过程中需要保持与现有API的兼容性，以避免影响已有功能
2. 所有敏感信息（API密钥等）应通过Kubernetes Secrets管理
3. 对于生产环境部署，建议启用SSL证书和API访问限制

## 后续计划

1. 完善工具调用系统，增加更多健康相关工具
2. 增强多模态处理能力，支持图像和音频分析
3. 优化智能体交接机制，提高协作效率
4. 实现自定义工具注册系统，便于扩展功能 