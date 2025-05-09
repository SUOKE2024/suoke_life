/// 大语言模型类型枚举
enum LLMType {
  /// DeepSeek模型，默认使用
  deepSeek,
  
  /// 百度文心一言
  ernieBot,
  
  /// 智谱清言
  chatGLM,
  
  /// 通义千问
  tongYi,
}

/// 大语言模型响应
class LLMResponse {
  /// 响应内容
  final String content;
  
  /// 模型名称
  final String model;
  
  /// 请求ID
  final String requestId;
  
  /// 使用的tokens
  final int totalTokens;
  
  /// 完成的原因
  final String finishReason;
  
  /// 构造函数
  LLMResponse({
    required this.content,
    required this.model,
    required this.requestId,
    required this.totalTokens,
    required this.finishReason,
  });
  
  /// 从DeepSeek响应JSON创建实例
  factory LLMResponse.fromDeepSeekJson(Map<String, dynamic> json) {
    final choice = json['choices'][0];
    
    return LLMResponse(
      content: choice['message']['content'],
      model: json['model'],
      requestId: json['id'],
      totalTokens: json['usage']['total_tokens'],
      finishReason: choice['finish_reason'],
    );
  }
}

/// LLM消息类型枚举
enum LLMMessageType {
  /// 系统消息
  system,
  
  /// 用户消息
  user,
  
  /// 助手消息
  assistant,
}

/// LLM消息
class LLMMessage {
  /// 消息类型
  final LLMMessageType role;
  
  /// 消息内容
  final String content;
  
  /// 构造函数
  LLMMessage({
    required this.role,
    required this.content,
  });
  
  /// 转换为DeepSeek接口格式
  Map<String, String> toDeepSeekJson() {
    String roleStr;
    
    switch (role) {
      case LLMMessageType.system:
        roleStr = 'system';
        break;
      case LLMMessageType.user:
        roleStr = 'user';
        break;
      case LLMMessageType.assistant:
        roleStr = 'assistant';
        break;
    }
    
    return {
      'role': roleStr,
      'content': content,
    };
  }
}