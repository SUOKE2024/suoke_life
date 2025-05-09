import 'package:suoke_life/domain/models/agent_model.dart';

/// 智能体仓库接口
abstract class AgentRepository {
  /// 获取所有可用智能体列表
  Future<List<Agent>> getAgents();

  /// 根据ID获取智能体
  Future<Agent?> getAgentById(String agentId);

  /// 获取指定类型的智能体
  Future<Agent?> getAgentByType(AgentType type);

  /// 获取用户的所有会话
  Future<List<AgentConversation>> getConversations(String userId);

  /// 获取指定会话
  Future<AgentConversation?> getConversationById(String conversationId);

  /// 创建新会话
  Future<AgentConversation> createConversation({
    required String userId,
    required String agentId,
    required String title,
  });

  /// 获取会话的所有消息
  Future<List<AgentMessage>> getMessages(String conversationId, {int limit = 20, int offset = 0});

  /// 发送消息
  Future<AgentMessage> sendMessage({
    required String conversationId,
    required String senderId,
    required MessageType messageType,
    required ContentType contentType,
    required String content,
    Map<String, dynamic>? extraData,
  });

  /// 生成智能体响应
  Future<AgentMessage> generateAgentResponse({
    required String conversationId,
    required String agentId,
    required List<AgentMessage> conversationHistory,
  });

  /// 更新会话状态
  Future<void> updateConversationStatus(String conversationId, {bool? isActive, String? title});

  /// 删除会话
  Future<void> deleteConversation(String conversationId);

  /// 删除消息
  Future<void> deleteMessage(String messageId);

  /// 获取用户与智能体的交互历史
  Future<List<UserInteraction>> getUserInteractions(String userId, {int limit = 5});
} 