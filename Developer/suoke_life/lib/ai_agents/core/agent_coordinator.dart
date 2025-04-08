import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import 'agent_interface.dart';
import '../models/agent_message.dart';
import '../../core/utils/logger.dart';

/// 智能体协调器 - 基于OpenAI Agents SDK的handoffs概念设计
class AgentCoordinator {
  final String id;
  final List<Agent> agents;
  final Logger _logger = Logger('AgentCoordinator');
  
  AgentCoordinator({
    required this.agents,
  }) : id = const Uuid().v4();
  
  /// 路由消息到最合适的智能体
  Future<AgentMessage> routeMessage(AgentMessage message) async {
    try {
      _logger.info('开始路由消息到合适的智能体...');
      
      // 确定最合适处理这个任务的智能体
      final bestAgent = _findBestAgentForTask(message.content);
      
      _logger.info('将消息路由到智能体: ${bestAgent.name}');
      
      // 将消息发送给选定的智能体处理
      return await bestAgent.processMessage(message);
    } catch (e) {
      _logger.error('路由消息时出错: $e');
      return AgentMessage.assistant(
        content: '抱歉，我在处理您的请求时遇到了问题。请稍后再试。',
        status: AgentMessageStatus.error,
      );
    }
  }
  
  /// 找到最合适处理任务的智能体
  Agent _findBestAgentForTask(String task) {
    // 默认使用第一个智能体
    Agent bestAgent = agents.first;
    
    // 尝试找到能够处理此任务的专门智能体
    for (final agent in agents) {
      if (agent.canHandleTask(task)) {
        bestAgent = agent;
        break;
      }
    }
    
    return bestAgent;
  }
  
  /// 手动将任务转发给特定智能体
  Future<AgentMessage> handoffToAgent(String agentId, AgentMessage message) async {
    try {
      // 查找指定ID的智能体
      final targetAgent = agents.firstWhere(
        (agent) => agent.id == agentId,
        orElse: () => throw Exception('找不到ID为 $agentId 的智能体'),
      );
      
      _logger.info('将任务手动转发给智能体: ${targetAgent.name}');
      
      // 将消息发送给目标智能体
      return await targetAgent.processMessage(message);
    } catch (e) {
      _logger.error('转发任务时出错: $e');
      return AgentMessage.assistant(
        content: '抱歉，我在尝试将您的请求转发给专业助手时遇到了问题。请稍后再试。',
        status: AgentMessageStatus.error,
      );
    }
  }
  
  /// 获取所有可用智能体列表
  List<Map<String, String>> getAvailableAgents() {
    return agents.map((agent) => {
      'id': agent.id,
      'name': agent.name,
    }).toList();
  }
}

/// 智能体协调器Provider
final agentCoordinatorProvider = Provider<AgentCoordinator>((ref) {
  // 收集所有已注册的智能体
  final laokeAgent = ref.watch(laokeAgentProvider);
  final healthAssistantAgent = ref.watch(healthAssistantAgentProvider);
  final perceptionAgent = ref.watch(perceptionAgentProvider);
  final pulseAgent = ref.watch(pulseAgentProvider);
  
  // 创建并返回协调器实例
  return AgentCoordinator(
    agents: [
      laokeAgent,
      healthAssistantAgent,
      perceptionAgent,
      pulseAgent,
    ],
  );
}); 