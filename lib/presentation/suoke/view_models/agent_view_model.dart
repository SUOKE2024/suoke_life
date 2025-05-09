import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';
import 'package:suoke_life/domain/services/agent_service.dart';

/// 智能体视图模型状态
class AgentViewState {
  /// 是否正在加载
  final bool isLoading;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 所有可用的智能体
  final List<Agent> agents;
  
  /// 当前活跃的智能体
  final Agent? activeAgent;
  
  /// 用户的会话列表
  final List<AgentConversation> conversations;
  
  /// 当前选中的会话
  final AgentConversation? selectedConversation;
  
  /// 当前会话的消息列表
  final List<AgentMessage> messages;
  
  /// 是否正在发送消息
  final bool isSending;
  
  /// 建议的回复
  final List<String> suggestedResponses;

  /// 构造函数
  AgentViewState({
    this.isLoading = false,
    this.errorMessage,
    this.agents = const [],
    this.activeAgent,
    this.conversations = const [],
    this.selectedConversation,
    this.messages = const [],
    this.isSending = false,
    this.suggestedResponses = const [],
  });

  /// 复制状态并修改部分属性
  AgentViewState copyWith({
    bool? isLoading,
    String? errorMessage,
    List<Agent>? agents,
    Agent? activeAgent,
    List<AgentConversation>? conversations,
    AgentConversation? selectedConversation,
    List<AgentMessage>? messages,
    bool? isSending,
    List<String>? suggestedResponses,
  }) {
    return AgentViewState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      agents: agents ?? this.agents,
      activeAgent: activeAgent ?? this.activeAgent,
      conversations: conversations ?? this.conversations,
      selectedConversation: selectedConversation ?? this.selectedConversation,
      messages: messages ?? this.messages,
      isSending: isSending ?? this.isSending,
      suggestedResponses: suggestedResponses ?? this.suggestedResponses,
    );
  }
}

/// 智能体视图模型
class AgentViewModel extends StateNotifier<AgentViewState> {
  /// 智能体仓库
  final AgentRepository _agentRepository;
  
  /// 智能体服务
  final AgentService _agentService;
  
  /// 模拟的用户ID
  final String _mockUserId = 'user_1';

  /// 构造函数
  AgentViewModel(this._agentRepository, this._agentService) : super(AgentViewState()) {
    _initialize();
  }

  /// 初始化
  Future<void> _initialize() async {
    try {
      state = state.copyWith(isLoading: true);
      
      // 初始化智能体系统
      await _agentService.initializeAgentSystem();
      
      // 获取所有智能体
      final agents = await _agentRepository.getAgents();
      
      // 获取最近活跃智能体
      final activeAgent = await _agentService.getLastActiveAgent();
      
      // 获取用户会话
      final conversations = await _agentRepository.getConversations(_mockUserId);
      
      // 如果有会话，选择最新的一个
      AgentConversation? selectedConversation;
      List<AgentMessage> messages = [];
      
      if (conversations.isNotEmpty) {
        // 按最后消息时间排序
        conversations.sort((a, b) => b.lastMessageTime.compareTo(a.lastMessageTime));
        selectedConversation = conversations.first;
        
        // 获取会话消息
        messages = await _agentRepository.getMessages(selectedConversation.id);
      }
      
      // 获取建议回复
      List<String> suggestedResponses = [];
      if (activeAgent != null) {
        suggestedResponses = await _agentService.getAgentSuggestedResponses(activeAgent.type);
      }
      
      state = state.copyWith(
        isLoading: false,
        agents: agents,
        activeAgent: activeAgent,
        conversations: conversations,
        selectedConversation: selectedConversation,
        messages: messages,
        suggestedResponses: suggestedResponses,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '初始化智能体系统失败: ${e.toString()}',
      );
    }
  }

  /// 切换活跃智能体
  Future<void> switchAgent(AgentType type) async {
    try {
      state = state.copyWith(isLoading: true);
      
      // 切换活跃智能体
      final activeAgent = await _agentService.switchActiveAgent(type);
      
      // 获取新智能体的建议回复
      final suggestedResponses = await _agentService.getAgentSuggestedResponses(type);
      
      state = state.copyWith(
        isLoading: false,
        activeAgent: activeAgent,
        suggestedResponses: suggestedResponses,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '切换智能体失败: ${e.toString()}',
      );
    }
  }

  /// 选择会话
  Future<void> selectConversation(String conversationId) async {
    try {
      state = state.copyWith(isLoading: true);
      
      // 获取会话
      final conversation = await _agentRepository.getConversationById(conversationId);
      if (conversation == null) {
        throw Exception('找不到指定的会话');
      }
      
      // 获取会话消息
      final messages = await _agentRepository.getMessages(conversationId);
      
      // 如果会话与当前活跃智能体不同，需要切换智能体
      if (state.activeAgent == null || conversation.agentId != state.activeAgent!.id) {
        final agent = await _agentRepository.getAgentById(conversation.agentId);
        if (agent != null) {
          await switchAgent(agent.type);
        }
      }
      
      state = state.copyWith(
        isLoading: false,
        selectedConversation: conversation,
        messages: messages,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '选择会话失败: ${e.toString()}',
      );
    }
  }

