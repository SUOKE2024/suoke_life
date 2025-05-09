import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/ai_agents/llm_manager.dart';
import 'package:suoke_life/ai_agents/models/llm_model.dart';
import 'package:suoke_life/ai_agents/services/deepseek_service.dart';
import 'package:suoke_life/ai_agents/services/llm_service.dart';
import 'package:suoke_life/data/repositories/agent_repository_impl.dart';
import 'package:suoke_life/data/repositories/health_repository_impl.dart';
import 'package:suoke_life/data/repositories/diagnosis_repository_impl.dart';
import 'package:suoke_life/data/services/agent_service_impl.dart';
import 'package:suoke_life/data/services/sleep_analysis_service_impl.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';
import 'package:suoke_life/domain/repositories/health_repository.dart';
import 'package:suoke_life/domain/repositories/diagnosis_repository.dart';
import 'package:suoke_life/domain/services/agent_service.dart';
import 'package:suoke_life/domain/services/sleep_analysis_service.dart';
import 'package:suoke_life/presentation/life/view_models/health_record_view_model.dart';
import 'package:suoke_life/presentation/life/view_models/sleep_analysis_view_model.dart';
import 'package:suoke_life/presentation/suoke/view_models/agent_view_model.dart';
import 'package:suoke_life/data/repositories/chat_repository_impl.dart';
import 'package:suoke_life/domain/repositories/chat_repository.dart';
import 'package:suoke_life/presentation/home/view_models/chat_list_view_model.dart';
import 'package:suoke_life/domain/services/voice_service.dart';
import 'package:suoke_life/data/services/voice_service_impl.dart';
import 'package:suoke_life/domain/models/voice_state.dart';

/// 全局依赖注入Provider

/// SharedPreferences Provider
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('需要在ProviderScope中覆盖此Provider');
});

/// 健康数据仓库Provider重写
final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  final sharedPrefs = ref.watch(sharedPreferencesProvider);
  return HealthRepositoryImpl(sharedPrefs);
});

/// 睡眠分析服务Provider
final sleepAnalysisServiceProvider = Provider<SleepAnalysisService>((ref) {
  final healthRepository = ref.watch(healthRepositoryProvider);
  return SleepAnalysisServiceImpl(healthRepository);
});

/// 健康记录视图模型Provider
final healthRecordViewModelProvider = StateNotifierProvider<HealthRecordViewModel, HealthRecordState>((ref) {
  final healthRepository = ref.watch(healthRepositoryProvider);
  return HealthRecordViewModel(healthRepository);
});

/// 睡眠分析视图模型Provider
final sleepAnalysisViewModelProvider = StateNotifierProvider<SleepAnalysisViewModel, SleepAnalysisState>((ref) {
  final sleepAnalysisService = ref.watch(sleepAnalysisServiceProvider);
  final healthRepository = ref.watch(healthRepositoryProvider);
  return SleepAnalysisViewModel(sleepAnalysisService, healthRepository);
});

/// 智能体相关Provider
/// 智能体仓库Provider
final agentRepositoryProvider = Provider<AgentRepository>((ref) {
  final sharedPrefs = ref.watch(sharedPreferencesProvider);
  return AgentRepositoryImpl(sharedPrefs);
});

/// 智能体服务Provider
final agentServiceProvider = Provider<AgentService>((ref) {
  final agentRepository = ref.watch(agentRepositoryProvider);
  final sharedPrefs = ref.watch(sharedPreferencesProvider);
  return AgentServiceImpl(agentRepository, sharedPrefs);
});

/// 聊天仓库Provider
final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  return ChatRepositoryImpl();
});

/// 聊天列表视图模型Provider
final chatListViewModelProvider = StateNotifierProvider<ChatListViewModel, ChatListViewState>((ref) {
  final chatRepository = ref.watch(chatRepositoryProvider);
  return ChatListViewModel(chatRepository);
});

/// 语音服务Provider
final voiceServiceProvider = Provider<VoiceService>((ref) {
  return VoiceServiceImpl();
});

/// 语音状态Provider
final voiceStateProvider = StateProvider<VoiceState>((ref) {
  return VoiceState.idle;
});

/// 语音识别文本Provider
final voiceRecognitionTextProvider = StateProvider<String>((ref) {
  return '';
});

/// LLM服务Provider
final llmServiceProvider = Provider<LLMService>((ref) {
  return DeepSeekService();
});

/// LLM管理器Provider
final llmManagerProvider = Provider<LLMManager>((ref) {
  return LLMManager();
});

/// 当前LLM类型Provider
final llmTypeProvider = StateProvider<LLMType>((ref) {
  return LLMType.deepSeek;
});

/// 智能体系统提示词Provider
final agentSystemPromptProvider = Provider.family<String, AgentType>((ref, agentType) {
  return getAgentSystemPrompt(agentType);
});

/// 四诊仓库提供者
final diagnosisRepositoryProvider = Provider<DiagnosisRepository>((ref) {
  return DiagnosisRepositoryImpl();
});

/// 当前活跃诊断会话ID提供者
final activeDiagnosisSessionIdProvider = StateProvider<String?>((ref) => null);
