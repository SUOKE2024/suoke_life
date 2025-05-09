import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:suoke_life/ai_agents/models/llm_model.dart';
import 'package:suoke_life/ai_agents/services/llm_service.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// DeepSeek API服务实现
class DeepSeekService implements LLMService {
  /// API密钥
  late final String _apiKey;
  
  /// API基础URL
  final String _baseUrl = 'https://api.deepseek.com/v1';
  
  /// 模型类型
  LLMType _modelType = LLMType.deepSeek;
  
  /// Dio HTTP客户端
  late final Dio _dio;
  
  /// 日志工具
  final AppLogger _logger = AppLogger();
  
  /// 当前使用的模型名称
  String _currentModel = 'deepseek-chat';
  
  /// 单例实例
  static final DeepSeekService _instance = DeepSeekService._internal();
  
  /// 单例访问器
  factory DeepSeekService() => _instance;
  
  /// 私有构造函数
  DeepSeekService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));
    
    _setupInterceptors();
  }
  
  /// 配置拦截器
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          options.headers['Authorization'] = 'Bearer $_apiKey';
          _logger.d('DeepSeek请求: ${options.method} ${options.path}');
          return handler.next(options);
        },
        onResponse: (response, handler) {
          _logger.d('DeepSeek响应: ${response.statusCode}');
          return handler.next(response);
        },
        onError: (DioException error, handler) {
          _logger.e(
            'DeepSeek错误: ${error.requestOptions.path}',
            error,
            error.stackTrace,
          );
          return handler.reject(error);
        },
      ),
    );
  }
  
  @override
  Future<void> initialize() async {
    // 从环境变量中获取API密钥
    _apiKey = dotenv.env['DEEPSEEK_API_KEY'] ?? '';
    
    if (_apiKey.isEmpty) {
      _logger.w('DeepSeek API密钥未设置，使用模拟模式');
      // 使用模拟密钥而不是抛出异常
      _apiKey = 'mock_api_key_for_development';
    }
    
    _logger.i('DeepSeek服务初始化完成');
  }
  
  @override
  Future<void> setModelType(LLMType modelType) async {
    _modelType = modelType;
    
    // 根据不同的模型类型设置不同的模型名称
    switch (modelType) {
      case LLMType.deepSeek:
        _currentModel = 'deepseek-chat';
        break;
      default:
        _currentModel = 'deepseek-chat';
        break;
    }
    
    _logger.i('已切换至模型: $_currentModel');
  }
  
  @override
  LLMType getCurrentModelType() {
    return _modelType;
  }
  
  @override
  Future<LLMResponse> sendMessage({
    required List<LLMMessage> messages,
    double temperature = 0.7,
    int maxTokens = 800,
  }) async {
    // 使用模拟数据模式
    if (_apiKey == 'mock_api_key_for_development') {
      _logger.i('使用模拟数据模式，返回固定回复');
      return LLMResponse(
        content: '这是来自索克智能助手的模拟回复。在开发环境中，我们使用模拟数据替代真实API调用。',
        model: _currentModel,
        requestId: 'mock-request-id',
        totalTokens: 30,
        finishReason: 'stop',
      );
    }
    
    try {
      // 构建请求体
      final requestData = {
        'model': _currentModel,
        'messages': messages.map((msg) => msg.toDeepSeekJson()).toList(),
        'temperature': temperature,
        'max_tokens': maxTokens,
      };
      
      // 发送请求
      final response = await _dio.post<Map<String, dynamic>>(
        '/chat/completions',
        data: requestData,
      );
      
      // 处理响应
      return LLMResponse.fromDeepSeekJson(response.data!);
    } catch (e) {
      _logger.e('发送消息至DeepSeek出错', e);
      throw Exception('DeepSeek API调用失败: ${e.toString()}');
    }
  }
  
  @override
  Future<String> chat({
    required String userMessage,
    String? systemMessage,
    List<LLMMessage>? historyMessages,
    double temperature = 0.7,
    int maxTokens = 800,
  }) async {
    // 构建消息列表
    final messages = <LLMMessage>[];
    
    // 添加系统消息
    if (systemMessage != null && systemMessage.isNotEmpty) {
      messages.add(LLMMessage(
        role: LLMMessageType.system,
        content: systemMessage,
      ));
    }
    
    // 添加历史消息
    if (historyMessages != null && historyMessages.isNotEmpty) {
      messages.addAll(historyMessages);
    }
    
    // 添加用户当前消息
    messages.add(LLMMessage(
      role: LLMMessageType.user,
      content: userMessage,
    ));
    
    // 发送请求
    final response = await sendMessage(
      messages: messages,
      temperature: temperature,
      maxTokens: maxTokens,
    );
    
    return response.content;
  }
  
  @override
  Stream<String> streamChat({
    required String userMessage,
    String? systemMessage,
    List<LLMMessage>? historyMessages,
    double temperature = 0.7,
    int maxTokens = 800,
  }) async* {
    // 使用模拟数据模式
    if (_apiKey == 'mock_api_key_for_development') {
      _logger.i('使用模拟数据模式，返回固定流式回复');
      
      // 模拟流式响应，每300毫秒返回一段文字
      final mockResponse = '这是来自索克智能助手的模拟流式回复。在开发环境中，我们使用模拟数据替代真实API调用。';
      final words = mockResponse.split(' ');
      
      for (final word in words) {
        await Future.delayed(const Duration(milliseconds: 300));
        yield '$word ';
      }
      
      return;
    }
    
    try {
      // 构建消息列表
      final messages = <LLMMessage>[];
      
      // 添加系统消息
      if (systemMessage != null && systemMessage.isNotEmpty) {
        messages.add(LLMMessage(
          role: LLMMessageType.system,
          content: systemMessage,
        ));
      }
      
      // 添加历史消息
      if (historyMessages != null && historyMessages.isNotEmpty) {
        messages.addAll(historyMessages);
      }
      
      // 添加用户当前消息
      messages.add(LLMMessage(
        role: LLMMessageType.user,
        content: userMessage,
      ));
      
      // 构建请求体
      final requestData = {
        'model': _currentModel,
        'messages': messages.map((msg) => msg.toDeepSeekJson()).toList(),
        'temperature': temperature,
        'max_tokens': maxTokens,
        'stream': true,
      };
      
      // 发送流式请求
      final response = await _dio.post<ResponseBody>(
        '/chat/completions',
        data: requestData,
        options: Options(
          responseType: ResponseType.stream,
        ),
      );
      
      // 处理流式响应
      final completer = Completer<void>();
      final streamController = StreamController<String>();
      
      response.data!.stream.listen(
        (data) {
          // 解析SSE数据
          final chunks = utf8.decode(data).split('\n\n');
          
          for (final chunk in chunks) {
            if (chunk.startsWith('data: ') && !chunk.contains('data: [DONE]')) {
              final jsonData = chunk.substring(6);
              try {
                final parsedData = json.decode(jsonData) as Map<String, dynamic>;
                final content = parsedData['choices'][0]['delta']['content'] as String?;
                
                if (content != null && content.isNotEmpty) {
                  streamController.add(content);
                }
              } catch (e) {
                _logger.e('解析SSE数据出错', e);
              }
            }
          }
        },
        onDone: () {
          completer.complete();
          streamController.close();
        },
        onError: (error) {
          _logger.e('流式请求出错', error);
          completer.completeError(error);
          streamController.addError(error);
          streamController.close();
        },
        cancelOnError: true,
      );
      
      // 等待消息流处理完成
      yield* streamController.stream;
      
      // 避免关闭还未完成的流请求
      unawaited(completer.future);
    } catch (e) {
      _logger.e('流式调用DeepSeek出错', e);
      throw Exception('DeepSeek流式API调用失败: ${e.toString()}');
    }
  }
}

// 忽略未使用的返回值的警告
void unawaited(Future<void> future) {}