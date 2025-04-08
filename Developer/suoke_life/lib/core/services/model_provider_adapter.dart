// 模型提供者适配器
// 用于统一不同模型API的调用格式

import 'dart:async';
import 'dart:convert';
import 'package:logging/logging.dart' as logging;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/ai_agents/models/agent_message.dart';
import 'package:suoke_life/core/services/config_service.dart';
import 'package:suoke_life/core/services/model_service.dart';
import 'package:suoke_life/di/providers/core_providers.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../ai_agents/core/agent_interface.dart';
import '../../ai_agents/tools/tool_interface.dart';

/// 模型响应
class ModelResponse {
  /// 响应内容
  final String? content;
  
  /// 工具调用
  final List<AgentToolCall>? toolCalls;
  
  /// 响应ID
  final String? id;
  
  /// 原始响应数据
  final Map<String, dynamic>? rawData;
  
  /// 构造函数
  ModelResponse({
    this.content,
    this.toolCalls,
    this.id,
    this.rawData,
  });
}

/// 模型流式响应
class ModelStreamResponse {
  /// 响应内容块
  final String? content;
  
  /// 工具调用
  final List<AgentToolCall>? toolCalls;
  
  /// 是否是最后一个响应块
  final bool isLast;
  
  /// 响应ID
  final String? id;
  
  /// 原始响应数据
  final Map<String, dynamic>? rawData;
  
  /// 构造函数
  ModelStreamResponse({
    this.content,
    this.toolCalls,
    this.isLast = false,
    this.id,
    this.rawData,
  });
}

/// 模型提供商类型
enum ModelProviderType {
  openAI,
  anthropic,
  gemini,
  ollama,
  deepseek,
  baidu,
  alibaba,
  iflytek,
  zhipu,
  local,
}

/// 模型提供商适配器接口
abstract class ModelProviderAdapter {
  final String apiKey;
  final String baseUrl;
  final String defaultModel;
  final ModelProviderType providerType;

  ModelProviderAdapter({
    required this.apiKey,
    required this.baseUrl,
    required this.defaultModel,
    required this.providerType,
  });

  /// 生成文本
  Future<Map<String, dynamic>> generateText({
    required String prompt,
    String? model,
    double temperature = 0.7,
    int maxTokens = 1000,
    Map<String, dynamic>? options,
  });

  /// 生成聊天回复
  Future<Map<String, dynamic>> generateChatResponse({
    required List<Map<String, dynamic>> messages,
    String? model,
    double temperature = 0.7,
    int maxTokens = 1000,
    Map<String, dynamic>? options,
  });

  /// 生成嵌入向量
  Future<List<double>> generateEmbeddings(String text, {String? model});
}

/// 模型提供者适配器实现
class ModelProviderAdapterImpl implements ModelProviderAdapter {
  static final logging.Logger _logger = logging.Logger('ModelProviderAdapterImpl');
  
  @override
  final String apiKey;
  
  @override
  final String baseUrl;
  
  @override
  final String defaultModel;
  
  @override
  final ModelProviderType providerType;
  
  /// 模型服务
  final ModelService _modelService;
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 当前模型名称
  String _modelName;
  
  /// 提供商名称
  final String _providerName;
  
  /// 构造函数
  ModelProviderAdapterImpl({
    required this.apiKey,
    required this.baseUrl,
    required this.defaultModel,
    required this.providerType,
    required ModelService modelService,
    required ConfigService configService,
    required String providerName,
    String? initialModel,
  }) : _modelService = modelService,
       _configService = configService,
       _modelName = initialModel ?? defaultModel,
       _providerName = providerName;
       
  @override
  Future<Map<String, dynamic>> generateText({
    required String prompt,
    String? model,
    double temperature = 0.7,
    int maxTokens = 1000,
    Map<String, dynamic>? options,
  }) async {
    _logger.info('生成文本，提示: ${prompt.substring(0, prompt.length > 20 ? 20 : prompt.length)}...');
    // 基础实现，子类会覆盖
    return {'text': 'ModelProviderAdapterImpl 基础实现'};
  }

