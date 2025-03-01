import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../domain/entities/message.dart';
import '../../domain/entities/chat.dart';
import '../../ai_agents/models/ai_agent.dart';

// 聊天状态
class ChatState {
  final List<Chat> chats;
  final Chat? currentChat;
  final List<Message> messages;
  final bool isLoading;
  final String? error;

  ChatState({
    this.chats = const [],
    this.currentChat,
    this.messages = const [],
    this.isLoading = false,
    this.error,
  });

  ChatState copyWith({
    List<Chat>? chats,
    Chat? currentChat,
    List<Message>? messages,
    bool? isLoading,
    String? error,
  }) {
    return ChatState(
      chats: chats ?? this.chats,
      currentChat: currentChat ?? this.currentChat,
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// 聊天状态管理器
class ChatNotifier extends StateNotifier<ChatState> {
  ChatNotifier() : super(ChatState()) {
    _initializeChat();
  }

  // 模拟用户ID
  final String _currentUserId = const Uuid().v4();
  
  // 获取当前用户ID
  String get currentUserId => _currentUserId;

  // 初始化聊天
  void _initializeChat() {
    // 创建默认的AI聊天
    final defaultChat = Chat.ai(
      userId: _currentUserId,
      title: "与小艾的对话",
      metadata: {
        'agentId': AIAgent.xiaoai.id,
      },
    );

    // 添加默认的欢迎消息
    final welcomeMessage = Message(
      id: const Uuid().v4(),
      content: "欢迎使用索克生活APP！我是您的健康生活助手小艾，有什么我可以帮助您的吗？",
      timestamp: DateTime.now(),
      senderId: AIAgent.xiaoai.id,
      receiverId: _currentUserId,
      chatId: defaultChat.id,
      type: MessageType.text,
      status: MessageStatus.delivered,
    );

    // 更新状态
    state = state.copyWith(
      chats: [defaultChat],
      currentChat: defaultChat,
      messages: [welcomeMessage],
    );
  }

  // 发送消息
  Future<void> sendMessage(String content) async {
    if (state.currentChat == null) return;

    // 创建用户消息
    final userMessage = Message(
      id: const Uuid().v4(),
      content: content,
      timestamp: DateTime.now(),
      senderId: _currentUserId,
      receiverId: state.currentChat!.participantIds.firstWhere(
        (id) => id != _currentUserId,
        orElse: () => AIAgent.xiaoai.id,
      ),
      chatId: state.currentChat!.id,
      type: MessageType.text,
      status: MessageStatus.sent,
    );

    // 更新消息列表
    state = state.copyWith(
      messages: [userMessage, ...state.messages],
      isLoading: true,
    );

    // 模拟AI回复
    await _simulateAIResponse(content);
  }

  // 模拟AI回复
  Future<void> _simulateAIResponse(String userContent) async {
    if (state.currentChat == null) return;

    // 模拟网络延迟
    await Future.delayed(const Duration(seconds: 1));

    // 根据聊天类型获取AI代理
    final String agentId = state.currentChat!.metadata?['agentId'] ?? AIAgent.xiaoai.id;

    // 根据用户输入生成回复内容
    String aiResponse = '';
    
    if (userContent.contains('你好') || userContent.contains('Hi') || userContent.contains('Hello')) {
      aiResponse = '你好！很高兴为您服务。我是索克生活APP的AI助手，您有什么健康问题想咨询吗？';
    } else if (userContent.contains('健康') || userContent.contains('养生')) {
      aiResponse = '健康生活需要均衡饮食、适量运动、充足睡眠和良好心态。您有具体关注的健康方面吗？';
    } else if (userContent.contains('饮食') || userContent.contains('吃')) {
      aiResponse = '饮食方面，建议遵循"三低一高"原则：低盐、低糖、低脂肪，高纤维。多吃蔬果，适量摄入优质蛋白，少吃加工食品。您想了解更详细的饮食建议吗？';
    } else if (userContent.contains('运动') || userContent.contains('锻炼')) {
      aiResponse = '适量运动对健康非常重要。建议每周进行150分钟中等强度有氧运动，如快走、游泳或骑车，并结合肌肉力量训练。重要的是找到您喜欢并能坚持的运动方式。';
    } else if (userContent.contains('睡眠') || userContent.contains('失眠')) {
      aiResponse = '良好的睡眠对健康至关重要。建议保持规律作息，睡前避免使用电子设备，营造安静舒适的睡眠环境。成年人每晚应保证7-8小时的睡眠时间。';
    } else if (userContent.contains('中医') || userContent.contains('中药')) {
      aiResponse = '中医理论强调整体观念和辨证施治。在日常养生中，可以结合体质特点，通过调整饮食、起居和情志来达到平衡阴阳、调和气血的目的。具体用药请在专业中医指导下进行。';
    } else if (userContent.contains('压力') || userContent.contains('焦虑') || userContent.contains('抑郁')) {
      aiResponse = '心理健康同样重要。建议学习一些减压技巧，如深呼吸、冥想、瑜伽等。保持社交联系，适当倾诉，必要时寻求专业心理咨询帮助。';
    } else if (userContent.contains('感冒') || userContent.contains('发烧')) {
      aiResponse = '感冒和发烧通常是自限性疾病。多休息、多饮水、保持室内通风。如果发热超过38.5°C，或症状持续加重，建议及时就医。';
    } else {
      aiResponse = '感谢您的提问！作为健康助手，我可以为您提供健康生活、疾病预防等方面的建议。请告诉我您具体关注的健康问题，我会尽力提供专业建议。';
    }

    // 创建AI回复消息
    final aiMessage = Message(
      id: const Uuid().v4(),
      content: aiResponse,
      timestamp: DateTime.now(),
      senderId: agentId,
      receiverId: _currentUserId,
      chatId: state.currentChat!.id,
      type: MessageType.text,
      status: MessageStatus.delivered,
    );

    // 更新消息列表
    state = state.copyWith(
      messages: [aiMessage, ...state.messages],
      isLoading: false,
    );
  }

  // 切换代理
  void switchAgent(AIAgent agent) {
    if (state.currentChat == null) return;

    // 创建系统消息
    final systemMessage = Message(
      id: const Uuid().v4(),
      content: "您已切换到${agent.name}，${agent.description}",
      timestamp: DateTime.now(),
      senderId: "system",
      receiverId: _currentUserId,
      chatId: state.currentChat!.id,
      type: MessageType.system,
      status: MessageStatus.delivered,
    );

    // 更新当前聊天的元数据
    final updatedChat = state.currentChat!.copyWith(
      metadata: {
        ...state.currentChat!.metadata ?? {},
        'agentId': agent.id,
      },
    );

    // 更新状态
    state = state.copyWith(
      currentChat: updatedChat,
      messages: [systemMessage, ...state.messages],
    );
  }

  // 清空聊天记录
  void clearMessages() {
    if (state.currentChat == null) return;

    // 创建系统消息
    final systemMessage = Message(
      id: const Uuid().v4(),
      content: "聊天记录已清空",
      timestamp: DateTime.now(),
      senderId: "system",
      receiverId: _currentUserId,
      chatId: state.currentChat!.id,
      type: MessageType.system,
      status: MessageStatus.delivered,
    );

    // 更新状态
    state = state.copyWith(
      messages: [systemMessage],
    );
  }
}

// 全局聊天状态提供者
final chatStateProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  return ChatNotifier();
});