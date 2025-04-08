import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/data/models/session_model.dart';

/// 智能体存储库接口
abstract class AgentRepository {
  /// 获取所有可用智能体
  Future<Either<Failure, List<AgentModel>>> getAgents();
  
  /// 获取指定智能体详情
  Future<Either<Failure, AgentModel>> getAgentById(String agentId);
  
  /// 发送消息给智能体
  Future<Either<Failure, MessageModel>> sendMessage(String agentId, String message, {String? sessionId});
  
  /// 从智能体获取流式响应
  Stream<Either<Failure, MessageModel>> streamFromAgent(String agentId, String message, {String? sessionId});
  
  /// 获取智能体会话列表
  Future<Either<Failure, List<SessionModel>>> getAgentSessions(String agentId);
  
  /// 创建新会话
  Future<Either<Failure, SessionModel>> createSession(String agentId, String title);
  
  /// 获取会话消息历史
  Future<Either<Failure, List<MessageModel>>> getSessionMessages(String sessionId);
} 