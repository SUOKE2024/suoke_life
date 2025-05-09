import 'package:suoke_life/ai_agents/models/llm_model.dart';

/// 大语言模型服务接口
abstract class LLMService {
  /// 初始化服务
  Future<void> initialize();
  
  /// 设置模型类型
  Future<void> setModelType(LLMType modelType);
  
  /// 获取当前使用的模型类型
  LLMType getCurrentModelType();
  
  /// 发送消息并获取回复
  Future<LLMResponse> sendMessage({
    required List<LLMMessage> messages,
    double temperature = 0.7,
    int maxTokens = 800,
  });
  
  /// 发送单条用户消息并获取回复（简化版）
  Future<String> chat({
    required String userMessage, 
    String? systemMessage,
    List<LLMMessage>? historyMessages,
    double temperature = 0.7,
    int maxTokens = 800,
  });
  
  /// 流式获取回复（用于实时显示回复过程）
  Stream<String> streamChat({
    required String userMessage,
    String? systemMessage,
    List<LLMMessage>? historyMessages,
    double temperature = 0.7,
    int maxTokens = 800,
  });
}