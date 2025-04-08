// 模型服务接口
// 用于封装不同大模型API的调用

import 'dart:async';
import 'dart:convert';

import 'package:logging/logging.dart' as logging;
import 'package:suoke_life/ai_agents/models/agent_message.dart';
import 'package:suoke_life/core/services/config_service.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

import 'model_provider_adapter.dart';
import '../../ai_agents/core/agent_interface.dart';
import '../../ai_agents/tools/tool_interface.dart';

/// 模型类型枚举
enum ModelType {
  /// 文本生成模型
  chat,
  
  /// 多模态模型
  multimodal,
  
  /// 嵌入模型
  embedding,
  
  /// 语音模型
  speech,
}

/// 模型服务配置
class ModelServiceConfig {
  /// 模型提供商类型
  final ModelProviderType providerType;
  
  /// API密钥
  final String apiKey;
  
  /// 端点URL
  final String? endpoint;
  
  /// 默认模型名称
  final String defaultModel;
  
  /// 默认选项
  final Map<String, dynamic> defaultOptions;
  
  /// 是否启用流式响应
  final bool enableStreaming;
  
  /// 是否使用Assistants API
  final bool useAssistantsApi;
  
  /// Assistants API配置
  final Map<String, dynamic>? assistantsApiConfig;

  /// 构造函数
  const ModelServiceConfig({
    required this.providerType,
    required this.apiKey,
    this.endpoint,
    required this.defaultModel,
    this.defaultOptions = const {},
    this.enableStreaming = true,
    this.useAssistantsApi = false,
    this.assistantsApiConfig,
  });
}

/// 流式响应回调
typedef StreamingCallback = void Function(String textDelta);

/// 撤销处理回调
typedef CancelCallback = void Function();

/// 模型服务接口
abstract class ModelService {
  /// 发送消息到模型并获取响应
  Future<AgentMessage> chat(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  });
  
  /// 发送消息到模型并获取流式响应
  Stream<AgentMessage> chatStream(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  });
  
  /// 生成嵌入向量
  Future<List<double>> generateEmbedding(String text);
  
  /// 获取可用的模型列表
  Future<List<String>> getAvailableModels(ModelType type);
}

/// 模型服务工厂
class ModelServiceFactory {
  static final logging.Logger _logger = logging.Logger('ModelServiceFactory');
  
  /// 创建模型服务实例
  static ModelService createModelService(
    String provider,
    ConfigService configService,
  ) {
    switch (provider.toLowerCase()) {
      case 'baidu':
        return BaiduModelService(configService);
      case 'deepseek':
        return DeepseekModelService(configService);
      case 'alibaba':
        return AlibabaModelService(configService);
      case 'iflytek':
        return IFlytekModelService(configService);
      default:
        _logger.warning('未知的模型提供商: $provider, 使用默认的模型服务');
        return BaiduModelService(configService);
    }
  }
}

/// 百度文心一言模型服务
class BaiduModelService implements ModelService {
  static final logging.Logger _logger = logging.Logger('BaiduModelService');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// API基础URL
  static const String _baseUrl = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop';
  
  /// 访问令牌
  String? _accessToken;
  
  /// 访问令牌过期时间
  DateTime? _tokenExpiry;
  
  /// 构造函数
  BaiduModelService(this._configService);
  
  /// 获取访问令牌
  Future<String> _getAccessToken() async {
    // 检查缓存的令牌是否有效
    if (_accessToken != null && _tokenExpiry != null) {
      // 令牌未过期，还有5分钟以上的有效期
      if (_tokenExpiry!.isAfter(DateTime.now().add(const Duration(minutes: 5)))) {
        return _accessToken!;
      }
    }
    
    // 获取API密钥
    final apiKey = _configService.getBaiduApiKey();
    final secretKey = _configService.getBaiduSecretKey();
    
    if (apiKey == null || secretKey == null) {
      throw Exception('百度API密钥未配置');
    }
    
    try {
      // TODO: 实现获取百度访问令牌的逻辑
      // 这里简化处理，实际应通过HTTP请求获取令牌
      _accessToken = 'sample_access_token';
      _tokenExpiry = DateTime.now().add(const Duration(days: 30));
      return _accessToken!;
    } catch (e) {
      _logger.severe('获取百度访问令牌失败: $e');
      throw Exception('获取访问令牌失败: $e');
    }
  }
  
