import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../registry/agent_registry.dart';
import 'multimodal_interaction_engine.dart';
import '../../providers/ai_core_providers.dart';
import '../../providers/interaction_providers.dart';

/// 多模态交互引擎Provider
final multimodalInteractionEngineProvider = interactionEngineServiceProvider;

/// 用户交互流Provider
final userInteractionStreamProvider = StreamProvider<UserInteraction>((ref) {
  final engine = ref.watch(interactionEngineServiceProvider);
  return engine.userInteractionStream;
});

/// 代理响应流Provider
final agentResponseStreamProvider = StreamProvider<AgentResponse>((ref) {
  final engine = ref.watch(interactionEngineServiceProvider);
  return engine.agentResponseStream;
});

/// 当前会话ID Provider
final sessionIdStateProvider = StateProvider<String>((ref) {
  return DateTime.now().millisecondsSinceEpoch.toString();
});

/// 是否正在进行语音输入的状态Provider
final isListeningStateProvider = StateProvider<bool>((ref) => false);

/// 语音识别结果Provider
final voiceRecognitionStateProvider = StateProvider<String>((ref) => '');

/// 消息历史Provider - 使用StateNotifier管理消息列表状态
class MessageHistoryNotifier extends StateNotifier<List<dynamic>> {
  MessageHistoryNotifier() : super([]);
  
  void addUserInteraction(UserInteraction interaction) {
    state = [...state, interaction];
  }
  
  void addAgentResponse(AgentResponse response) {
    state = [...state, response];
  }
  
  void clearHistory() {
    state = [];
  }
}

/// 消息历史StateNotifierProvider
final messageHistoryProvider = StateNotifierProvider<MessageHistoryNotifier, List<dynamic>>((ref) {
  final notifier = MessageHistoryNotifier();
  
  // 监听用户交互流
  ref.listen<AsyncValue<UserInteraction>>(
    userInteractionStreamProvider,
    (previous, next) {
      next.whenData((interaction) {
        notifier.addUserInteraction(interaction);
      });
    },
  );
  
  // 监听代理响应流
  ref.listen<AsyncValue<AgentResponse>>(
    agentResponseStreamProvider,
    (previous, next) {
      next.whenData((response) {
        notifier.addAgentResponse(response);
      });
    },
  );
  
  return notifier;
});

/// @deprecated 使用sessionIdStateProvider替代
@Deprecated('使用sessionIdStateProvider替代')
final sessionIdProvider = sessionIdStateProvider;

/// @deprecated 使用isListeningStateProvider替代
@Deprecated('使用isListeningStateProvider替代')
final isListeningProvider = isListeningStateProvider;

/// @deprecated 使用voiceRecognitionStateProvider替代
@Deprecated('使用voiceRecognitionStateProvider替代')
final voiceRecognitionResultProvider = voiceRecognitionStateProvider; 