import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'ai_service.dart';

class LifeAssistantService extends GetxService {
  final StorageService _storageService = Get.find();
  final AiService _aiService = Get.find();

  // 生活建议
  Future<Map<String, dynamic>> getLifeAdvice() async {
    try {
      final healthData = await _getHealthData();
      final lifeRecords = await _getLifeRecords();
      final weatherData = await _getWeatherData();

      return await _generateLifeAdvice(
        healthData: healthData,
        lifeRecords: lifeRecords,
        weatherData: weatherData,
      );
    } catch (e) {
      rethrow;
    }
  }

  // 日程管理
  Future<void> manageDailySchedule(Map<String, dynamic> schedule) async {
    try {
      // 分析日程
      final analysis = await _analyzeSchedule(schedule);
      
      // 优化日程
      final optimizedSchedule = await _optimizeSchedule(analysis);
      
      // 保存日程
      await _saveSchedule(optimizedSchedule);
      
      // 设置提醒
      await _setScheduleReminders(optimizedSchedule);
    } catch (e) {
      rethrow;
    }
  }

  // 生活记录
  Future<void> recordLifeEvent(Map<String, dynamic> event) async {
    try {
      final record = {
        'id': DateTime.now().toString(),
        'type': event['type'],
        'content': event['content'],
        'timestamp': DateTime.now().toIso8601String(),
        'tags': event['tags'] ?? [],
      };

      // 保存记录
      await _saveLifeRecord(record);

      // 分析记录
      await _analyzeLifeRecord(record);
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getHealthData() async {
    try {
      final data = await _storageService.getLocal('latest_health_data');
      return data != null ? Map<String, dynamic>.from(data) : {};
    } catch (e) {
      return {};
    }
  }

  Future<List<Map<String, dynamic>>> _getLifeRecords() async {
    try {
      final data = await _storageService.getLocal('life_records');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  Future<Map<String, dynamic>> _getWeatherData() async {
    // TODO: 实现天气数据获取
    return {};
  }

  Future<Map<String, dynamic>> _generateLifeAdvice({
    required Map<String, dynamic> healthData,
    required List<Map<String, dynamic>> lifeRecords,
    required Map<String, dynamic> weatherData,
  }) async {
    try {
      return await _aiService.queryKnowledge(
        'generate_life_advice',
        parameters: {
          'health_data': healthData,
          'life_records': lifeRecords,
          'weather_data': weatherData,
        },
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _analyzeSchedule(Map<String, dynamic> schedule) async {
    try {
      return await _aiService.queryKnowledge(
        'analyze_schedule',
        parameters: schedule,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _optimizeSchedule(Map<String, dynamic> analysis) async {
    try {
      return await _aiService.queryKnowledge(
        'optimize_schedule',
        parameters: analysis,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveSchedule(Map<String, dynamic> schedule) async {
    try {
      await _storageService.saveLocal('daily_schedule', schedule);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _setScheduleReminders(Map<String, dynamic> schedule) async {
    // TODO: 实现日程提醒设置
  }

  Future<void> _saveLifeRecord(Map<String, dynamic> record) async {
    try {
      final records = await _getLifeRecords();
      records.insert(0, record);
      await _storageService.saveLocal('life_records', records);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _analyzeLifeRecord(Map<String, dynamic> record) async {
    try {
      await _aiService.queryKnowledge(
        'analyze_life_record',
        parameters: record,
      );
    } catch (e) {
      rethrow;
    }
  }
} 