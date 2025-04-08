// 百度文心一言模型提供商适配器
// 用于接入百度文心一言API服务

import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/agent_message.dart';
import '../../models/agent_response.dart';
import '../../utils/logger.dart';
import '../model_provider_adapter.dart';

/// 百度文心一言适配器
class BaiduProviderAdapter implements ModelProviderAdapter {
  /// HTTP客户端
  final http.Client _client;
  
  /// API密钥
  final String _apiKey;
  
  /// 密钥
  final String _secretKey;
  
  /// 访问令牌
  String? _accessToken;
  
  /// 访问令牌过期时间
  DateTime? _tokenExpireTime;
  
  /// API基础URL
  static const String _baseUrl = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop';
  
  /// 获取访问令牌URL
  static const String _tokenUrl = 'https://aip.baidubce.com/oauth/2.0/token';
  
  /// 模型映射
  static const Map<String, String> _modelMapping = {
    'ernie-bot-4': 'completions_pro', // Ernie Bot 4.0
    'ernie-bot-8k': 'ernie_bot_8k',   // Ernie Bot 8K
    'ernie-bot-turbo': 'eb-instant',  // Ernie Bot Turbo
    'ernie-speed': 'ernie_speed',     // Ernie Speed
    'ernie-lite': 'ernie_lite',       // Ernie Lite
    'default': 'completions_pro',     // 默认使用Ernie Bot 4.0
  };
  
  /// 构造函数
  BaiduProviderAdapter({
    required String apiKey,
    required String secretKey,
    http.Client? client,
  }) : 
    _apiKey = apiKey,
    _secretKey = secretKey,
    _client = client ?? http.Client();
  
  @override
  ModelProviderType get providerType => ModelProviderType.baidu;
  
  @override
  String get providerName => '百度文心一言';
  
  @override
  List<String> getSupportedModels() {
    return _modelMapping.keys.toList();
  }
  
  @override
  Future<bool> isModelAvailable(String modelName) async {
    try {
      // 判断模型名称是否在映射表中
      final modelPath = _getModelPath(modelName);
      return modelPath.isNotEmpty;
    } catch (e) {
      LoggerUtil.error('检查模型可用性异常: ${e.toString()}');
      return false;
    }
  }
  