  /// 创建新会话
  Future<void> createNewConversation({String? title}) async {
    try {
      if (state.activeAgent == null) {
        throw Exception('没有活跃的智能体');
      }
      
      state = state.copyWith(isLoading: true);
      
      // 创建新会话
      final conversation = await _agentRepository.createConversation(
        userId: _mockUserId,
        agentId: state.activeAgent!.id,
        title: title ?? '与${state.activeAgent!.name}的对话',
      );
      
      // 更新会话列表
      final conversations = [...state.conversations, conversation];
      
      // 获取会话消息
      final messages = await _agentRepository.getMessages(conversation.id);
      
      state = state.copyWith(
        isLoading: false,
        conversations: conversations,
        selectedConversation: conversation,
        messages: messages,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '创建会话失败: ${e.toString()}',
      );
    }
  }

  /// 发送消息
  Future<void> sendMessage(String content) async {
    try {
      if (content.trim().isEmpty) {
        return;
      }
      
      if (state.activeAgent == null) {
        throw Exception('没有活跃的智能体');
      }
      
      if (state.selectedConversation == null) {
        // 如果没有选中的会话，先创建一个
        await createNewConversation();
        if (state.selectedConversation == null) {
          throw Exception('创建会话失败');
        }
      }
      
      state = state.copyWith(isSending: true);
      
      // 发送用户消息
      final userMessage = await _agentRepository.sendMessage(
        conversationId: state.selectedConversation!.id,
        senderId: _mockUserId,
        messageType: MessageType.user,
        contentType: ContentType.text,
        content: content,
      );
      
      // 添加用户消息到状态
      final updatedMessages = [...state.messages, userMessage];
      state = state.copyWith(
        messages: updatedMessages,
        isSending: true,
      );
      
      // 检查是否需要切换智能体
      final suggestedAgent = await _agentService.checkAndHandleAgentSwitchRequest(
        currentAgentType: state.activeAgent!.type,
        message: content,
      );
      
      if (suggestedAgent != null && suggestedAgent.id != state.activeAgent!.id) {
        // 添加系统消息，表示智能体推荐
        await _agentRepository.sendMessage(
          conversationId: state.selectedConversation!.id,
          senderId: 'system',
          messageType: MessageType.system,
          contentType: ContentType.text,
          content: '根据您的问题，我推荐由${suggestedAgent.name}为您解答。',
        );
        
        // 切换智能体
        await switchAgent(suggestedAgent.type);
      }
      
      // 生成智能体响应
      final agentResponse = await _agentRepository.generateAgentResponse(
        conversationId: state.selectedConversation!.id,
        agentId: state.activeAgent!.id,
        conversationHistory: updatedMessages,
      );
      
      // 获取最新的消息列表
      final latestMessages = await _agentRepository.getMessages(state.selectedConversation!.id);
      
      // 更新会话列表
      final conversations = await _agentRepository.getConversations(_mockUserId);
      
      state = state.copyWith(
        isSending: false,
        messages: latestMessages,
        conversations: conversations,
      );
    } catch (e) {
      state = state.copyWith(
        isSending: false,
        errorMessage: '发送消息失败: ${e.toString()}',
      );
    }
  }

  /// 发送系统消息
  Future<void> sendSystemMessage(String content, {bool hidden = false}) async {
    try {
      if (content.trim().isEmpty) {
        return;
      }
      
      if (state.activeAgent == null) {
        throw Exception('没有活跃的智能体');
      }
      
      if (state.selectedConversation == null) {
        // 如果没有选中的会话，创建一个
        await createNewConversation();
      }
      
      state = state.copyWith(isSending: true);
      
      // 创建系统消息
      final systemMessage = await _agentRepository.sendMessage(
        conversationId: state.selectedConversation!.id,
        senderId: 'system',
        messageType: MessageType.system,
        contentType: ContentType.text,
        content: content,
      );
      
      // 如果是隐藏消息，不更新UI显示
      if (!hidden) {
        // 添加到消息列表
        final updatedMessages = [...state.messages, systemMessage];
        state = state.copyWith(
          isSending: false,
          messages: updatedMessages,
        );
      } else {
        state = state.copyWith(isSending: false);
      }
      
      // 生成智能体回复
      await _agentRepository.generateAgentResponse(
        conversationId: state.selectedConversation!.id,
        agentId: state.activeAgent!.id,
        conversationHistory: state.messages,
      );
    } catch (e) {
      state = state.copyWith(
        isSending: false,
        errorMessage: '发送系统消息失败: ${e.toString()}',
      );
    }
  }

  /// 使用建议回复
  Future<void> useSuggestedResponse(String response) async {
    await sendMessage(response);
  }

  /// 清除错误
  void clearError() {
    if (state.errorMessage != null) {
      state = state.copyWith(errorMessage: null);
    }
  }
}

/// 智能体视图模型Provider
final agentViewModelProvider = StateNotifierProvider<AgentViewModel, AgentViewState>((ref) {
  final agentRepository = ref.watch(agentRepositoryProvider);
  final agentService = ref.watch(agentServiceProvider);
  return AgentViewModel(agentRepository, agentService);
}); 