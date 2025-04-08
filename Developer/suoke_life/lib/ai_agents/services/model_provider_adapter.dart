// 模型提供商适配器接口
// 用于支持不同的模型服务商，使系统可以方便地切换不同的模型提供商

import 'dart:async';
import 'package:http/http.dart' as http;
import '../models/agent_message.dart';
import '../models/agent_response.dart';

/// 模型提供商类型
enum ModelProviderType {
  /// 百度文心一言
  baidu,
  
  /// 阿里通义千问
  ali,
  
  /// 讯飞星火
  xunfei,
  
  /// 智谱ChatGLM
  zhipu,
  
  /// 深度求索DeepSeek
  deepseek,
  
  /// OpenAI (国际版)
  openai,
  
  /// 本地模型
  local
}

/// 工具调用定义
class ToolDefinition {
  /// 工具名称
  final String name;
  
  /// 工具描述
  final String description;
  
  /// 参数定义
  final Map<String, dynamic> parameters;
  
  /// 构造函数
  const ToolDefinition({
    required this.name,
    required this.description,
    required this.parameters,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'description': description,
      'parameters': parameters,
    };
  }
}

/// 模型调用选项
class ModelCallOptions {
  /// 模型名称
  final String modelName;
  
  /// 温度
  final double temperature;
  
  /// 最大tokens
  final int maxTokens;
  
  /// 启用工具
  final bool enableTools;
  
  /// 工具定义
  final List<ToolDefinition>? tools;
  
  /// 最大步骤数
  final int maxSteps;
  
  /// 流式响应
  final bool streamResponse;
  
  /// 构造函数
  const ModelCallOptions({
    required this.modelName,
    this.temperature = 0.7,
    this.maxTokens = 2000,
    this.enableTools = false,
    this.tools,
    this.maxSteps = 5,
    this.streamResponse = false,
  });
}

/// 模型提供商适配器接口
abstract class ModelProviderAdapter {
  /// 获取提供商类型
  ModelProviderType get providerType;
  
  /// 获取提供商名称
  String get providerName;
  
  /// 获取支持的模型列表
  List<String> getSupportedModels();
  
  /// 检查模型是否可用
  Future<bool> isModelAvailable(String modelName);
  
  /// 调用聊天模型
  Future<AgentResponse> chatCompletion({
    required List<AgentMessage> messages,
    required ModelCallOptions options,
    Duration timeout = const Duration(seconds: 30),
    int retries = 3,
  });
  
  /// 流式调用聊天模型
  Stream<AgentResponseChunk> streamChatCompletion({
    required List<AgentMessage> messages,
    required ModelCallOptions options,
    Duration timeout = const Duration(seconds: 60),
    int retries = 3,
  });
  
  /// 生成嵌入
  Future<List<double>> generateEmbedding({
    required String text,
    String? modelName,
  });
  
  /// 关闭适配器和释放资源
  void dispose();
}

/// 工厂方法创建模型提供商适配器
class ModelProviderFactory {
  /// 创建模型提供商适配器
  static ModelProviderAdapter createProvider(
    ModelProviderType type, {
    Map<String, dynamic>? config,
    http.Client? httpClient,
  }) {
    switch (type) {
      case ModelProviderType.baidu:
        throw UnimplementedError('百度文心一言适配器未实现');
      case ModelProviderType.ali:
        throw UnimplementedError('阿里通义千问适配器未实现');
      case ModelProviderType.xunfei:
        throw UnimplementedError('讯飞星火适配器未实现');
      case ModelProviderType.zhipu:
        throw UnimplementedError('智谱ChatGLM适配器未实现');
      case ModelProviderType.deepseek:
        throw UnimplementedError('深度求索DeepSeek适配器未实现');
      case ModelProviderType.openai:
        throw UnimplementedError('OpenAI适配器未实现');
      case ModelProviderType.local:
        throw UnimplementedError('本地模型适配器未实现');
    }
  }
} 