  @override
  Future<AgentResponse> chatCompletion({
    required List<AgentMessage> messages,
    required ModelCallOptions options,
    Duration timeout = const Duration(seconds: 30),
    int retries = 3,
  }) async {
    try {
      // 确保有有效的访问令牌
      await _ensureAccessToken();
      
      // 准备API请求
      final modelPath = _getModelPath(options.modelName);
      final apiUrl = '$_baseUrl/$modelPath';
      
      // 转换消息格式
      final convertedMessages = _convertMessages(messages);
      
      // 准备请求体
      final requestBody = {
        'messages': convertedMessages,
        'temperature': options.temperature,
        'top_p': 0.8,
      };
      
      if (options.maxTokens > 0) {
        requestBody['max_output_tokens'] = options.maxTokens;
      }
      
      // 工具支持（只有ernie-bot-4支持工具）
      if (options.enableTools && 
          options.tools != null && 
          options.tools!.isNotEmpty &&
          options.modelName == 'ernie-bot-4') {
        requestBody['tools'] = options.tools!.map((tool) => {
          'name': tool.name,
          'description': tool.description,
          'parameters': tool.parameters,
        }).toList();
        requestBody['tool_choice'] = 'auto';
      }
      
      // 发送API请求
      final headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };
      
      final response = await _client.post(
        Uri.parse('$apiUrl?access_token=$_accessToken'),
        headers: headers,
        body: jsonEncode(requestBody),
      ).timeout(timeout);
      
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        
        // 处理错误响应
        if (jsonResponse.containsKey('error_code')) {
          final errorMsg = '百度API错误: ${jsonResponse['error_code']} - ${jsonResponse['error_msg']}';
          LoggerUtil.error(errorMsg);
          throw Exception(errorMsg);
        }
        
        // 解析响应
        return _parseResponse(jsonResponse, options);
      } else {
        final error = '百度API调用失败: ${response.statusCode} - ${response.body}';
        LoggerUtil.error(error);
        throw Exception(error);
      }
    } catch (e) {
      final error = '百度模型调用异常: ${e.toString()}';
      LoggerUtil.error(error);
      throw Exception(error);
    }
  }
  
  @override
  Stream<AgentResponseChunk> streamChatCompletion({
    required List<AgentMessage> messages,
    required ModelCallOptions options,
    Duration timeout = const Duration(seconds: 60),
    int retries = 3,
  }) async* {
    try {
      // 确保有有效的访问令牌
      await _ensureAccessToken();
      
      // 准备API请求
      final modelPath = _getModelPath(options.modelName);
      final apiUrl = '$_baseUrl/$modelPath';
      
      // 对于流式响应，添加_stream后缀
      final streamUrl = apiUrl.endsWith('_stream') ? apiUrl : '${apiUrl}_stream';
      
      // 转换消息格式
      final convertedMessages = _convertMessages(messages);
      
      // 准备请求体
      final requestBody = {
        'messages': convertedMessages,
        'temperature': options.temperature,
        'top_p': 0.8,
        'stream': true,
      };
      
      if (options.maxTokens > 0) {
        requestBody['max_output_tokens'] = options.maxTokens;
      }
      
      // 工具支持（只有ernie-bot-4支持工具）
      if (options.enableTools && 
          options.tools != null && 
          options.tools!.isNotEmpty &&
          options.modelName == 'ernie-bot-4') {
        requestBody['tools'] = options.tools!.map((tool) => {
          'name': tool.name,
          'description': tool.description,
          'parameters': tool.parameters,
        }).toList();
        requestBody['tool_choice'] = 'auto';
      }
      
      // 发送API请求
      final headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };
      
      final request = http.Request('POST', Uri.parse('$streamUrl?access_token=$_accessToken'));
      request.headers.addAll(headers);
      request.body = jsonEncode(requestBody);
      
      final streamedResponse = await _client.send(request).timeout(timeout);
      
      if (streamedResponse.statusCode == 200) {
        await for (final chunk in streamedResponse.stream) {
          final decodedChunk = utf8.decode(chunk);
          
          // 解析SSE格式数据
          for (final line in decodedChunk.split('\n')) {
            if (line.startsWith('data: ')) {
              final jsonData = line.substring(6).trim();
              if (jsonData == '[DONE]') {
                break;
              }
              
              try {
                final jsonResponse = jsonDecode(jsonData);
                // 解析流式响应
                final responseChunk = _parseStreamResponse(jsonResponse);
                yield responseChunk;
              } catch (e) {
                LoggerUtil.error('解析流式响应数据失败: $e, data: $jsonData');
              }
            }
          }
        }
      } else {
        final error = '百度API流式调用失败: ${streamedResponse.statusCode}';
        LoggerUtil.error(error);
        throw Exception(error);
      }
    } catch (e) {
      final error = '百度模型流式调用异常: ${e.toString()}';
      LoggerUtil.error(error);
      throw Exception(error);
    }
  }
  
  @override
  Future<List<double>> generateEmbedding({
    required String text,
    String? modelName,
  }) async {
    try {
      // 确保有有效的访问令牌
      await _ensureAccessToken();
      
      // 百度文心向量接口
      final apiUrl = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1';
      
      // 准备请求体
      final requestBody = {
        'input': [text],
      };
      
      // 发送API请求
      final headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };
      
      final response = await _client.post(
        Uri.parse('$apiUrl?access_token=$_accessToken'),
        headers: headers,
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        
        // 处理错误响应
        if (jsonResponse.containsKey('error_code')) {
          final errorMsg = '百度API错误: ${jsonResponse['error_code']} - ${jsonResponse['error_msg']}';
          LoggerUtil.error(errorMsg);
          throw Exception(errorMsg);
        }
        
        // 解析向量
        if (jsonResponse['data'] != null && 
            jsonResponse['data'].isNotEmpty && 
            jsonResponse['data'][0]['embedding'] != null) {
          return List<double>.from(jsonResponse['data'][0]['embedding']);
        }
        
        throw Exception('解析向量响应失败: $jsonResponse');
      } else {
        final error = '百度向量API调用失败: ${response.statusCode} - ${response.body}';
        LoggerUtil.error(error);
        throw Exception(error);
      }
    } catch (e) {
      final error = '百度向量调用异常: ${e.toString()}';
      LoggerUtil.error(error);
      throw Exception(error);
    }
  }
  
  @override
  void dispose() {
    _client.close();
  }
  
  /// 确保有有效的访问令牌
  Future<void> _ensureAccessToken() async {
    // 检查令牌是否存在且有效
    if (_accessToken != null && 
        _tokenExpireTime != null && 
        DateTime.now().isBefore(_tokenExpireTime!)) {
      return;
    }
    
    try {
      // 获取新的访问令牌
      final response = await _client.post(
        Uri.parse(_tokenUrl),
        body: {
          'grant_type': 'client_credentials',
          'client_id': _apiKey,
          'client_secret': _secretKey,
        },
      );
      
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _accessToken = jsonResponse['access_token'];
        
        // 设置过期时间（提前5分钟过期，以便安全刷新）
        final expiresIn = jsonResponse['expires_in'] as int;
        _tokenExpireTime = DateTime.now().add(Duration(seconds: expiresIn - 300));
        
        LoggerUtil.debug('百度访问令牌刷新成功，有效期至: $_tokenExpireTime');
      } else {
        final error = '获取百度访问令牌失败: ${response.statusCode} - ${response.body}';
        LoggerUtil.error(error);
        throw Exception(error);
      }
    } catch (e) {
      final error = '获取百度访问令牌异常: ${e.toString()}';
      LoggerUtil.error(error);
      throw Exception(error);
    }
  }
  
  /// 获取模型路径
  String _getModelPath(String modelName) {
    // 从映射表中获取模型路径，如果不存在则使用默认模型
    return _modelMapping[modelName] ?? _modelMapping['default'] ?? '';
  }
  
  /// 转换消息格式
  List<Map<String, dynamic>> _convertMessages(List<AgentMessage> messages) {
    return messages.map((msg) {
      final Map<String, dynamic> convertedMsg = {
        'role': _convertRole(msg.role),
      };
      
      // 处理内容
      if (msg.content != null && msg.content!.isNotEmpty) {
        convertedMsg['content'] = msg.content;
      }
      
      // 处理工具调用和工具响应
      if (msg.role == AgentMessageRole.assistant && msg.toolCalls != null && msg.toolCalls!.isNotEmpty) {
        // 百度API中工具调用需要特殊处理
        convertedMsg['function_call'] = {
          'name': msg.toolCalls![0].name,
          'arguments': msg.toolCalls![0].arguments,
        };
      } else if (msg.role == AgentMessageRole.tool && msg.toolCallId != null) {
        convertedMsg['name'] = msg.name ?? 'unknown_tool';
        convertedMsg['function_call'] = {
          'name': msg.name ?? 'unknown_tool',
          'arguments': msg.content,
        };
      }
      
      return convertedMsg;
    }).toList();
  }
  
  /// 转换角色
  String _convertRole(AgentMessageRole role) {
    switch (role) {
      case AgentMessageRole.system:
        return 'system';
      case AgentMessageRole.user:
        return 'user';
      case AgentMessageRole.assistant:
        return 'assistant';
      case AgentMessageRole.tool:
        return 'function';
      default:
        return 'user';
    }
  }
  
  /// 解析响应
  AgentResponse _parseResponse(Map<String, dynamic> response, ModelCallOptions options) {
    try {
      final result = response['result'] ?? '';
      
      // 处理工具调用
      List<AgentToolCall>? toolCalls;
      if (response['function_call'] != null) {
        toolCalls = [
          AgentToolCall(
            id: '${DateTime.now().millisecondsSinceEpoch}',
            name: response['function_call']['name'],
            arguments: response['function_call']['arguments'],
          )
        ];
      }
      
      // 创建响应对象
      return AgentResponse(
        id: response['id'] ?? 'baidu_${DateTime.now().millisecondsSinceEpoch}',
        model: options.modelName,
        content: result,
        toolCalls: toolCalls,
        usage: AgentUsage(
          promptTokens: response['usage']?['prompt_tokens'] ?? 0,
          completionTokens: response['usage']?['completion_tokens'] ?? 0,
          totalTokens: response['usage']?['total_tokens'] ?? 0,
        ),
      );
    } catch (e) {
      LoggerUtil.error('解析百度响应异常: ${e.toString()}');
      throw Exception('解析百度响应失败: ${e.toString()}');
    }
  }
  
  /// 解析流式响应
  AgentResponseChunk _parseStreamResponse(Map<String, dynamic> response) {
    try {
      final result = response['result'] ?? '';
      
      // 处理工具调用
      List<AgentToolCall>? toolCalls;
      if (response['function_call'] != null) {
        toolCalls = [
          AgentToolCall(
            id: '${DateTime.now().millisecondsSinceEpoch}',
            name: response['function_call']['name'],
            arguments: response['function_call']['arguments'],
          )
        ];
      }
      
      // 创建响应对象
      return AgentResponseChunk(
        id: response['id'] ?? 'baidu_stream_${DateTime.now().millisecondsSinceEpoch}',
        content: result,
        toolCalls: toolCalls,
        isComplete: response['is_end'] ?? false,
      );
    } catch (e) {
      LoggerUtil.error('解析百度流式响应异常: ${e.toString()}');
      throw Exception('解析百度流式响应失败: ${e.toString()}');
    }
  }
} 