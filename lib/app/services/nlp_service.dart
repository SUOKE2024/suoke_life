import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'ai_service.dart';

class NlpService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AiService _aiService = Get.find();

  // 情感分析
  Future<Map<String, dynamic>> analyzeSentiment(String text) async {
    try {
      final response = await _aiService.queryKnowledge(
        'analyze_sentiment',
        parameters: {'text': text},
      );
      
      await _logAnalysis('sentiment', text, response);
      return response;
    } catch (e) {
      await _loggingService.log('error', 'Failed to analyze sentiment', data: {'error': e.toString()});
      return {};
    }
  }

  // 意图识别
  Future<Map<String, dynamic>> detectIntent(String text) async {
    try {
      final response = await _aiService.queryKnowledge(
        'detect_intent',
        parameters: {'text': text},
      );
      
      await _logAnalysis('intent', text, response);
      return response;
    } catch (e) {
      await _loggingService.log('error', 'Failed to detect intent', data: {'error': e.toString()});
      return {};
    }
  }

  // 实体识别
  Future<List<Map<String, dynamic>>> extractEntities(String text) async {
    try {
      final response = await _aiService.queryKnowledge(
        'extract_entities',
        parameters: {'text': text},
      );
      
      await _logAnalysis('entities', text, response);
      return List<Map<String, dynamic>>.from(response['entities'] ?? []);
    } catch (e) {
      await _loggingService.log('error', 'Failed to extract entities', data: {'error': e.toString()});
      return [];
    }
  }

  // 文本分类
  Future<Map<String, double>> classifyText(String text) async {
    try {
      final response = await _aiService.queryKnowledge(
        'classify_text',
        parameters: {'text': text},
      );
      
      await _logAnalysis('classification', text, response);
      return Map<String, double>.from(response['categories'] ?? {});
    } catch (e) {
      await _loggingService.log('error', 'Failed to classify text', data: {'error': e.toString()});
      return {};
    }
  }

  // 关键词提取
  Future<List<String>> extractKeywords(String text) async {
    try {
      final response = await _aiService.queryKnowledge(
        'extract_keywords',
        parameters: {'text': text},
      );
      
      await _logAnalysis('keywords', text, response);
      return List<String>.from(response['keywords'] ?? []);
    } catch (e) {
      await _loggingService.log('error', 'Failed to extract keywords', data: {'error': e.toString()});
      return [];
    }
  }

  // 文本摘要
  Future<String> generateSummary(String text, {int maxLength = 200}) async {
    try {
      final response = await _aiService.queryKnowledge(
        'generate_summary',
        parameters: {
          'text': text,
          'max_length': maxLength,
        },
      );
      
      await _logAnalysis('summary', text, response);
      return response['summary'] ?? '';
    } catch (e) {
      await _loggingService.log('error', 'Failed to generate summary', data: {'error': e.toString()});
      return '';
    }
  }

  Future<void> _logAnalysis(
    String type,
    String text,
    Map<String, dynamic> result,
  ) async {
    try {
      final analysisLog = {
        'type': type,
        'text': text,
        'result': result,
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      await _saveToHistory(analysisLog);
      await _loggingService.log('info', 'NLP analysis completed', data: analysisLog);
    } catch (e) {
      // 忽略日志错误
    }
  }

  Future<void> _saveToHistory(Map<String, dynamic> analysis) async {
    try {
      final history = await _getHistory();
      history.insert(0, analysis);
      
      // 只保留最近100条记录
      if (history.length > 100) {
        history.removeRange(100, history.length);
      }
      
      await _storageService.saveLocal('nlp_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getHistory() async {
    try {
      final data = await _storageService.getLocal('nlp_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 