  @override
  Future<AgentMessage> chat(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async {
    try {
      final accessToken = await _getAccessToken();
      final model = options?['model'] as String? ?? 'ernie-bot-4';
      
      // 准备请求体
      final Map<String, dynamic> requestBody = {
        'messages': messages,
        'temperature': options?['temperature'] ?? 0.7,
        'top_p': options?['top_p'] ?? 0.95,
      };
      
      // 添加工具调用支持
      if (tools != null && tools.isNotEmpty) {
        requestBody['tools'] = tools;
        requestBody['tool_choice'] = options?['tool_choice'] ?? 'auto';
      }
      
      // TODO: 发送HTTP请求到百度API
      // 这里简化处理，实际应通过HTTP客户端发送请求
      
      // 模拟API响应
      final Map<String, dynamic> response = {
        'id': 'mock-response-id',
        'object': 'chat.completion',
        'created': DateTime.now().millisecondsSinceEpoch ~/ 1000,
        'result': '这是来自百度文心一言的模拟响应',
      };
      
      // 检查工具调用
      List<AgentToolCall>? toolCalls;
      if (response.containsKey('tool_calls')) {
        final toolCallsJson = response['tool_calls'] as List;
        toolCalls = toolCallsJson.map((tc) {
          return AgentToolCall(
            id: tc['id'],
            name: tc['function']['name'],
            arguments: tc['function']['arguments'],
          );
        }).toList();
      }
      
      // 返回助手消息
      return AgentMessage.assistant(
        content: response['result'],
        toolCalls: toolCalls,
      );
    } catch (e) {
      _logger.severe('百度模型调用失败: $e');
      return AgentMessage.assistant(
        content: '抱歉，我暂时无法处理您的请求。请稍后再试。',
        status: AgentMessageStatus.error,
      );
    }
  }
  
  @override
  Stream<AgentMessage> chatStream(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async* {
    try {
      final accessToken = await _getAccessToken();
      final model = options?['model'] as String? ?? 'ernie-bot-4';
      
      // 准备请求体
      final Map<String, dynamic> requestBody = {
        'messages': messages,
        'temperature': options?['temperature'] ?? 0.7,
        'top_p': options?['top_p'] ?? 0.95,
        'stream': true,
      };
      
      // 添加工具调用支持
      if (tools != null && tools.isNotEmpty) {
        requestBody['tools'] = tools;
        requestBody['tool_choice'] = options?['tool_choice'] ?? 'auto';
      }
      
      // TODO: 发送HTTP流请求到百度API
      // 这里简化处理，模拟流响应
      
      // 创建初始响应消息
      final responseMessage = AgentMessage.assistant(
        content: '',
        status: AgentMessageStatus.streaming,
      );
      
      // 模拟流式返回
      final chunks = [
        '这是',
        '来自',
        '百度',
        '文心一言',
        '的',
        '模拟',
        '流式',
        '响应',
        '。'
      ];
      
      for (var chunk in chunks) {
        await Future.delayed(const Duration(milliseconds: 100));
        responseMessage.content += chunk;
        yield responseMessage;
      }
      
      // 模拟工具调用（最后一个消息）
      if (tools != null && tools.isNotEmpty) {
        final toolCall = AgentToolCall(
          name: 'search_health_info',
          arguments: json.encode({
            'query': '常见感冒症状',
          }),
        );
        
        responseMessage.updateWithToolCalls([toolCall]);
      }
      
      // 完成流式传输
      responseMessage.completeStreaming();
      yield responseMessage;
    } catch (e) {
      _logger.severe('百度模型流式调用失败: $e');
      yield AgentMessage.assistant(
        content: '抱歉，我暂时无法处理您的请求。请稍后再试。',
        status: AgentMessageStatus.error,
      );
    }
  }
  
  @override
  Future<List<double>> generateEmbedding(String text) async {
    try {
      final accessToken = await _getAccessToken();
      
      // TODO: 实现调用百度嵌入API的逻辑
      // 这里简化处理，返回固定长度的随机向量
      return List.generate(384, (index) => (index % 10) / 10);
    } catch (e) {
      _logger.severe('生成嵌入向量失败: $e');
      throw Exception('生成嵌入向量失败: $e');
    }
  }
  
  @override
  Future<List<String>> getAvailableModels(ModelType type) async {
    switch (type) {
      case ModelType.chat:
        return ['ernie-bot', 'ernie-bot-4', 'ernie-bot-8k', 'ernie-bot-turbo'];
      case ModelType.embedding:
        return ['ernie-embedding-text-v1'];
      case ModelType.multimodal:
        return ['ernie-vilg-v2', 'ernie-vl-3.0'];
      case ModelType.speech:
        return ['ernie-speed-speech'];
    }
  }
}

/// 深度求索模型服务
class DeepseekModelService implements ModelService {
  static final logging.Logger _logger = logging.Logger('DeepseekModelService');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 构造函数
  DeepseekModelService(this._configService);
  
  @override
  Future<AgentMessage> chat(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async {
    // 简化实现，返回模拟响应
    return AgentMessage.assistant(
      content: '这是来自Deepseek的响应',
    );
  }
  
  @override
  Stream<AgentMessage> chatStream(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async* {
    // 简化实现，返回模拟流式响应
    final responseMessage = AgentMessage.assistant(
      content: '',
      status: AgentMessageStatus.streaming,
    );
    
    final chunks = ['这是', '来自', 'Deepseek', '的', '响应'];
    
    for (var chunk in chunks) {
      await Future.delayed(const Duration(milliseconds: 100));
      responseMessage.content += chunk;
      yield responseMessage;
    }
    
    responseMessage.completeStreaming();
    yield responseMessage;
  }
  
  @override
  Future<List<double>> generateEmbedding(String text) async {
    // 简化实现，返回固定向量
    return List.generate(384, (index) => (index % 10) / 10);
  }
  
  @override
  Future<List<String>> getAvailableModels(ModelType type) async {
    // 简化实现，返回固定模型列表
    return ['deepseek-chat', 'deepseek-lite', 'deepseek-coder'];
  }
}

/// 阿里通义千问模型服务
class AlibabaModelService implements ModelService {
  static final logging.Logger _logger = logging.Logger('AlibabaModelService');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 构造函数
  AlibabaModelService(this._configService);
  
  @override
  Future<AgentMessage> chat(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async {
    // 简化实现，返回模拟响应
    return AgentMessage.assistant(
      content: '这是来自阿里通义千问的响应',
    );
  }
  
  @override
  Stream<AgentMessage> chatStream(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async* {
    // 简化实现，返回模拟流式响应
    final responseMessage = AgentMessage.assistant(
      content: '',
      status: AgentMessageStatus.streaming,
    );
    
    final chunks = ['这是', '来自', '阿里', '通义千问', '的', '响应'];
    
    for (var chunk in chunks) {
      await Future.delayed(const Duration(milliseconds: 100));
      responseMessage.content += chunk;
      yield responseMessage;
    }
    
    responseMessage.completeStreaming();
    yield responseMessage;
  }
  
  @override
  Future<List<double>> generateEmbedding(String text) async {
    // 简化实现，返回固定向量
    return List.generate(384, (index) => (index % 10) / 10);
  }
  
  @override
  Future<List<String>> getAvailableModels(ModelType type) async {
    // 简化实现，返回固定模型列表
    return ['qwen-plus', 'qwen-max', 'qwen-turbo'];
  }
}

/// 科大讯飞星火认知模型服务
class IFlytekModelService implements ModelService {
  static final logging.Logger _logger = logging.Logger('IFlytekModelService');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 构造函数
  IFlytekModelService(this._configService);
  
  @override
  Future<AgentMessage> chat(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async {
    // 简化实现，返回模拟响应
    return AgentMessage.assistant(
      content: '这是来自科大讯飞星火认知的响应',
    );
  }
  
  @override
  Stream<AgentMessage> chatStream(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async* {
    // 简化实现，返回模拟流式响应
    final responseMessage = AgentMessage.assistant(
      content: '',
      status: AgentMessageStatus.streaming,
    );
    
    final chunks = ['这是', '来自', '科大讯飞', '星火认知', '的', '响应'];
    
    for (var chunk in chunks) {
      await Future.delayed(const Duration(milliseconds: 100));
      responseMessage.content += chunk;
      yield responseMessage;
    }
    
    responseMessage.completeStreaming();
    yield responseMessage;
  }
  
  @override
  Future<List<double>> generateEmbedding(String text) async {
    // 简化实现，返回固定向量
    return List.generate(384, (index) => (index % 10) / 10);
  }
  
  @override
  Future<List<String>> getAvailableModels(ModelType type) async {
    // 简化实现，返回固定模型列表
    return ['spark-3.5', 'spark-3.0'];
  }
}

/// 模型服务 - 集成OpenAI Assistants API
class ModelServiceImpl implements ModelService {
  static final logging.Logger _logger = logging.Logger('ModelService');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 模型适配器
  late ModelProviderAdapter _adapter;
  
  /// 是否使用Assistants API
  bool _useAssistantsApi = false;
  
  /// Assistants API配置
  Map<String, dynamic>? _assistantsApiConfig;
  
  /// 构造函数
  ModelServiceImpl({
    required ConfigService configService,
    ModelServiceConfig? config,
  }) : _configService = configService {
    // 如果提供了配置，则使用提供的配置
    if (config != null) {
      _initializeAdapter(config);
    } else {
      // 否则从配置服务加载
      _loadConfigFromConfigService();
    }
  }
  
  /// 从配置服务加载配置
  void _loadConfigFromConfigService() {
    final modelConfig = _configService.getModelConfig();
    
    final providerType = ModelProviderType.values.firstWhere(
      (type) => type.toString().split('.').last.toLowerCase() == modelConfig['provider'],
      orElse: () => ModelProviderType.openAI,
    );
    
    final config = ModelServiceConfig(
      providerType: providerType,
      apiKey: modelConfig['api_key'],
      endpoint: modelConfig['endpoint'],
      defaultModel: modelConfig['default_model'],
      defaultOptions: modelConfig['default_options'] ?? {},
      enableStreaming: modelConfig['enable_streaming'] ?? true,
      useAssistantsApi: modelConfig['use_assistants_api'] ?? false,
      assistantsApiConfig: modelConfig['assistants_api_config'],
    );
    
    _initializeAdapter(config);
  }
  
  /// 初始化适配器
  void _initializeAdapter(ModelServiceConfig config) {
    _useAssistantsApi = config.useAssistantsApi;
    _assistantsApiConfig = config.assistantsApiConfig;
    
    switch (config.providerType) {
      case ModelProviderType.openAI:
        _adapter = OpenAIAdapter(
          apiKey: config.apiKey,
          endpoint: config.endpoint,
          defaultModel: config.defaultModel,
          defaultOptions: config.defaultOptions,
        );
        break;
      case ModelProviderType.anthropic:
        _adapter = AnthropicAdapter(
          apiKey: config.apiKey,
          endpoint: config.endpoint,
          defaultModel: config.defaultModel,
          defaultOptions: config.defaultOptions,
        );
        break;
      case ModelProviderType.ollama:
        _adapter = OllamaAdapter(
          endpoint: config.endpoint ?? 'http://localhost:11434',
          defaultModel: config.defaultModel,
          defaultOptions: config.defaultOptions,
        );
        break;
      case ModelProviderType.gemini:
        _adapter = GeminiAdapter(
          apiKey: config.apiKey,
          defaultModel: config.defaultModel,
          defaultOptions: config.defaultOptions,
        );
        break;
      case ModelProviderType.deepseek:
        _adapter = DeepseekAdapter(
          apiKey: config.apiKey,
          endpoint: config.endpoint,
          defaultModel: config.defaultModel,
          defaultOptions: config.defaultOptions,
        );
        break;
      default:
        throw UnimplementedError('不支持的模型提供商: ${config.providerType}');
    }
    
    _logger.info('初始化模型服务: ${config.providerType}');
  }
  
  /// 生成文本
  Future<String> generateText({
    required String prompt,
    String? systemPrompt,
    Map<String, dynamic>? options,
    StreamingCallback? onStream,
    Stream<bool>? cancelSignal,
  }) async {
    try {
      _logger.info('生成文本, 提示词: $prompt');
      
      final result = await _adapter.generateText(
        prompt: prompt,
        systemPrompt: systemPrompt,
        options: options,
        onStream: onStream,
        cancelSignal: cancelSignal,
      );
      
      _logger.info('生成文本成功');
      return result;
    } catch (e, stackTrace) {
      _logger.severe('生成文本失败: $e', stackTrace);
      rethrow;
    }
  }
  
  /// 生成对话回复
  Future<Message> generateChatResponse({
    required List<Message> messages,
    List<Map<String, dynamic>>? tools,
    Map<String, dynamic>? options,
    StreamingCallback? onStream,
    Stream<bool>? cancelSignal,
  }) async {
    try {
      _logger.info('生成对话回复, 消息数: ${messages.length}');
      
      if (_useAssistantsApi) {
        return await _generateWithAssistantsAPI(
          messages: messages,
          tools: tools,
          options: options,
          onStream: onStream,
          cancelSignal: cancelSignal,
        );
      }
      
      final formattedMessages = messages.map((message) {
        final role = message.type.toString().split('.').last;
        
        if (message.type == MessageType.tool) {
          return {
            'role': 'tool',
            'content': message.content,
            'tool_call_id': message.metadata?['tool_call_id'],
          };
        }
        
        return {
          'role': role,
          'content': message.content,
          if (message.toolCalls != null && message.toolCalls!.isNotEmpty)
            'tool_calls': message.toolCalls!.map((tc) => tc.toJson()).toList(),
          if (message.fileIds != null && message.fileIds!.isNotEmpty)
            'file_ids': message.fileIds,
        };
      }).toList();
      
      final responseJson = await _adapter.generateChatResponse(
        messages: formattedMessages,
        tools: tools,
        options: options,
        onStream: onStream,
        cancelSignal: cancelSignal,
      );
      
      // 解析工具调用
      List<ToolCall>? toolCalls;
      if (responseJson['tool_calls'] != null) {
        toolCalls = (responseJson['tool_calls'] as List).map((tc) {
          return ToolCall(
            id: tc['id'],
            toolName: tc['function']['name'],
            parameters: jsonDecode(tc['function']['arguments']),
          );
        }).toList();
      }
      
      final response = Message.assistant(
        content: responseJson['content'] ?? '',
        toolCalls: toolCalls,
      );
      
      _logger.info('生成对话回复成功');
      return response;
    } catch (e, stackTrace) {
      _logger.severe('生成对话回复失败: $e', stackTrace);
      
      return Message.assistant(
        content: '生成回复时出错: $e',
        metadata: {'error': e.toString()},
      );
    }
  }
  
  /// 使用OpenAI Assistants API生成回复
  Future<Message> _generateWithAssistantsAPI({
    required List<Message> messages,
    List<Map<String, dynamic>>? tools,
    Map<String, dynamic>? options,
    StreamingCallback? onStream,
    Stream<bool>? cancelSignal,
  }) async {
    if (_adapter is! OpenAIAdapter) {
      throw UnsupportedError('Assistants API仅支持OpenAI提供商');
    }
    
    try {
      final assistantId = _assistantsApiConfig?['assistant_id'];
      if (assistantId == null) {
        throw StateError('未配置Assistant ID');
      }
      
      // 创建线程
      final threadId = await _createThread();
      
      // 添加消息到线程
      for (final message in messages.where((m) => m.type != MessageType.system)) {
        await _addMessageToThread(threadId, message);
      }
      
      // 运行Assistant
      final runId = await _runAssistant(
        threadId: threadId,
        assistantId: assistantId,
        options: options,
      );
      
      // 轮询运行状态
      final completer = Completer<Map<String, dynamic>>();
      
      // 处理取消信号
      if (cancelSignal != null) {
        cancelSignal.listen((cancel) {
          if (cancel && !completer.isCompleted) {
            _cancelRun(threadId, runId);
            completer.completeError('用户取消了请求');
          }
        });
      }
      
      // 开始轮询
      _pollRunStatus(
        threadId: threadId,
        runId: runId,
        completer: completer,
        onStream: onStream,
      );
      
      // 等待结果
      final runResult = await completer.future;
      
      // 获取并处理Assistant的回复
      final messages = await _getThreadMessages(threadId);
      final assistantMessage = messages.first;
      
      // 解析工具调用
      List<ToolCall>? toolCalls;
      if (assistantMessage['tool_calls'] != null) {
        toolCalls = (assistantMessage['tool_calls'] as List).map((tc) {
          return ToolCall(
            id: tc['id'],
            toolName: tc['function']['name'],
            parameters: jsonDecode(tc['function']['arguments']),
          );
        }).toList();
      }
      
      return Message.assistant(
        content: assistantMessage['content'][0]['text']['value'],
        toolCalls: toolCalls,
      );
    } catch (e, stackTrace) {
      _logger.error('使用Assistants API生成回复失败: $e', stackTrace);
      
      return Message.assistant(
        content: '生成回复时出错: $e',
        metadata: {'error': e.toString()},
      );
    }
  }
  
  /// 创建线程
  Future<String> _createThread() async {
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/threads'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${_adapter.apiKey}',
        'OpenAI-Beta': 'assistants=v1',
      },
      body: jsonEncode({}),
    );
    
    if (response.statusCode != 200) {
      throw Exception('创建线程失败: ${response.body}');
    }
    
    final data = jsonDecode(response.body);
    return data['id'];
  }
  
  /// 添加消息到线程
  Future<void> _addMessageToThread(String threadId, Message message) async {
    final role = message.type == MessageType.user ? 'user' : 'assistant';
    
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/threads/$threadId/messages'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${_adapter.apiKey}',
        'OpenAI-Beta': 'assistants=v1',
      },
      body: jsonEncode({
        'role': role,
        'content': message.content,
        if (message.fileIds != null && message.fileIds!.isNotEmpty)
          'file_ids': message.fileIds,
      }),
    );
    
    if (response.statusCode != 200) {
      throw Exception('添加消息到线程失败: ${response.body}');
    }
  }
  
  /// 运行Assistant
  Future<String> _runAssistant({
    required String threadId,
    required String assistantId,
    Map<String, dynamic>? options,
  }) async {
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/threads/$threadId/runs'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${_adapter.apiKey}',
        'OpenAI-Beta': 'assistants=v1',
      },
      body: jsonEncode({
        'assistant_id': assistantId,
        ...?options,
      }),
    );
    
    if (response.statusCode != 200) {
      throw Exception('运行Assistant失败: ${response.body}');
    }
    
    final data = jsonDecode(response.body);
    return data['id'];
  }
  
  /// 轮询运行状态
  Future<void> _pollRunStatus({
    required String threadId,
    required String runId,
    required Completer<Map<String, dynamic>> completer,
    required StreamingCallback? onStream,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('https://api.openai.com/v1/threads/$threadId/runs/$runId'),
        headers: {
          'Authorization': 'Bearer ${_adapter.apiKey}',
          'OpenAI-Beta': 'assistants=v1',
        },
      );
      
      if (response.statusCode != 200) {
        throw Exception('获取运行状态失败: ${response.body}');
      }
      
      final data = jsonDecode(response.body);
      final status = data['status'];
      
      if (status == 'completed') {
        // 运行完成
        if (!completer.isCompleted) {
          completer.complete(data);
        }
        return;
      } else if (status == 'failed') {
        // 运行失败
        if (!completer.isCompleted) {
          completer.completeError('Assistant运行失败: ${data['last_error']}');
        }
        return;
      } else if (status == 'cancelled') {
        // 运行取消
        if (!completer.isCompleted) {
          completer.completeError('Assistant运行被取消');
        }
        return;
      } else if (status == 'requires_action') {
        // 需要执行工具调用
        await _handleToolCallsRequired(threadId, runId, data, completer);
        return;
      }
      
      // 将部分数据发送到流回调
      if (onStream != null && status == 'in_progress') {
        final stepResponse = await http.get(
          Uri.parse('https://api.openai.com/v1/threads/$threadId/runs/$runId/steps'),
          headers: {
            'Authorization': 'Bearer ${_adapter.apiKey}',
            'OpenAI-Beta': 'assistants=v1',
          },
        );
        
        if (stepResponse.statusCode == 200) {
          final stepData = jsonDecode(stepResponse.body);
          if (stepData['data'] != null && stepData['data'].isNotEmpty) {
            final step = stepData['data'][0];
            if (step['step_details'] != null && 
                step['step_details']['message_creation'] != null) {
              onStream('正在生成回复...');
            }
          }
        }
      }
      
      // 继续轮询
      await Future.delayed(const Duration(milliseconds: 500));
      _pollRunStatus(
        threadId: threadId,
        runId: runId,
        completer: completer,
        onStream: onStream,
      );
    } catch (e, stackTrace) {
      _logger.error('轮询运行状态失败: $e', stackTrace);
      if (!completer.isCompleted) {
        completer.completeError(e);
      }
    }
  }
  
  /// 处理需要工具调用的情况
  Future<void> _handleToolCallsRequired(
    String threadId,
    String runId,
    Map<String, dynamic> data,
    Completer<Map<String, dynamic>> completer,
  ) async {
    final toolCalls = data['required_action']['submit_tool_outputs']['tool_calls'];
    final toolOutputs = [];
    
    for (final toolCall in toolCalls) {
      try {
        final toolName = toolCall['function']['name'];
        final parameters = jsonDecode(toolCall['function']['arguments']);
        
        // 执行工具调用（这里需要集成工具注册表）
        final result = await _executeToolCall(toolName, parameters);
        
        toolOutputs.add({
          'tool_call_id': toolCall['id'],
          'output': result.output,
        });
      } catch (e) {
        toolOutputs.add({
          'tool_call_id': toolCall['id'],
          'output': '执行工具调用失败: $e',
        });
      }
    }
    
    // 提交工具输出
    await _submitToolOutputs(threadId, runId, toolOutputs);
    
    // 继续轮询
    await Future.delayed(const Duration(milliseconds: 500));
    _pollRunStatus(
      threadId: threadId,
      runId: runId,
      completer: completer,
      onStream: null, // 工具执行后不再发送流更新
    );
  }
  
  /// 执行工具调用（需要集成工具注册表）
  Future<ToolCallResult> _executeToolCall(
    String toolName,
    Map<String, dynamic> parameters,
  ) async {
    // 这里需要集成工具注册表
    // 临时实现，实际应该调用工具注册表
    return ToolCallResult.success('工具 $toolName 执行成功（模拟结果）');
  }
  
  /// 提交工具输出
  Future<void> _submitToolOutputs(
    String threadId,
    String runId,
    List<Map<String, dynamic>> toolOutputs,
  ) async {
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/threads/$threadId/runs/$runId/submit_tool_outputs'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${_adapter.apiKey}',
        'OpenAI-Beta': 'assistants=v1',
      },
      body: jsonEncode({
        'tool_outputs': toolOutputs,
      }),
    );
    
