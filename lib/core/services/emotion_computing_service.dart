import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'ai_service.dart';

class EmotionComputingService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AiService _aiService = Get.find();

  final currentEmotion = <String, double>{}.obs;
  final emotionHistory = <Map<String, dynamic>>[].obs;

  // 分析情感状态
  Future<Map<String, double>> analyzeEmotion(Map<String, dynamic> input) async {
    try {
      final emotions = await _detectEmotions(input);
      currentEmotion.value = emotions;
      
      await _saveEmotionRecord(emotions);
      return emotions;
    } catch (e) {
      await _loggingService.log('error', 'Failed to analyze emotion', data: {'error': e.toString()});
      return {};
    }
  }

  // 情感趋势分析
  Future<Map<String, dynamic>> analyzeEmotionTrends({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final records = await _getEmotionRecords(startDate, endDate);
      return await _analyzeEmotionPatterns(records);
    } catch (e) {
      await _loggingService.log('error', 'Failed to analyze emotion trends', data: {'error': e.toString()});
      return {};
    }
  }

  // 情感干预建议
  Future<List<String>> getEmotionSuggestions(Map<String, double> emotions) async {
    try {
      final response = await _aiService.queryKnowledge(
        'emotion_suggestions',
        parameters: {'emotions': emotions},
      );
      return List<String>.from(response['suggestions'] ?? []);
    } catch (e) {
      await _loggingService.log('error', 'Failed to get emotion suggestions', data: {'error': e.toString()});
      return [];
    }
  }

  Future<Map<String, double>> _detectEmotions(Map<String, dynamic> input) async {
    try {
      final response = await _aiService.queryKnowledge(
        'detect_emotions',
        parameters: input,
      );
      return Map<String, double>.from(response['emotions'] ?? {});
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveEmotionRecord(Map<String, double> emotions) async {
    try {
      final record = {
        'emotions': emotions,
        'timestamp': DateTime.now().toIso8601String(),
      };

      emotionHistory.insert(0, record);

      // 只保留最近100条记录
      if (emotionHistory.length > 100) {
        emotionHistory.removeRange(100, emotionHistory.length);
      }

      await _storageService.saveLocal('emotion_history', emotionHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getEmotionRecords([
    DateTime? startDate,
    DateTime? endDate,
  ]) async {
    try {
      final records = await _loadEmotionHistory();
      
      if (startDate == null && endDate == null) {
        return records;
      }

      return records.where((record) {
        final timestamp = DateTime.parse(record['timestamp']);
        if (startDate != null && timestamp.isBefore(startDate)) {
          return false;
        }
        if (endDate != null && timestamp.isAfter(endDate)) {
          return false;
        }
        return true;
      }).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _loadEmotionHistory() async {
    try {
      final data = await _storageService.getLocal('emotion_history');
      if (data != null) {
        emotionHistory.value = List<Map<String, dynamic>>.from(data);
      }
      return emotionHistory;
    } catch (e) {
      return [];
    }
  }

  Future<Map<String, dynamic>> _analyzeEmotionPatterns(
    List<Map<String, dynamic>> records,
  ) async {
    try {
      return await _aiService.queryKnowledge(
        'analyze_emotion_patterns',
        parameters: {'records': records},
      );
    } catch (e) {
      rethrow;
    }
  }

  @override
  void onInit() {
    super.onInit();
    _loadEmotionHistory();
  }
} 