  @override
  Future<Map<String, dynamic>> generateChatResponse({
    required List<Map<String, dynamic>> messages,
    String? model,
    double temperature = 0.7,
    int maxTokens = 1000,
    Map<String, dynamic>? options,
  }) async {
    _logger.info('生成聊天回复，消息数: ${messages.length}');
    // 基础实现，子类会覆盖
    return {
      'message': {
        'role': 'assistant',
        'content': 'ModelProviderAdapterImpl 基础实现'
      }
    };
  }

  @override
  Future<List<double>> generateEmbeddings(String text, {String? model}) async {
    _logger.info('生成嵌入向量，文本长度: ${text.length}');
    // 基础实现，子类会覆盖
    return List.generate(384, (index) => (index % 10) / 10);
  }
  
  @override
  ModelService get modelService => _modelService;
  
  @override
  String get providerName => _providerName;
  
  @override
  String get modelName => _modelName;
  
  @override
  set modelName(String name) {
    _modelName = name;
  }
  
  @override
  Future<ModelResponse> generateResponse({
    required List<Map<String, dynamic>> messages,
    List<Map<String, dynamic>>? toolDefinitions,
    Map<String, dynamic>? options,
  }) async {
    try {
      // 合并选项
      final mergedOptions = {
        ...getDefaultOptions(),
        ...?options,
        'model': _modelName,
      };
      
      // 准备工具列表
      final tools = toolDefinitions;
      
      // 调用模型服务
      final agentMessage = await _modelService.chat(
        messages,
        options: mergedOptions,
        tools: tools,
      );
      
      // 转换为统一响应格式
      return ModelResponse(
        content: agentMessage.content,
        toolCalls: agentMessage.toolCalls,
        id: agentMessage.id,
        rawData: agentMessage.toolCalls != null 
            ? {'tool_calls': agentMessage.toolCalls!.map((tc) => tc.toJson()).toList()} 
            : null,
      );
    } catch (e) {
      _logger.severe('生成响应失败: $e');
      throw Exception('生成响应失败: $e');
    }
  }
  
  @override
  Stream<ModelStreamResponse> generateStreamingResponse({
    required List<Map<String, dynamic>> messages,
    List<Map<String, dynamic>>? toolDefinitions,
    Map<String, dynamic>? options,
  }) async* {
    try {
      // 合并选项
      final mergedOptions = {
        ...getDefaultOptions(),
        ...?options,
        'model': _modelName,
        'stream': true,
      };
      
      // 准备工具列表
      final tools = toolDefinitions;
      
      // 调用模型服务获取流式响应
      final stream = _modelService.chatStream(
        messages,
        options: mergedOptions,
        tools: tools,
      );
      
      // 最后一个全内容
      String fullContent = '';
      
      // 转换响应流
      await for (final agentMessage in stream) {
        // 更新全内容
        if (agentMessage.content.isNotEmpty) {
          fullContent = agentMessage.content;
        }
        
        // 检查是否完成流式传输
        final isLast = agentMessage.status != AgentMessageStatus.streaming;
        
        // 转换为统一流式响应格式
        yield ModelStreamResponse(
          content: agentMessage.content,
          toolCalls: agentMessage.toolCalls,
          isLast: isLast,
          id: agentMessage.id,
          rawData: agentMessage.toolCalls != null 
              ? {'tool_calls': agentMessage.toolCalls!.map((tc) => tc.toJson()).toList()} 
              : null,
        );
        
        // 如果消息包含工具调用，这是流的最后一个消息
        if (agentMessage.toolCalls != null && agentMessage.toolCalls!.isNotEmpty) {
          break;
        }
      }
    } catch (e) {
      _logger.severe('生成流式响应失败: $e');
      yield ModelStreamResponse(
        content: '生成响应失败: $e',
        isLast: true,
      );
    }
  }
  
  @override
  Future<List<double>> generateEmbedding(String text) async {
    try {
      return await _modelService.generateEmbedding(text);
    } catch (e) {
      _logger.severe('生成嵌入向量失败: $e');
      throw Exception('生成嵌入向量失败: $e');
    }
  }
  
  @override
  Map<String, dynamic> getDefaultOptions() {
    return {
      'temperature': _configService.getModelTemperature(),
      'top_p': 0.95,
      'max_tokens': 2000,
    };
  }
}

