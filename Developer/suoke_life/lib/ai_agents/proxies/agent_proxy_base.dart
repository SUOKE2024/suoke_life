import 'dart:async';
import 'package:suoke_life/ai_agents/models/agent_message.dart';
import 'package:suoke_life/core/network/api_client.dart';

abstract class AgentProxyBase {
  final String agentId;
  final ApiClient apiClient;
  final StreamController<AgentMessage> _messageController = StreamController.broadcast();
  
  Stream<AgentMessage> get messageStream => _messageController.stream;
  
  AgentProxyBase({required this.agentId, required this.apiClient});
  
  Future<AgentMessage> sendMessage(String message, {String? conversationId});
  
  Stream<AgentMessage> sendMessageStream(String message, {String? conversationId});
  
  void dispose() {
    _messageController.close();
  }
  
  // 发送消息到流
  void _addMessageToStream(AgentMessage message) {
    if (!_messageController.isClosed) {
      _messageController.add(message);
    }
  }
}
