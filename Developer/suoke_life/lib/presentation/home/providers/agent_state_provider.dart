import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/usecases/agent/get_agents_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/get_agent_by_id_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/send_message_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/stream_from_agent_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/get_agent_sessions_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/create_session_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/get_session_messages_usecase.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/di/providers/agent_providers.dart';
import 'package:uuid/uuid.dart';

/// 智能体状态
class AgentState {
  final List<AgentModel>? agents;
  final AgentModel? currentAgent;
  final List<SessionModel>? sessions;
  final SessionModel? currentSession;
  final List<MessageModel>? messages;
  final bool isLoading;
  final String? errorMessage;
  final String? chatId;

  AgentState({
    this.agents,
    this.currentAgent,
    this.sessions,
    this.currentSession,
    this.messages,
    this.isLoading = false,
    this.errorMessage,
    this.chatId,
  });

  /// 创建初始状态
  factory AgentState.initial() {
    return AgentState();
  }

  /// 创建加载状态
  AgentState loading() {
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: messages,
      isLoading: true,
      errorMessage: null,
      chatId: null,
    );
  }

  /// 创建错误状态
  AgentState error(String message) {
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: messages,
      isLoading: false,
      errorMessage: message,
      chatId: null,
    );
  }

  /// 设置智能体列表
  AgentState withAgents(List<AgentModel> agents) {
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: messages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  /// 设置当前智能体
  AgentState withCurrentAgent(AgentModel agent) {
    return AgentState(
      agents: agents,
      currentAgent: agent,
      sessions: sessions,
      currentSession: currentSession,
      messages: messages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  /// 设置会话列表
  AgentState withSessions(List<SessionModel> sessions) {
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: messages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  /// 设置当前会话
  AgentState withCurrentSession(SessionModel session) {
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: session,
      messages: messages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  /// 设置消息列表
  AgentState withMessages(List<MessageModel> messages) {
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: messages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  /// 添加新消息
  AgentState addMessage(MessageModel message) {
    final updatedMessages = [...(messages ?? []), message];
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: updatedMessages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  AgentState appendMessage(MessageModel message) {
    final updatedMessages = [...(messages ?? []), message];
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: updatedMessages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  AgentState appendPlaceholderMessage() {
    final updatedMessages = [...(messages ?? []), MessageModel(
      id: const Uuid().v4(),
      role: MessageRole.assistant,
      content: '',
      timestamp: DateTime.now(),
      isPlaceholder: true,
    )];
    return AgentState(
      agents: agents,
      currentAgent: currentAgent,
      sessions: sessions,
      currentSession: currentSession,
      messages: updatedMessages,
      isLoading: false,
      errorMessage: null,
      chatId: null,
    );
  }

  AgentState copyWith({
    List<AgentModel>? agents,
    AgentModel? currentAgent,
    List<SessionModel>? sessions,
    SessionModel? currentSession,
    List<MessageModel>? messages,
    bool? isLoading,
    String? errorMessage,
    String? chatId,
  }) {
    return AgentState(
      agents: agents ?? this.agents,
      currentAgent: currentAgent ?? this.currentAgent,
      sessions: sessions ?? this.sessions,
      currentSession: currentSession ?? this.currentSession,
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage ?? this.errorMessage,
      chatId: chatId ?? this.chatId,
    );
  }
}

/// 智能体状态管理器
class AgentNotifier extends StateNotifier<AgentState> {
  final GetAgentsUseCase _getAgentsUseCase;
  final GetAgentByIdUseCase _getAgentByIdUseCase;
  final SendMessageUseCase _sendMessageUseCase;
  final StreamFromAgentUseCase _streamFromAgentUseCase;
  final GetAgentSessionsUseCase _getAgentSessionsUseCase;
  final CreateSessionUseCase _createSessionUseCase;
  final GetSessionMessagesUseCase _getSessionMessagesUseCase;
  final List<AgentModel> _presetAgents;
  final AgentService _agentService;

  AgentNotifier({
    required GetAgentsUseCase getAgentsUseCase,
    required GetAgentByIdUseCase getAgentByIdUseCase,
    required SendMessageUseCase sendMessageUseCase,
    required StreamFromAgentUseCase streamFromAgentUseCase,
    required GetAgentSessionsUseCase getAgentSessionsUseCase,
    required CreateSessionUseCase createSessionUseCase,
    required GetSessionMessagesUseCase getSessionMessagesUseCase,
    required List<AgentModel> presetAgents,
    required AgentService agentService,
  })  : _getAgentsUseCase = getAgentsUseCase,
        _getAgentByIdUseCase = getAgentByIdUseCase,
        _sendMessageUseCase = sendMessageUseCase,
        _streamFromAgentUseCase = streamFromAgentUseCase,
        _getAgentSessionsUseCase = getAgentSessionsUseCase,
        _createSessionUseCase = createSessionUseCase,
        _getSessionMessagesUseCase = getSessionMessagesUseCase,
        _presetAgents = presetAgents,
        _agentService = agentService,
        super(AgentState.initial());

  /// 加载预设智能体
  void loadPresetAgents() {
    state = state.withAgents(_presetAgents);
  }

  /// 加载智能体列表
  Future<void> loadAgents() async {
    state = state.loading();
    
    // 首先加载预设智能体，确保UI可以立即响应
    loadPresetAgents();
    
    // 然后尝试从API获取智能体
    final result = await _getAgentsUseCase(NoParams());
    result.fold(
      (failure) {
        // 如果API请求失败，但我们已经有预设智能体，则不更新错误状态
        if (state.agents == null || state.agents!.isEmpty) {
          state = state.error(failure.message);
        }
      },
      (agents) {
        // 如果API请求成功，将预设智能体和API返回的智能体合并
        // 优先使用预设智能体的信息（因为预设智能体有本地头像URL）
        final presetAgentIds = _presetAgents.map((a) => a.id).toSet();
        final nonPresetAgents = agents.where((a) => !presetAgentIds.contains(a.id)).toList();
        final mergedAgents = [..._presetAgents, ...nonPresetAgents];
        
        state = state.withAgents(mergedAgents);
      },
    );
  }

  /// 获取指定智能体
  Future<void> getAgentById(String agentId) async {
    state = state.loading();
    final result = await _getAgentByIdUseCase(AgentParams(agentId: agentId));
    result.fold(
      (failure) => state = state.error(failure.message),
      (agent) => state = state.withCurrentAgent(agent),
    );
  }

  /// 发送消息
  Future<void> sendMessage(String message) async {
    if (state.currentAgent == null) {
      state = state.error('未选择智能体');
      return;
    }

    final agentId = state.currentAgent!.id;
    final sessionId = state.currentSession?.id;

    // 先添加用户消息
    final userMessage = MessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: message,
      role: 'user',
      timestamp: DateTime.now(),
    );
    state = state.addMessage(userMessage);

    final params = MessageParams(
      agentId: agentId,
      message: message,
      sessionId: sessionId,
    );

    final result = await _sendMessageUseCase(params);
    result.fold(
      (failure) => state = state.error(failure.message),
      (response) => state = state.addMessage(response),
    );
  }

  /// 获取流式响应
  void sendStreamMessage(String message) {
    if (state.currentAgent == null) {
      state = state.error('未选择智能体');
      return;
    }

    final userMessage = MessageModel(
      id: const Uuid().v4(),
      role: MessageRole.user,
      content: message,
      timestamp: DateTime.now(),
    );

    state = state.appendMessage(userMessage);
    state = state.appendPlaceholderMessage();

    final agentId = state.currentAgent!.id;
    final chatId = state.chatId ?? const Uuid().v4();

    if (state.chatId == null) {
      state = state.copyWith(chatId: chatId);
    }

    final stream = _agentService.sendStreamMessage(
      agentId: agentId,
      message: message,
      chatId: chatId,
    );

    // 使用监听器处理流
    stream.listen(
      (result) {
        result.fold(
          (failure) {
            state = state.error(failure.message);
          },
          (assistantResponse) {
            // 找到占位消息的索引
            final placeholderIndex = state.messages?.indexWhere(
              (msg) => msg.role == MessageRole.assistant && msg.isPlaceholder,
            );

            if (placeholderIndex != -1) {
              // 创建更新后的消息列表
              final updatedMessages = List<MessageModel>.from(state.messages ?? []);
              // 用实际内容替换占位符
              updatedMessages[placeholderIndex] = updatedMessages[placeholderIndex].copyWith(
                content: assistantResponse,
                isPlaceholder: false,
              );
              
              // 更新状态
              state = state.copyWith(
                messages: updatedMessages,
                isLoading: false,
                errorMessage: null,
              );
            }
          },
        );
      },
      onError: (error) {
        state = state.error(error.toString());
      },
      onDone: () {
        // 如果流结束但占位符仍存在，确保它被移除或标记为完成
        final placeholderIndex = state.messages?.indexWhere(
          (msg) => msg.role == MessageRole.assistant && msg.isPlaceholder,
        );
        
        if (placeholderIndex != -1) {
          final updatedMessages = List<MessageModel>.from(state.messages ?? []);
          // 如果没有内容就移除占位符
          if (updatedMessages[placeholderIndex].content.isEmpty) {
            updatedMessages.removeAt(placeholderIndex);
          } else {
            // 标记为非占位符
            updatedMessages[placeholderIndex] = updatedMessages[placeholderIndex].copyWith(
              isPlaceholder: false,
            );
          }
          
          state = state.copyWith(
            messages: updatedMessages,
            isLoading: false,
          );
        }
      },
    );
  }

  /// 获取智能体会话列表
  Future<void> loadAgentSessions(String agentId) async {
    state = state.loading();
    final result = await _getAgentSessionsUseCase(AgentSessionsParams(agentId: agentId));
    result.fold(
      (failure) => state = state.error(failure.message),
      (sessions) => state = state.withSessions(sessions),
    );
  }

  /// 创建新会话
  Future<void> createSession(String title) async {
    if (state.currentAgent == null) {
      state = state.error('未选择智能体');
      return;
    }

    state = state.loading();
    final result = await _createSessionUseCase(
      CreateSessionParams(
        agentId: state.currentAgent!.id,
        title: title,
      ),
    );
    result.fold(
      (failure) => state = state.error(failure.message),
      (session) => state = state.withCurrentSession(session),
    );
  }

  /// 加载会话消息历史
  Future<void> loadSessionMessages(String sessionId) async {
    state = state.loading();
    final result = await _getSessionMessagesUseCase(SessionParams(sessionId: sessionId));
    result.fold(
      (failure) => state = state.error(failure.message),
      (messages) => state = state.withMessages(messages),
    );
  }

  /// 选择会话
  void selectSession(SessionModel session) {
    state = state.withCurrentSession(session);
    loadSessionMessages(session.id);
  }

  /// 选择智能体
  void selectAgent(AgentModel agent) {
    state = state.withCurrentAgent(agent);
    loadAgentSessions(agent.id);
  }
}

/// 智能体状态提供者
final agentStateProvider = StateNotifierProvider<AgentNotifier, AgentState>((ref) {
  return AgentNotifier(
    getAgentsUseCase: ref.watch(getAgentsUseCaseProvider),
    getAgentByIdUseCase: ref.watch(getAgentByIdUseCaseProvider),
    sendMessageUseCase: ref.watch(sendMessageUseCaseProvider),
    streamFromAgentUseCase: ref.watch(streamFromAgentUseCaseProvider),
    getAgentSessionsUseCase: ref.watch(getAgentSessionsUseCaseProvider),
    createSessionUseCase: ref.watch(createSessionUseCaseProvider),
    getSessionMessagesUseCase: ref.watch(getSessionMessagesUseCaseProvider),
    presetAgents: ref.watch(presetAgentsProvider),
    agentService: ref.watch(agentServiceProvider),
  );
}); 