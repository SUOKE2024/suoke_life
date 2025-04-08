// 智能体工厂类
// 用于创建和管理不同类型的智能体

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/agent_message.dart';
import '../models/agent_response.dart';
import '../services/model_provider_adapter.dart';
import '../rag/enhanced_rag_service.dart';

/// 智能体类型
enum AgentType {
  /// 健康顾问
  healthAdvisor,
  
  /// 中医咨询
  tcmConsultant,
  
  /// 营养师
  nutritionist,
  
  /// 运动教练
  fitnessCoach,
  
  /// 知识检索
  knowledgeRetrieval,
  
  /// 生活助手
  lifeAssistant,
}

/// 智能体创建参数
class AgentCreateParams {
  /// 智能体类型
  final AgentType type;
  
  /// 自定义系统提示
  final String? systemPrompt;
  
  /// 模型名称
  final String? modelName;
  
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
  
  /// 是否启用RAG
  final bool enableRAG;
  
  /// RAG集合名称
  final String? ragCollection;
  
  /// 构造函数
  const AgentCreateParams({
    required this.type,
    this.systemPrompt,
    this.modelName,
    this.temperature = 0.7,
    this.maxTokens = 2000,
    this.enableTools = false,
    this.tools,
    this.maxSteps = 5,
    this.enableRAG = false,
    this.ragCollection,
  });
}

/// 智能体工厂类
class AgentFactory {
  /// 模型提供商适配器
  final ModelProviderAdapter _modelProvider;
  
  /// 增强版RAG服务
  final EnhancedRagService? _ragService;
  
  /// 构造函数
  AgentFactory({
    required ModelProviderAdapter modelProvider,
    EnhancedRagService? ragService,
  }) : 
    _modelProvider = modelProvider,
    _ragService = ragService;
  
  /// 获取默认系统提示
  String _getDefaultSystemPrompt(AgentType type) {
    switch (type) {
      case AgentType.healthAdvisor:
        return '''你是索克生活健康顾问智能体，名为"索儿"。
你专注于提供个人健康管理、健康生活方式建议和健康知识普及。
你会在回答中融合中医养生理念和现代健康理念，提供平衡、科学的建议。
回答要有针对性、实用性和科学性，避免生硬的说教，语气要温暖亲切。
你不应替代专业医疗咨询，对可能涉及严重健康问题的咨询，应建议用户咨询医生。''';
      
      case AgentType.tcmConsultant:
        return '''你是索克生活中医顾问智能体，名为"老克"。
你精通中医理论、中药学、针灸推拿等中医基础与临床知识，擅长融合传统与现代中医理念。
你需要以通俗易懂的语言解释专业中医概念，答案需有科学依据，避免过度承诺治疗效果。
遇到可能需要就医的情况，应建议用户及时就医，你不是医生，不能替代专业医疗咨询。''';
      
      case AgentType.nutritionist:
        return '''你是索克生活营养师智能体，名为"营养师小营"。
你擅长根据个人体质、生活习惯和健康目标提供个性化的饮食建议。
你的建议融合中医食疗理念和现代营养学知识，强调整体平衡和适合个人体质的饮食方案。
回答要具体实用，可以提供食谱示例、食材选择和烹饪方式建议，语气友好专业。''';
      
      case AgentType.fitnessCoach:
        return '''你是索克生活健身教练智能体，名为"教练小动"。
你擅长根据用户的身体状况、健身目标和生活习惯，制定科学合理的运动计划。
你的建议注重安全性和有效性，会考虑用户的体质特点和可能的活动限制。
回答要详细具体，包括运动类型、频率、强度和注意事项，以及进展跟踪方法。''';
      
      case AgentType.knowledgeRetrieval:
        return '''你是索克生活知识检索智能体，名为"检索小智"。
你专注于从索克生活知识库中检索和整合健康、中医和养生相关知识。
回答要准确完整，注明信息来源，对于知识库中没有的信息，应明确告知，避免编造。
你善于分析用户问题，提取关键词，找到最相关的知识内容，并以结构化方式呈现。''';
      
      case AgentType.lifeAssistant:
        return '''你是索克生活助手智能体，名为"生活小助"。
你帮助用户管理日常生活，包括健康记录、习惯养成、日程安排和生活小贴士。
你的回答要实用、简洁，富有生活智慧，应考虑用户的具体情况和需求。
你会鼓励用户培养健康生活方式，提供积极支持和适当的督促，语气亲切友好。''';
    }
  }
  
  /// 获取默认模型名称
  String _getDefaultModelName(AgentType type) {
    switch (type) {
      case AgentType.healthAdvisor:
        return 'ernie-bot-4';
      case AgentType.tcmConsultant:
        return 'ernie-bot-4';
      case AgentType.nutritionist:
        return 'ernie-bot-turbo';
      case AgentType.fitnessCoach:
        return 'ernie-bot-turbo';
      case AgentType.knowledgeRetrieval:
        return 'ernie-bot-4';
      case AgentType.lifeAssistant:
        return 'ernie-bot-turbo';
    }
  }
  
  /// 创建智能体会话
  Future<AgentResponse> createAgentChat({
    required AgentCreateParams params,
    required List<AgentMessage> messages,
    String? userQuery,
  }) async {
    // 准备系统提示
    final systemPrompt = params.systemPrompt ?? _getDefaultSystemPrompt(params.type);
    
    // 准备模型名称
    final modelName = params.modelName ?? _getDefaultModelName(params.type);
    
    // 准备调用选项
    final options = ModelCallOptions(
      modelName: modelName,
      temperature: params.temperature,
      maxTokens: params.maxTokens,
      enableTools: params.enableTools,
      tools: params.tools,
      maxSteps: params.maxSteps,
    );
    
    // 准备消息列表
    final completeMessages = <AgentMessage>[];
    
    // 添加系统提示
    bool hasSystemPrompt = false;
    for (final message in messages) {
      if (message.role == AgentMessageRole.system) {
        hasSystemPrompt = true;
        break;
      }
    }
    
    if (!hasSystemPrompt) {
      completeMessages.add(AgentMessage(
        role: AgentMessageRole.system,
        content: systemPrompt,
      ));
    }
    
    // 添加现有消息
    completeMessages.addAll(messages);
    
    // 如果有新的用户查询，添加到消息列表
    if (userQuery != null && userQuery.isNotEmpty) {
      completeMessages.add(AgentMessage(
        role: AgentMessageRole.user,
        content: userQuery,
      ));
    }
    
    // 如果启用RAG且提供了RAG集合名称
    if (params.enableRAG && 
        params.ragCollection != null && 
        _ragService != null && 
        userQuery != null) {
      
      // 使用RAG服务生成回答
      return await _ragService!.generateWithRAG(
        query: userQuery,
        baseMessages: completeMessages,
        collection: params.ragCollection!,
        options: options,
      );
    } else {
      // 直接使用模型提供商生成回答
      return await _modelProvider.chatCompletion(
        messages: completeMessages,
        options: options,
      );
    }
  }
}

/// 智能体工厂提供者
final agentFactoryProvider = Provider<AgentFactory>((ref) {
  final modelProvider = ref.watch(modelProviderAdapterProvider);
  final ragService = ref.watch(enhancedRagServiceProvider);
  
  return AgentFactory(
    modelProvider: modelProvider,
    ragService: ragService,
  );
}); 