/// 百度模型适配器
class BaiduModelAdapter extends ModelProviderAdapterImpl {
  /// 构造函数
  BaiduModelAdapter({
    required String apiKey,
    required String baseUrl,
    required ModelService modelService,
    required ConfigService configService,
    String? initialModel,
  }) : super(
    apiKey: apiKey,
    baseUrl: baseUrl, 
    defaultModel: 'ernie-bot-4',
    providerType: ModelProviderType.baidu,
    modelService: modelService,
    configService: configService,
    providerName: 'baidu',
    initialModel: initialModel,
  );
  
  @override
  Map<String, dynamic> getDefaultOptions() {
    final baseOptions = super.getDefaultOptions();
    return {
      ...baseOptions,
      'tool_choice': 'auto',
    };
  }
}

/// 阿里巴巴模型适配器
class AlibabaModelAdapter extends ModelProviderAdapterImpl {
  /// 构造函数
  AlibabaModelAdapter({
    required String apiKey,
    required String baseUrl,
    required ModelService modelService,
    required ConfigService configService,
    String? initialModel,
  }) : super(
    apiKey: apiKey,
    baseUrl: baseUrl,
    defaultModel: 'qwen-plus',
    providerType: ModelProviderType.alibaba,
    modelService: modelService,
    configService: configService,
    providerName: 'alibaba',
    initialModel: initialModel,
  );
}

/// 讯飞模型适配器
class IFlytekModelAdapter extends ModelProviderAdapterImpl {
  /// 构造函数
  IFlytekModelAdapter({
    required String apiKey,
    required String baseUrl,
    required ModelService modelService,
    required ConfigService configService,
    String? initialModel,
  }) : super(
    apiKey: apiKey,
    baseUrl: baseUrl,
    defaultModel: 'spark-3.5',
    providerType: ModelProviderType.iflytek,
    modelService: modelService,
    configService: configService,
    providerName: 'iflytek',
    initialModel: initialModel,
  );
}

/// Deepseek模型适配器
class DeepseekModelAdapter extends ModelProviderAdapterImpl {
  /// 构造函数
  DeepseekModelAdapter({
    required String apiKey,
    required String baseUrl,
    required ModelService modelService,
    required ConfigService configService,
    String? initialModel,
  }) : super(
    apiKey: apiKey,
    baseUrl: baseUrl,
    defaultModel: 'deepseek-chat',
    providerType: ModelProviderType.deepseek,
    modelService: modelService,
    configService: configService,
    providerName: 'deepseek',
    initialModel: initialModel,
  );
}

/// 模型适配器工厂
class ModelAdapterFactory {
  static final logging.Logger _logger = logging.Logger('ModelAdapterFactory');
  
  /// 创建模型适配器
  static ModelProviderAdapter createAdapter({
    required String provider,
    required ModelService modelService,
    required ConfigService configService,
    String? modelName,
  }) {
    switch (provider.toLowerCase()) {
      case 'baidu':
        return BaiduModelAdapter(
          apiKey: '',
          baseUrl: '',
          modelService: modelService,
          configService: configService,
          initialModel: modelName,
        );
      case 'alibaba':
        return AlibabaModelAdapter(
          apiKey: '',
          baseUrl: '',
          modelService: modelService,
          configService: configService,
          initialModel: modelName,
        );
      case 'iflytek':
        return IFlytekModelAdapter(
          apiKey: '',
          baseUrl: '',
          modelService: modelService,
          configService: configService,
          initialModel: modelName,
        );
      case 'deepseek':
        return DeepseekModelAdapter(
          apiKey: '',
          baseUrl: '',
          modelService: modelService,
          configService: configService,
          initialModel: modelName,
        );
      default:
        _logger.warning('未知的模型提供商: $provider，使用百度作为默认提供商');
        return BaiduModelAdapter(
          apiKey: '',
          baseUrl: '',
          modelService: modelService,
          configService: configService,
          initialModel: modelName,
        );
    }
  }
}

/// 模型提供者适配器Provider
final modelProviderAdapterProvider = Provider<ModelProviderAdapter>((ref) {
  // 获取配置服务
  final configService = ref.watch(configServiceProvider);
  
  // 获取首选模型提供商
  final provider = configService.getPreferredModelProvider();
  
  // 创建模型服务
  final modelService = ModelServiceFactory.createModelService(
    provider,
    configService,
  );
  
  // 创建并返回适配器
  return ModelAdapterFactory.createAdapter(
    provider: provider,
    modelService: modelService,
    configService: configService,
  );
}); 