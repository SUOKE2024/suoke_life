import 'package:suoke_life/domain/models/agent_model.dart';

/// 智能体服务接口
abstract class AgentService {
  /// 初始化智能体系统
  Future<void> initializeAgentSystem();

  /// 切换活跃智能体
  Future<Agent> switchActiveAgent(AgentType type);

  /// 获取默认智能体
  Future<Agent> getDefaultAgent();

  /// 获取最近活跃的智能体
  Future<Agent?> getLastActiveAgent();

  /// 分析消息并推荐合适的智能体
  Future<Agent> recommendAgentForMessage(String message);

  /// 获取智能体的预设回复
  Future<List<String>> getAgentSuggestedResponses(AgentType type);

  /// 检查并处理智能体间的任务转换
  /// 
  /// 根据消息内容判断是否需要将任务转交给其他智能体
  Future<Agent?> checkAndHandleAgentSwitchRequest({
    required AgentType currentAgentType,
    required String message,
  });

  /// 生成四诊推荐问题
  Future<List<String>> generateDiagnosisQuestions(AgentType agentType);

  /// 分析会话并生成摘要
  Future<String> generateConversationSummary(String conversationId);

  /// 获取智能体针对特定健康问题的建议
  Future<String> getHealthAdvice({
    required AgentType agentType,
    required String healthIssue,
  });

  /// 获取智能体的交互历史摘要（用于提供上下文）
  Future<String> getInteractionHistory(String userId, {int limit = 5});
} 