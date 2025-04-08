import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/data/models/session_model.dart';

/// 智能体远程数据源接口
abstract class AgentRemoteDataSource {
  /// 获取所有可用智能体
  Future<List<AgentModel>> getAgents();
  
  /// 获取指定智能体详情
  Future<AgentModel> getAgentById(String agentId);
  
  /// 发送消息给智能体
  Future<MessageModel> sendMessage(String agentId, String message, {String? sessionId});
  
  /// 从智能体获取流式响应
  Stream<MessageModel> streamFromAgent(String agentId, String message, {String? sessionId});
  
  /// 获取智能体会话列表
  Future<List<SessionModel>> getAgentSessions(String agentId);
  
  /// 创建新会话
  Future<SessionModel> createSession(String agentId, String title);
  
  /// 获取会话消息历史
  Future<List<MessageModel>> getSessionMessages(String sessionId);
}

/// 智能体远程数据源实现
class AgentRemoteDataSourceImpl implements AgentRemoteDataSource {
  final ApiClient _apiClient;
  
  AgentRemoteDataSourceImpl(this._apiClient);
  
  @override
  Future<List<AgentModel>> getAgents() async {
    try {
      final response = await _apiClient.get('/api/v1/agents');
      final List<dynamic> agentsJson = response.data['agents'];
      return agentsJson.map((json) => AgentModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<AgentModel> getAgentById(String agentId) async {
    try {
      final response = await _apiClient.get('/api/v1/agents/$agentId');
      return AgentModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<MessageModel> sendMessage(String agentId, String message, {String? sessionId}) async {
    try {
      final response = await _apiClient.post(
        '/api/v1/agents/$agentId/messages',
        data: {
          'content': message,
          if (sessionId != null) 'session_id': sessionId
        }
      );
      return MessageModel.fromJson(response.data['message']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Stream<MessageModel> streamFromAgent(String agentId, String message, {String? sessionId}) {
    return _apiClient
        .streamFromAgent(agentId, message, conversationId: sessionId)
        .map((json) => MessageModel.fromJson(json['message']));
  }
  
  @override
  Future<List<SessionModel>> getAgentSessions(String agentId) async {
    try {
      final response = await _apiClient.get('/api/v1/agents/$agentId/sessions');
      final List<dynamic> sessionsJson = response.data['sessions'];
      return sessionsJson.map((json) => SessionModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<SessionModel> createSession(String agentId, String title) async {
    try {
      final response = await _apiClient.post(
        '/api/v1/sessions',
        data: {
          'agent_id': agentId,
          'title': title
        }
      );
      return SessionModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<List<MessageModel>> getSessionMessages(String sessionId) async {
    try {
      final response = await _apiClient.get('/api/v1/sessions/$sessionId/messages');
      final List<dynamic> messagesJson = response.data['messages'];
      return messagesJson.map((json) => MessageModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  Exception _handleError(DioException e) {
    if (e.response?.statusCode == 401) {
      return UnauthorizedException('未授权访问，请先登录');
    } else if (e.response?.statusCode == 404) {
      return NotFoundException('资源不存在: ${e.message}');
    } else {
      return NetworkException('网络请求失败: ${e.message}');
    }
  }
}

/// 网络异常
class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
}

/// 未授权异常
class UnauthorizedException implements Exception {
  final String message;
  UnauthorizedException(this.message);
}

/// 资源不存在异常
class NotFoundException implements Exception {
  final String message;
  NotFoundException(this.message);
} 