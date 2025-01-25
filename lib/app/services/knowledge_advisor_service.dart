import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'ai_service.dart';

class KnowledgeAdvisorService extends GetxService {
  final StorageService _storageService = Get.find();
  final AiService _aiService = Get.find();

  // 知识探索
  Future<Map<String, dynamic>> exploreKnowledge(String topic) async {
    try {
      final knowledge = await _aiService.queryKnowledge(
        'explore_knowledge',
        parameters: {'topic': topic},
      );

      // 记录搜索历史
      await _saveSearchHistory(topic);

      return knowledge;
    } catch (e) {
      rethrow;
    }
  }

  // 研究分析
  Future<Map<String, dynamic>> analyzeResearch(String topic) async {
    try {
      return await _aiService.queryKnowledge(
        'analyze_research',
        parameters: {'topic': topic},
      );
    } catch (e) {
      rethrow;
    }
  }

  // 知识图谱构建
  Future<Map<String, dynamic>> buildKnowledgeGraph(String domain) async {
    try {
      return await _aiService.queryKnowledge(
        'build_knowledge_graph',
        parameters: {'domain': domain},
      );
    } catch (e) {
      rethrow;
    }
  }

  // 保存搜索历史
  Future<void> _saveSearchHistory(String topic) async {
    try {
      final history = await _getSearchHistory();
      history.insert(0, {
        'topic': topic,
        'timestamp': DateTime.now().toIso8601String(),
      });

      // 只保留最近100条记录
      if (history.length > 100) {
        history.removeRange(100, history.length);
      }

      await _storageService.saveLocal('search_history', history);
    } catch (e) {
      rethrow;
    }
  }

  // 获取搜索历史
  Future<List<Map<String, dynamic>>> _getSearchHistory() async {
    try {
      final data = await _storageService.getLocal('search_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 