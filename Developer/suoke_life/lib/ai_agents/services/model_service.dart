// 模型服务类
// 用于与LLM API进行交互

import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/agent_config.dart';
import '../utils/logger.dart';

/// 聊天消息角色
enum ChatRole {
  system,   // 系统消息
  user,     // 用户消息
  assistant, // 助手消息
  tool      // 工具消息
}

/// 聊天消息
class ChatMessage {
  /// 消息角色
  final ChatRole role;
  
  /// 消息内容
  final String content;
  
  /// 工具调用结果（当role为tool时使用）
  final Map<String, dynamic>? toolResult;
  
  /// 消息名称或ID
  final String? name;
  
  /// 构造函数
  const ChatMessage({
    required this.role,
    required this.content,
    this.toolResult,
    this.name,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    final result = {
      'role': _roleToString(role),
      'content': content,
    };
    
    if (name != null) {
      result['name'] = name;
    }
    
    if (toolResult != null && role == ChatRole.tool) {
      result['tool_call_id'] = toolResult!['tool_call_id'];
      result['content'] = jsonEncode(toolResult!['result']);
    }
    
    return result;
  }
  
  /// 角色转字符串
  static String _roleToString(ChatRole role) {
    switch (role) {
      case ChatRole.system:
        return 'system';
      case ChatRole.user:
        return 'user';
      case ChatRole.assistant:
        return 'assistant';
      case ChatRole.tool:
        return 'tool';
    }
  }
}

/// 模型调用选项
class ModelOptions {
  /// 模型名称
  final String modelName;
  
  /// 温度
  final double temperature;
  
  /// 最大tokens
  final int maxTokens;
  
  /// 启用工具
  final bool enableTools;
  
  /// 工具定义
  final List<Map<String, dynamic>>? tools;
  
  /// 构造函数
  const ModelOptions({
    this.modelName = 'deepseek-chat',
    this.temperature = 0.7,
    this.maxTokens = 2000,
    this.enableTools = false,
    this.tools,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    final result = {
      'model': modelName,
      'temperature': temperature,
      'max_tokens': maxTokens,
    };
    
    if (enableTools && tools != null) {
      result['tools'] = tools;
    }
    
    return result;
  }
}

/// 模型服务类
class ModelService {
  /// HTTP客户端
  final http.Client _client;
  
  /// API密钥
  final String _apiKey;
  
  /// 构造函数
  ModelService({
    http.Client? client,
    String? apiKey,
  }) : 
    _client = client ?? http.Client(),
    _apiKey = apiKey ?? '';
  
  /// 调用聊天模型
  Future<Map<String, dynamic>> chatCompletion({
    required List<ChatMessage> messages,
    ModelOptions options = const ModelOptions(),
    Duration timeout = const Duration(seconds: 30),
    int retries = 3,
  }) async {
    final apiUrl = AgentConfig.getModelEndpoint(options.modelName);
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_apiKey',
    };
    
    final body = jsonEncode({
      ...options.toMap(),
      'messages': messages.map((m) => m.toMap()).toList(),
    });
    
    LoggerUtil.debug('模型请求: $apiUrl');
    LoggerUtil.debug('模型请求体: $body');
    
    for (int attempt = 0; attempt < retries; attempt++) {
      try {
        final response = await _client.post(
          Uri.parse(apiUrl),
          headers: headers,
          body: body,
        ).timeout(timeout);
        
        if (response.statusCode == 200) {
          final jsonResponse = jsonDecode(response.body);
          LoggerUtil.debug('模型响应: ${response.body}');
          return jsonResponse;
        } else {
          final error = 'API调用失败: ${response.statusCode} - ${response.body}';
          LoggerUtil.error(error);
          
          if (attempt == retries - 1) {
            throw Exception(error);
          }
        }
      } catch (e) {
        final error = '模型调用异常: ${e.toString()}';
        LoggerUtil.error(error);
        
        if (attempt == retries - 1) {
          throw Exception(error);
        }
        
        // 指数退避重试
        final delay = Duration(milliseconds: AgentConfig.retryDelayMs * (1 << attempt));
        await Future.delayed(delay);
      }
    }
    
    throw Exception('达到最大重试次数');
  }
  
  /// 从响应中提取文本
  String extractTextFromResponse(Map<String, dynamic> response) {
    try {
      return response['choices'][0]['message']['content'] ?? '';
    } catch (e) {
      LoggerUtil.error('提取响应文本异常: ${e.toString()}');
      return '';
    }
  }
  
  /// 从响应中提取工具调用
  List<Map<String, dynamic>> extractToolCalls(Map<String, dynamic> response) {
    try {
      final message = response['choices'][0]['message'];
      final toolCalls = message['tool_calls'];
      
      if (toolCalls == null) {
        return [];
      }
      
      return List<Map<String, dynamic>>.from(toolCalls);
    } catch (e) {
      LoggerUtil.error('提取工具调用异常: ${e.toString()}');
      return [];
    }
  }
  
  /// 创建简单的文本完成请求
  Future<String> simpleCompletion({
    required String prompt,
    String modelName = 'deepseek-chat',
    double temperature = 0.7,
  }) async {
    final messages = [
      ChatMessage(
        role: ChatRole.user,
        content: prompt,
      ),
    ];
    
    final options = ModelOptions(
      modelName: modelName,
      temperature: temperature,
    );
    
    final response = await chatCompletion(
      messages: messages,
      options: options,
    );
    
    return extractTextFromResponse(response);
  }
  
  /// 释放资源
  void dispose() {
    _client.close();
  }
}