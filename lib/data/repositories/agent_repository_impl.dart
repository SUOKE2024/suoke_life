import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 智能体仓库实现类
class AgentRepositoryImpl implements AgentRepository {
  /// SharedPreferences实例
  final SharedPreferences _prefs;
  
  /// 存储智能体会话的键前缀
  static const String _conversationPrefix = 'agent_conversation_';
  
  /// 存储智能体消息的键前缀
  static const String _messagePrefix = 'agent_message_';
  
  /// 生成随机ID的实例
  final Random _random = Random();

  /// 构造函数
  AgentRepositoryImpl(this._prefs);

  /// 模拟的智能体数据
  final List<Agent> _mockAgents = [
    Agent(
      id: 'agent_1',
      name: '小艾',
      type: AgentType.xiaoAi,
      description: '我是小艾，索克智能体家族的交互专家。可以帮助你完成四诊采集，解答健康问题，并协调其他智能体为你服务。',
      avatarUrl: 'assets/images/avatars/xiaoai.png',
      lastActiveTime: DateTime.now(),
      createdAt: DateTime.now().subtract(const Duration(days: 365)),
    ),
    Agent(
      id: 'agent_2',
      name: '小克',
      type: AgentType.xiaoKe,
      description: '我是小克，负责服务资源管理。可以帮你推荐合适的服务和产品，安排预约，管理订单。',
      avatarUrl: 'assets/images/avatars/xiaoke.png',
      lastActiveTime: DateTime.now().subtract(const Duration(hours: 2)),
      createdAt: DateTime.now().subtract(const Duration(days: 300)),
    ),
    Agent(
      id: 'agent_3',
      name: '老克',
      type: AgentType.laoKe,
      description: '我是老克，专注于中医知识传播。擅长讲解中医理论，分享养生知识，提供学习资源。',
      avatarUrl: 'assets/images/avatars/laoke.png',
      lastActiveTime: DateTime.now().subtract(const Duration(days: 1)),
      createdAt: DateTime.now().subtract(const Duration(days: 500)),
    ),
    Agent(
      id: 'agent_4',
      name: '索儿',
      type: AgentType.suoEr,
      description: '我是索儿，你的生活健康助手。负责记录你的健康数据，提供个性化建议，督促良好习惯养成。',
      avatarUrl: 'assets/images/avatars/suoer.png',
      lastActiveTime: DateTime.now().subtract(const Duration(minutes: 30)),
      createdAt: DateTime.now().subtract(const Duration(days: 200)),
    ),
  ];

  /// 模拟的会话数据
  final List<AgentConversation> _mockConversations = [];
  
  /// 模拟的消息数据
  final List<AgentMessage> _mockMessages = [];

  @override
  Future<List<Agent>> getAgents() async {
    // 在MVP阶段，直接返回模拟数据
    return _mockAgents;
  }

  @override
  Future<Agent?> getAgentById(String agentId) async {
    // 在模拟数据中查找对应ID的智能体
    try {
      return _mockAgents.firstWhere((agent) => agent.id == agentId);
    } catch (e) {
      return null;
    }
  }

  @override
  Future<Agent?> getAgentByType(AgentType type) async {
    // 在模拟数据中查找对应类型的智能体
    try {
      return _mockAgents.firstWhere((agent) => agent.type == type);
    } catch (e) {
      return null;
    }
  }

  @override
  Future<List<AgentConversation>> getConversations(String userId) async {
    // 返回用户的所有会话
    return _mockConversations
        .where((conversation) => conversation.userId == userId)
        .toList();
  }

  @override
  Future<AgentConversation?> getConversationById(String conversationId) async {
    // 查找指定ID的会话
    try {
      return _mockConversations.firstWhere((conversation) => conversation.id == conversationId);
    } catch (e) {
      return null;
    }
  }

