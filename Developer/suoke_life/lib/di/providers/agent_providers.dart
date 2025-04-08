import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/data/datasources/remote/agent_remote_datasource.dart';
import 'package:suoke_life/data/repositories/agent_repository_impl.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';
import 'package:suoke_life/domain/usecases/agent/get_agents_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/get_agent_by_id_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/send_message_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/stream_from_agent_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/get_agent_sessions_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/create_session_usecase.dart';
import 'package:suoke_life/domain/usecases/agent/get_session_messages_usecase.dart';
import 'package:suoke_life/di/providers/api_providers.dart';
import 'package:suoke_life/data/models/agent_model.dart';

/// 智能体远程数据源提供者
final agentRemoteDataSourceProvider = Provider<AgentRemoteDataSource>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return AgentRemoteDataSourceImpl(apiClient);
});

/// 智能体存储库提供者
final agentRepositoryProvider = Provider<AgentRepository>((ref) {
  final remoteDataSource = ref.watch(agentRemoteDataSourceProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  
  return AgentRepositoryImpl(
    remoteDataSource: remoteDataSource,
    networkInfo: networkInfo,
  );
});

/// 获取智能体用例提供者
final getAgentsUseCaseProvider = Provider<GetAgentsUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return GetAgentsUseCase(repository);
});

/// 获取指定智能体用例提供者
final getAgentByIdUseCaseProvider = Provider<GetAgentByIdUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return GetAgentByIdUseCase(repository);
});

/// 发送消息用例提供者
final sendMessageUseCaseProvider = Provider<SendMessageUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return SendMessageUseCase(repository);
});

/// 流式响应用例提供者
final streamFromAgentUseCaseProvider = Provider<StreamFromAgentUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return StreamFromAgentUseCase(repository);
});

/// 获取智能体会话列表用例提供者
final getAgentSessionsUseCaseProvider = Provider<GetAgentSessionsUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return GetAgentSessionsUseCase(repository);
});

/// 创建会话用例提供者
final createSessionUseCaseProvider = Provider<CreateSessionUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return CreateSessionUseCase(repository);
});

/// 获取会话消息历史用例提供者
final getSessionMessagesUseCaseProvider = Provider<GetSessionMessagesUseCase>((ref) {
  final repository = ref.watch(agentRepositoryProvider);
  return GetSessionMessagesUseCase(repository);
});

/// 预设智能体提供者
final presetAgentsProvider = Provider<List<AgentModel>>((ref) {
  // 创建智能体当前时间
  final now = DateTime.now();
  
  // 返回预设的智能体列表
  return [
    // 小柯智能体
    AgentModel(
      id: 'xiaoke-service',
      name: '小柯',
      description: '小柯是一位专注于日常健康管理的AI助手，擅长健康习惯培养、饮食指导和生活方式调整。',
      avatarUrl: 'https://suoke.life/assets/agents/xiaoke_avatar.png',
      type: '健康管理',
      capabilities: {
        'health_tracking': true,
        'diet_suggestions': true,
        'lifestyle_advice': true,
      },
      createdAt: now,
      updatedAt: now,
    ),
    
    // 小艾智能体
    AgentModel(
      id: 'xiaoai-service',
      name: '小艾',
      description: '小艾是索克生活的主要AI助手，擅长全方位健康咨询、中医理论解读和个性化健康方案制定。',
      avatarUrl: 'https://suoke.life/assets/agents/xiaoai_avatar.png',
      type: '综合顾问',
      capabilities: {
        'tcm_knowledge': true,
        'health_consultation': true,
        'personalized_plans': true,
        'knowledge_graph': true,
      },
      createdAt: now,
      updatedAt: now,
    ),
    
    // 索尔智能体
    AgentModel(
      id: 'soer-service',
      name: '索尔',
      description: '索尔是专门针对情绪和心理健康的AI顾问，擅长提供心理支持、压力管理和情绪调节建议。',
      avatarUrl: 'https://suoke.life/assets/agents/soer_avatar.png',
      type: '心理顾问',
      capabilities: {
        'emotional_support': true,
        'stress_management': true,
        'mood_tracking': true,
        'meditation_guide': true,
      },
      createdAt: now,
      updatedAt: now,
    ),
    
    // 老柯智能体
    AgentModel(
      id: 'laoke-service',
      name: '老柯',
      description: '老柯是中医理论专家，精通经络、穴位、中药和传统养生理论，提供专业的中医健康指导。',
      avatarUrl: 'https://suoke.life/assets/agents/laoke_avatar.png',
      type: '中医专家',
      capabilities: {
        'acupuncture_advice': true,
        'herbal_medicine': true,
        'meridian_knowledge': true,
        'seasonal_health': true,
      },
      createdAt: now,
      updatedAt: now,
    ),
  ];
});