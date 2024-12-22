import 'package:get/get.dart';
import 'package:logger/logger.dart';
import '../core/storage/storage_service.dart';

class LoggingService extends GetxService {
  final StorageService _storageService = Get.find();
  late final Logger _logger;

  final logs = <Map<String, dynamic>>[].obs;
  final logLevel = 'info'.obs;

  Future<LoggingService> init() async {
    _initLogger();
    await _loadLogs();
    return this;
  }

  void _initLogger() {
    _logger = Logger(
      printer: PrettyPrinter(
        methodCount: 2,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
        printTime: true,
      ),
    );
  }

  Future<void> log(String level, String message, {Map<String, dynamic>? data}) async {
    try {
      // 记录日志
      switch (level.toLowerCase()) {
        case 'debug':
          _logger.d(message);
          break;
        case 'info':
          _logger.i(message);
          break;
        case 'warning':
          _logger.w(message);
          break;
        case 'error':
          _logger.e(message);
          break;
        default:
          _logger.i(message);
      }

      // 构建日志条目
      final logEntry = {
        'level': level,
        'message': message,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      };

      // 添加到日志列表
      logs.insert(0, logEntry);

      // 保存到本地
      await _saveLogs();
    } catch (e) {
      print('Error logging: $e');
    }
  }

  Future<void> setLogLevel(String level) async {
    try {
      logLevel.value = level;
      await _storageService.saveLocal('log_level', level);
    } catch (e) {
      print('Error setting log level: $e');
    }
  }

  Future<void> clearLogs() async {
    try {
      logs.clear();
      await _storageService.removeLocal('app_logs');
    } catch (e) {
      print('Error clearing logs: $e');
    }
  }

  Future<Map<String, dynamic>> exportLogs() async {
    try {
      final exportData = {
        'logs': logs,
        'exported_at': DateTime.now().toIso8601String(),
      };
      return exportData;
    } catch (e) {
      print('Error exporting logs: $e');
      return {};
    }
  }

  Future<void> _loadLogs() async {
    try {
      final savedLogs = await _storageService.getLocal('app_logs');
      if (savedLogs != null) {
        logs.value = List<Map<String, dynamic>>.from(savedLogs);
      }

      final level = await _storageService.getLocal('log_level');
      if (level != null) {
        logLevel.value = level;
      }
    } catch (e) {
      print('Error loading logs: $e');
    }
  }

  Future<void> _saveLogs() async {
    try {
      // 只保留最近1000条日志
      if (logs.length > 1000) {
        logs.removeRange(1000, logs.length);
      }
      await _storageService.saveLocal('app_logs', logs);
    } catch (e) {
      print('Error saving logs: $e');
    }
  }
} 