  @override
  Future<AgentConversation> createConversation({
    required String userId,
    required String agentId,
    required String title,
  }) async {
    // 创建新会话
    final conversation = AgentConversation(
      id: 'conversation_${_random.nextInt(10000)}',
      title: title,
      agentId: agentId,
      userId: userId,
      createdAt: DateTime.now(),
      lastMessageTime: DateTime.now(),
    );
    
    _mockConversations.add(conversation);
    
    // 添加系统欢迎消息
    final agent = await getAgentById(agentId);
    if (agent != null) {
      await sendMessage(
        conversationId: conversation.id,
        senderId: agentId,
        messageType: MessageType.system,
        contentType: ContentType.text,
        content: '欢迎与${agent.name}开始对话，有什么可以帮助你的？',
      );
    }
    
    return conversation;
  }

  @override
  Future<List<AgentMessage>> getMessages(String conversationId, {int limit = 20, int offset = 0}) async {
    // 获取会话的消息，并应用分页
    final messages = _mockMessages
        .where((message) => message.conversationId == conversationId)
        .toList();
    
    // 按时间排序，最新的在最后
    messages.sort((a, b) => a.createdAt.compareTo(b.createdAt));
    
    // 应用分页
    if (offset >= messages.length) {
      return [];
    }
    
    final end = offset + limit;
    return messages.sublist(offset, end < messages.length ? end : messages.length);
  }

  @override
  Future<AgentMessage> sendMessage({
    required String conversationId,
    required String senderId,
    required MessageType messageType,
    required ContentType contentType,
    required String content,
    Map<String, dynamic>? extraData,
  }) async {
    // 创建并保存新消息
    final message = AgentMessage(
      id: 'message_${_random.nextInt(10000)}',
      conversationId: conversationId,
      senderId: senderId,
      messageType: messageType,
      contentType: contentType,
      content: content,
      createdAt: DateTime.now(),
      extraData: extraData,
    );
    
    _mockMessages.add(message);
    
    // 更新会话的最后消息时间
    final conversationIndex = _mockConversations.indexWhere((c) => c.id == conversationId);
    if (conversationIndex != -1) {
      final conversation = _mockConversations[conversationIndex];
      _mockConversations[conversationIndex] = conversation.copyWith(
        lastMessageTime: DateTime.now(),
      );
    }
    
    return message;
  }

  @override
  Future<AgentMessage> generateAgentResponse({
    required String conversationId,
    required String agentId,
    required List<AgentMessage> conversationHistory,
  }) async {
    // 获取智能体信息
    final agent = await getAgentById(agentId);
    if (agent == null) {
      throw Exception('找不到智能体: $agentId');
    }
    
    // 获取最后一条用户消息
    final lastUserMessage = conversationHistory.lastWhere(
      (message) => message.messageType == MessageType.user,
      orElse: () => AgentMessage(
        id: '',
        conversationId: conversationId,
        senderId: '',
        messageType: MessageType.user,
        contentType: ContentType.text,
        content: '',
        createdAt: DateTime.now(),
      ),
    );
    
    // 根据智能体类型和用户消息生成响应
    String response;
    switch (agent.type) {
      case AgentType.xiaoAi:
        response = _generateXiaoAiResponse(lastUserMessage.content);
        break;
      case AgentType.xiaoKe:
        response = _generateXiaoKeResponse(lastUserMessage.content);
        break;
      case AgentType.laoKe:
        response = _generateLaoKeResponse(lastUserMessage.content);
        break;
      case AgentType.suoEr:
        response = _generateSuoErResponse(lastUserMessage.content);
        break;
    }
    
    // 创建并返回智能体响应消息
    return sendMessage(
      conversationId: conversationId,
      senderId: agentId,
      messageType: MessageType.agent,
      contentType: ContentType.text,
      content: response,
    );
  }

  @override
  Future<void> updateConversationStatus(String conversationId, {bool? isActive, String? title}) async {
    final index = _mockConversations.indexWhere((c) => c.id == conversationId);
    if (index != -1) {
      final conversation = _mockConversations[index];
      _mockConversations[index] = conversation.copyWith(
        isActive: isActive ?? conversation.isActive,
        title: title ?? conversation.title,
      );
    }
  }

