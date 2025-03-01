import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:get_it/get_it.dart';

import '../core/agent_microkernel.dart';
import '../core/autonomous_learning_system.dart';
import '../core/security_privacy_framework.dart';
import '../rag/rag_service.dart';

/// GetIt实例Provider
final getItProvider = Provider<GetIt>((ref) {
  return GetIt.instance;
});

/// 代理微内核Provider
final agentMicrokernelProvider = Provider<AgentMicrokernel>((ref) {
  return GetIt.instance<AgentMicrokernel>();
});

/// 自主学习系统Provider
final autonomousLearningSystemProvider = Provider<AutonomousLearningSystem>((ref) {
  return GetIt.instance<AutonomousLearningSystem>();
});

/// 安全与隐私框架Provider
final securityPrivacyFrameworkProvider = Provider<SecurityPrivacyFramework>((ref) {
  return GetIt.instance<SecurityPrivacyFramework>();
});

/// RAG服务Provider
final ragServiceProvider = Provider<RAGService>((ref) {
  return GetIt.instance<RAGService>();
});

/// 学习模式Provider
final learningModeProvider = StateProvider<LearningMode>((ref) {
  // 默认使用主动学习模式
  return LearningMode.active;
});

/// 学习事件流Provider
final learningEventsStreamProvider = StreamProvider<List<LearningEvent>>((ref) async* {
  final List<LearningEvent> events = [];
  yield events;
  
  // 在实际应用中，这里应该监听学习事件的流
  // 并在有新事件时更新列表
});

/// 知识单元Provider
final knowledgeUnitsProvider = FutureProvider.family<List<KnowledgeUnit>, String>((ref, domain) async {
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  return learningSystem.getKnowledgeByDomain(domain);
});

/// 学习统计信息Provider
final learningStatisticsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  return learningSystem.getLearningStatistics();
}); 