    if (response.statusCode != 200) {
      throw Exception('提交工具输出失败: ${response.body}');
    }
  }
  
  /// 取消运行
  Future<void> _cancelRun(String threadId, String runId) async {
    try {
      await http.post(
        Uri.parse('https://api.openai.com/v1/threads/$threadId/runs/$runId/cancel'),
        headers: {
          'Authorization': 'Bearer ${_adapter.apiKey}',
          'OpenAI-Beta': 'assistants=v1',
        },
      );
    } catch (e) {
      _logger.error('取消运行失败: $e');
    }
  }
  
  /// 获取线程消息
  Future<List<Map<String, dynamic>>> _getThreadMessages(String threadId) async {
    final response = await http.get(
      Uri.parse('https://api.openai.com/v1/threads/$threadId/messages'),
      headers: {
        'Authorization': 'Bearer ${_adapter.apiKey}',
        'OpenAI-Beta': 'assistants=v1',
      },
    );
    
    if (response.statusCode != 200) {
      throw Exception('获取线程消息失败: ${response.body}');
    }
    
    final data = jsonDecode(response.body);
    return List<Map<String, dynamic>>.from(data['data']);
  }
  
  /// 上传文件到Assistant
  Future<String> uploadFile(List<int> fileBytes, String filename, String purpose) async {
    if (_adapter is! OpenAIAdapter) {
      throw UnsupportedError('文件上传仅支持OpenAI提供商');
    }
    
    final uri = Uri.parse('https://api.openai.com/v1/files');
    
    final request = http.MultipartRequest('POST', uri)
      ..headers.addAll({
        'Authorization': 'Bearer ${_adapter.apiKey}',
      })
      ..fields['purpose'] = purpose
      ..files.add(
        http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: filename,
        ),
      );
    
    final response = await request.send();
    final responseBody = await response.stream.bytesToString();
    
    if (response.statusCode != 200) {
      throw Exception('上传文件失败: $responseBody');
    }
    
    final data = jsonDecode(responseBody);
    return data['id'];
  }
  
  /// 生成嵌入向量
  Future<List<double>> generateEmbeddings(String text) async {
    try {
      _logger.info('生成嵌入向量');
      
      final result = await _adapter.generateEmbeddings(text);
      
      _logger.info('生成嵌入向量成功');
      return result;
    } catch (e, stackTrace) {
      _logger.severe('生成嵌入向量失败: $e', stackTrace);
      rethrow;
    }
  }
  
  /// 设置模型提供商
  void setModelProvider(ModelServiceConfig config) {
    _initializeAdapter(config);
  }
  
  /// 获取当前模型提供商名称
  String getProviderName() {
    return _adapter.providerType.toString().split('.').last;
  }
  
  /// 获取当前默认模型名称
  String getDefaultModelName() {
    return _adapter.defaultModel;
  }
  
  /// 是否启用了Assistants API
  bool get useAssistantsApi => _useAssistantsApi;
  
  /// 获取API密钥(谨慎使用)
  String get apiKey => _adapter.apiKey;
  
  @override
  Future<AgentMessage> chat(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async {
    try {
      // 将消息转换为Message对象
      final convertedMessages = messages.map((message) {
        final type = _getMessageType(message['role'].toString());
        return Message(
          type: type,
          content: message['content'].toString(),
          metadata: message,
        );
      }).toList();
      
      // 使用generateChatResponse生成回复
      final response = await generateChatResponse(
        messages: convertedMessages,
        tools: tools,
        options: options,
      );
      
      // 将Message对象转换为AgentMessage
      return AgentMessage.assistant(
        content: response.content,
        toolCalls: response.toolCalls,
        id: response.metadata?['id'] as String?,
      );
    } catch (e, stackTrace) {
      _logger.severe('Chat调用失败: $e', stackTrace);
      return AgentMessage.assistant(
        content: '生成回复失败: $e',
        status: AgentMessageStatus.error,
      );
    }
  }
  
  @override
  Stream<AgentMessage> chatStream(
    List<Map<String, dynamic>> messages, {
    Map<String, dynamic>? options,
    List<Map<String, dynamic>>? tools,
  }) async* {
    try {
      // 将消息转换为Message对象
      final convertedMessages = messages.map((message) {
        final type = _getMessageType(message['role'].toString());
        return Message(
          type: type,
          content: message['content'].toString(),
          metadata: message,
        );
      }).toList();
      
      // 创建初始响应消息
      final responseMessage = AgentMessage.assistant(
        content: '',
        status: AgentMessageStatus.streaming,
      );
      
      // 添加onStream回调
      StreamController<String> streamController = StreamController<String>();
      
      // 监听流并更新响应消息
      streamController.stream.listen((String textDelta) {
        responseMessage.content += textDelta;
      });
      
      // 启动生成过程
      generateChatResponse(
        messages: convertedMessages,
        tools: tools,
        options: options,
        onStream: (textDelta) {
          streamController.add(textDelta);
        }
      ).then((finalResponse) {
        // 如果有工具调用，更新响应
        if (finalResponse.toolCalls != null && finalResponse.toolCalls!.isNotEmpty) {
          responseMessage.updateWithToolCalls(
            finalResponse.toolCalls!.map((tc) => AgentToolCall(
              id: tc.id,
              name: tc.toolName,
              arguments: jsonEncode(tc.parameters),
            )).toList()
          );
        }
        // 完成流
        responseMessage.completeStreaming();
        streamController.close();
      }).catchError((e) {
        streamController.addError(e);
        streamController.close();
      });
      
      // 每次流更新时生成新的响应
      yield responseMessage;
      
      // 定期轮询更新
      while (responseMessage.status == AgentMessageStatus.streaming) {
        await Future.delayed(const Duration(milliseconds: 100));
        yield responseMessage.copy();
      }
    } catch (e, stackTrace) {
      _logger.severe('ChatStream调用失败: $e', stackTrace);
      yield AgentMessage.assistant(
        content: '生成流式回复失败: $e',
        status: AgentMessageStatus.error,
      );
    }
  }
  
  @override
  Future<List<double>> generateEmbedding(String text) async {
    try {
      return await generateEmbeddings(text);
    } catch (e) {
      _logger.severe('生成嵌入向量失败: $e');
      throw Exception('生成嵌入向量失败: $e');
    }
  }
  
  @override
  Future<List<String>> getAvailableModels(ModelType type) async {
    try {
      final providerName = getProviderName().toLowerCase();
      
      switch (providerName) {
        case 'baidu':
          switch (type) {
            case ModelType.chat:
              return ['ernie-bot', 'ernie-bot-4', 'ernie-bot-turbo'];
            case ModelType.embedding:
              return ['ernie-embedding-v1'];
            case ModelType.multimodal:
              return ['ernie-vilg-v2'];
            case ModelType.speech:
              return ['ernie-speed-speech'];
          }
        case 'deepseek':
          return ['deepseek-coder', 'deepseek-chat', 'deepseek-v2'];
        case 'alibaba':
          return ['qwen-turbo', 'qwen-max', 'qwen-plus'];
        case 'iflytek':
          return ['spark-1.5', 'spark-2.0', 'spark-3.0', 'spark-3.5'];
        default:
          return ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'claude-3'];
      }
    } catch (e) {
      _logger.severe('获取可用模型失败: $e');
      return [];
    }
  }
  
  // 辅助方法：根据角色字符串确定消息类型
  MessageType _getMessageType(String role) {
    switch (role.toLowerCase()) {
      case 'system':
        return MessageType.system;
      case 'user':
        return MessageType.user;
      case 'assistant':
        return MessageType.assistant;
      case 'tool':
        return MessageType.tool;
      default:
        return MessageType.user;
    }
  }
} 