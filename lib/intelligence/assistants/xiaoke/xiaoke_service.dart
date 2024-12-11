import 'package:flutter/foundation.dart';
import '../../../models/message.dart';
import '../../../services/ai/core_algorithm_service.dart';
import '../../../services/storage/data_storage_service.dart';

class XiaokeService {
  final CoreAlgorithmService _algorithmService;
  final DataStorageService _storageService;

  static const String name = '小克';
  static const String description = '您的高效商务助手，提升工作效率和决策支持';

  XiaokeService({
    required CoreAlgorithmService algorithmService,
    required DataStorageService storageService,
  })  : _algorithmService = algorithmService,
        _storageService = storageService;

  // 处理用户消息
  Future<Message> processMessage(Message userMessage) async {
    try {
      // 保存用户消息
      await _storageService.saveMessage(userMessage);
      
      // 分析用户意图
      final intent = await _analyzeIntent(userMessage);
      
      // 根据意图生成回复
      final response = await _generateResponse(userMessage, intent);
      
      // 保存助手回复
      await _storageService.saveMessage(response);
      
      return response;
    } catch (e) {
      debugPrint('Xiaoke failed to process message: $e');
      rethrow;
    }
  }

  // 分析用户意图
  Future<Map<String, dynamic>> _analyzeIntent(Message message) async {
    try {
      // 分析用户意图和商务需求
      final analysis = await _algorithmService.performComprehensiveAnalysis(
        text: message.content,
        context: message.context,
      );
      
      // 识别商务领域
      final domain = await _identifyBusinessDomain(analysis);
      
      return {
        'type': 'business_query',
        'domain': domain,
        'analysis': analysis,
        'priority': _assessPriority(analysis),
      };
    } catch (e) {
      debugPrint('Intent analysis failed: $e');
      rethrow;
    }
  }

  // 生成回复
  Future<Message> _generateResponse(
    Message userMessage,
    Map<String, dynamic> intent,
  ) async {
    try {
      String response;
      
      // 根据意图类型生成不同的回复
      switch (intent['domain']) {
        case 'supply_chain':
          response = await _handleSupplyChainQuery(intent);
          break;
        case 'market_analysis':
          response = await _handleMarketAnalysis(intent);
          break;
        case 'business_strategy':
          response = await _handleBusinessStrategy(intent);
          break;
        case 'operation_optimization':
          response = await _handleOperationOptimization(intent);
          break;
        default:
          response = await _handleGeneralBusinessQuery(intent);
      }
      
      return Message(
        role: 'assistant',
        content: response,
        timestamp: DateTime.now(),
        context: userMessage.context,
      );
    } catch (e) {
      debugPrint('Response generation failed: $e');
      rethrow;
    }
  }

  // 识别商务领域
  Future<String> _identifyBusinessDomain(Map<String, dynamic> analysis) async {
    try {
      final keywords = analysis['keywords'] as List<String>;
      final context = analysis['context'] as Map<String, dynamic>;
      
      // 根据关键词和上下文识别领域
      return await _algorithmService.identifyBusinessDomain(
        keywords: keywords,
        context: context,
      );
    } catch (e) {
      debugPrint('Domain identification failed: $e');
      return 'general';
    }
  }

  // 评估优先级
  String _assessPriority(Map<String, dynamic> analysis) {
    try {
      final urgency = analysis['urgency'] as double;
      final importance = analysis['importance'] as double;
      
      if (urgency > 0.8 || importance > 0.8) {
        return 'high';
      } else if (urgency > 0.5 || importance > 0.5) {
        return 'medium';
      } else {
        return 'low';
      }
    } catch (e) {
      debugPrint('Priority assessment failed: $e');
      return 'medium';
    }
  }

  // 处理供应链查询
  Future<String> _handleSupplyChainQuery(Map<String, dynamic> intent) async {
    try {
      final analysis = intent['analysis'];
      final priority = intent['priority'];
      
      return await _algorithmService.generateSupplyChainResponse(
        analysis: analysis,
        priority: priority,
      );
    } catch (e) {
      debugPrint('Supply chain query handling failed: $e');
      return '这个供应链问题需要更多数据支持。请提供相关数据。';
    }
  }

  // 处理市场分析
  Future<String> _handleMarketAnalysis(Map<String, dynamic> intent) async {
    try {
      final analysis = intent['analysis'];
      
      return await _algorithmService.generateMarketAnalysis(
        analysis: analysis,
      );
    } catch (e) {
      debugPrint('Market analysis handling failed: $e');
      return '让我为您分析市场趋势和机会。';
    }
  }

  // 处理商业战略
  Future<String> _handleBusinessStrategy(Map<String, dynamic> intent) async {
    try {
      final analysis = intent['analysis'];
      
      return await _algorithmService.generateBusinessStrategy(
        analysis: analysis,
      );
    } catch (e) {
      debugPrint('Business strategy handling failed: $e');
      return '这需要结合您的具体业务场景来制定策略。';
    }
  }

  // 处理运营优化
  Future<String> _handleOperationOptimization(Map<String, dynamic> intent) async {
    try {
      final analysis = intent['analysis'];
      
      return await _algorithmService.generateOperationOptimization(
        analysis: analysis,
      );
    } catch (e) {
      debugPrint('Operation optimization handling failed: $e');
      return '让我帮您找出运营中的优化空间。';
    }
  }

  // 处理一般商务查询
  Future<String> _handleGeneralBusinessQuery(Map<String, dynamic> intent) async {
    try {
      final analysis = intent['analysis'];
      
      return await _algorithmService.generateGeneralBusinessResponse(
        analysis: analysis,
      );
    } catch (e) {
      debugPrint('General business query handling failed: $e');
      return '这是一个很好的商业问题。让我为您分析。';
    }
  }

  // 获取历史对话
  Future<List<Message>> getConversationHistory(String userId, {int limit = 20}) async {
    try {
      return await _storageService.getMessages(userId, limit: limit);
    } catch (e) {
      debugPrint('Failed to get conversation history: $e');
      return [];
    }
  }

  // 清除历史对话
  Future<void> clearConversationHistory(String userId) async {
    try {
      await _storageService.clearMessages(userId);
    } catch (e) {
      debugPrint('Failed to clear conversation history: $e');
      rethrow;
    }
  }

  // 获取助手状态
  Future<Map<String, dynamic>> getStatus() async {
    try {
      return {
        'name': name,
        'description': description,
        'isAvailable': true,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('Failed to get assistant status: $e');
      return {
        'name': name,
        'description': description,
        'isAvailable': false,
        'error': e.toString(),
      };
    }
  }
} 