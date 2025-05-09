import 'package:suoke_life/ai_agents/models/llm_model.dart';
import 'package:suoke_life/ai_agents/services/deepseek_service.dart';
import 'package:suoke_life/ai_agents/services/llm_service.dart';
import 'package:suoke_life/ai_agents/config/agent_prompts.dart';
import 'package:suoke_life/domain/models/agent_model.dart';

/// 大语言模型管理器
/// 
/// 用于管理和协调不同的大语言模型服务
class LLMManager {
  /// 当前使用的LLM服务
  late LLMService _currentService;
  
  /// 单例实例
  static final LLMManager _instance = LLMManager._internal();
  
  /// 单例访问器
  factory LLMManager() => _instance;
  
  /// 私有构造函数
  LLMManager._internal() {
    // 默认使用DeepSeek模型
    _currentService = DeepSeekService();
  }
  
  /// 初始化LLM管理器
  Future<void> initialize() async {
    await _currentService.initialize();
  }
  
  /// 切换LLM模型类型
  Future<void> switchModelType(LLMType modelType) async {
    await _currentService.setModelType(modelType);
  }
  
  /// 获取当前LLM服务
  LLMService get currentService => _currentService;
  
  /// 发送聊天消息并获取回复
  Future<String> chat({
    required String message,
    String? systemPrompt,
    List<LLMMessage>? history,
    double temperature = 0.7,
  }) async {
    return await _currentService.chat(
      userMessage: message,
      systemMessage: systemPrompt,
      historyMessages: history,
      temperature: temperature,
    );
  }
  
  /// 流式获取聊天回复
  Stream<String> streamChat({
    required String message,
    String? systemPrompt,
    List<LLMMessage>? history,
    double temperature = 0.7,
  }) {
    return _currentService.streamChat(
      userMessage: message,
      systemMessage: systemPrompt,
      historyMessages: history,
      temperature: temperature,
    );
  }
}

/// 获取不同智能体的系统提示词
String getAgentSystemPrompt(AgentType agentType) {
  return getAgentSystemPromptByType(agentType);
}

/// 中医体质类型枚举
enum ConstitutionType {
  /// 平和质
  balanced,
  
  /// 气虚质
  qiDeficiency,
  
  /// 阳虚质
  yangDeficiency,
  
  /// 阴虚质
  yinDeficiency,
  
  /// 痰湿质
  phlegmDampness,
  
  /// 湿热质
  dampnessHeat,
  
  /// 血瘀质
  bloodStasis,
  
  /// 气郁质
  qiStagnation,
  
  /// 特禀质
  specialConstitution,
}