  @override
  Future<void> deleteConversation(String conversationId) async {
    _mockConversations.removeWhere((conversation) => conversation.id == conversationId);
    _mockMessages.removeWhere((message) => message.conversationId == conversationId);
  }

  @override
  Future<void> deleteMessage(String messageId) async {
    _mockMessages.removeWhere((message) => message.id == messageId);
  }
  
  /// 生成小艾的预设回复
  String _generateXiaoAiResponse(String userMessage) {
    final lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.contains('你好') || lowerMessage.contains('嗨') || lowerMessage.isEmpty) {
      return '你好，我是小艾，很高兴为你服务。我可以帮助你进行健康评估、回答健康问题，以及协调其他智能体为你提供服务。有什么我可以帮助你的？';
    } else if (lowerMessage.contains('四诊') || lowerMessage.contains('辨证')) {
      return '四诊合参是中医诊断的基本方法，包括望、闻、问、切四种诊法。我可以引导你完成四诊采集，帮助评估你的体质状况。需要开始吗？';
    } else if (lowerMessage.contains('舌诊') || lowerMessage.contains('舌象') || lowerMessage.contains('舌头')) {
      return '舌诊是中医望诊的重要内容。你可以点击下方的"开始舌诊"按钮，按照指引拍摄舌头照片，我会为你分析舌象特征，协助评估你的健康状况。';
    } else if (lowerMessage.contains('如何') || lowerMessage.contains('怎么')) {
      return '关于这个问题，我需要更多信息来给你准确的建议。能具体描述一下你的情况吗？或者，你可以尝试开始四诊采集，让我全面了解你的健康状况。';
    } else {
      return '我理解你的问题。为了给你提供更准确的帮助，我建议我们先进行一次简单的健康评估。你最近感觉怎么样？有没有特别不舒服的地方？';
    }
  }
  
  /// 生成小克的预设回复
  String _generateXiaoKeResponse(String userMessage) {
    final lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.contains('你好') || lowerMessage.contains('嗨') || lowerMessage.isEmpty) {
      return '你好，我是小克，负责服务资源管理。有什么服务或产品需要我为你推荐吗？';
    } else if (lowerMessage.contains('推荐') || lowerMessage.contains('建议')) {
      return '根据你的需求，我可以为你推荐一些适合的健康服务和产品。不过，为了提供更个性化的推荐，我建议先完成体质评估，这样推荐会更准确。';
    } else if (lowerMessage.contains('预约') || lowerMessage.contains('咨询')) {
      return '预约服务目前支持线上健康咨询、营养指导和中医调理预约。你想预约哪一类服务？请告诉我你的具体需求和期望的时间段。';
    } else if (lowerMessage.contains('产品') || lowerMessage.contains('购买')) {
      return '索克生活提供多种健康产品，包括体质调理茶饮、养生食材、健康监测设备等。你对哪一类产品更感兴趣？我可以为你筛选最适合的选择。';
    } else {
      return '感谢你的咨询。为了更好地为你服务，我需要了解你的具体需求。你可以告诉我你关注的健康方向，如睡眠、营养、运动等，我会为你提供相关的服务和产品建议。';
    }
  }
  
  /// 生成老克的预设回复
  String _generateLaoKeResponse(String userMessage) {
    final lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.contains('你好') || lowerMessage.contains('嗨') || lowerMessage.isEmpty) {
      return '你好，我是老克，专注于中医知识传播。有什么中医知识问题想请教吗？';
    } else if (lowerMessage.contains('中医') || lowerMessage.contains('理论')) {
      return '中医学理论博大精深，核心包括阴阳五行、脏腑经络、气血津液等理论。你想了解哪一方面的具体内容？我可以为你提供系统的知识讲解。';
    } else if (lowerMessage.contains('体质') || lowerMessage.contains('类型')) {
      return '中医体质理论将人体质分为九种基本类型：平和质、气虚质、阳虚质、阴虚质、痰湿质、湿热质、血瘀质、气郁质、特禀质。每种体质有不同的生理病理特点和养生要求。你想深入了解某种体质吗？';
    } else if (lowerMessage.contains('经络') || lowerMessage.contains('穴位')) {
      return '经络是中医理论的重要组成部分，全身共有十二正经和奇经八脉，连接五脏六腑和体表各部。经络上分布着众多穴位，是针灸、推拿等治疗的关键点。你想了解特定的经络或穴位吗？';
    } else {
      return '这是个很好的问题。中医讲究整体观念和辨证论治，根据个体差异给予个性化的健康指导。如果你对特定领域感兴趣，可以详细询问，我会提供更深入的知识分享。';
    }
  }
  
  /// 生成索儿的预设回复
  String _generateSuoErResponse(String userMessage) {
    final lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.contains('你好') || lowerMessage.contains('嗨') || lowerMessage.isEmpty) {
      return '你好，我是索儿，你的生活健康助手。我可以帮你记录健康数据，提供个性化建议，督促良好习惯养成。有什么我可以帮到你的？';
    } else if (lowerMessage.contains('睡眠') || lowerMessage.contains('失眠')) {
      return '良好的睡眠对健康至关重要。我注意到你最近的睡眠数据显示，睡眠效率有所下降。我可以帮你制定改善睡眠的计划，包括睡前放松、环境调整和作息规律等方面。要开始睡眠改善计划吗？';
    } else if (lowerMessage.contains('饮食') || lowerMessage.contains('吃什么')) {
      return '健康的饮食应当根据个人体质和季节变化来调整。基于你的体质特点，我建议你增加一些温性食物，如生姜、羊肉等，减少生冷食物的摄入。你想查看完整的体质饮食建议吗？';
    } else if (lowerMessage.contains('运动') || lowerMessage.contains('锻炼')) {
      return '根据你的健康数据，我建议你进行适度的有氧运动，如快走、慢跑或游泳，每周3-5次，每次30分钟。同时，太极拳或八段锦等传统导引术也很适合你。需要详细的运动计划吗？';
    } else {
      return '我了解你的关注点。健康生活是一个系统工程，需要从饮食、运动、睡眠、情绪等多方面进行调节。我可以根据你的健康数据和日常习惯，为你提供个性化的生活方案。有特定方面需要我重点关注吗？';
    }
  }

  /// 模拟的用户交互历史数据
  final List<UserInteraction> _mockInteractions = [
    UserInteraction(
      id: 'interaction_1',
      userId: 'user_1',
      agentType: AgentType.xiaoAi,
      conversationId: 'conversation_1',
      topic: '健康评估咨询',
      timestamp: DateTime.now().subtract(const Duration(days: 1)),
    ),
    UserInteraction(
      id: 'interaction_2',
      userId: 'user_1',
      agentType: AgentType.laoKe,
      conversationId: 'conversation_2',
      topic: '中医体质理论讨论',
      timestamp: DateTime.now().subtract(const Duration(hours: 12)),
    ),
    UserInteraction(
      id: 'interaction_3',
      userId: 'user_1',
      agentType: AgentType.suoEr,
      conversationId: 'conversation_3',
      topic: '睡眠质量改善计划',
      timestamp: DateTime.now().subtract(const Duration(hours: 6)),
    ),
    UserInteraction(
      id: 'interaction_4',
      userId: 'user_1',
      agentType: AgentType.xiaoKe,
      conversationId: 'conversation_4',
      topic: '健康产品推荐',
      timestamp: DateTime.now().subtract(const Duration(hours: 2)),
    ),
  ];

  @override
  Future<List<UserInteraction>> getUserInteractions(String userId, {int limit = 5}) async {
    // 获取用户的交互历史记录
    final interactions = _mockInteractions
        .where((interaction) => interaction.userId == userId)
        .toList();
    
    // 按时间排序，最新的在前面
    interactions.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    
    // 应用数量限制
    return interactions.take(limit).toList();
  }
} 