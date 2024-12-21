import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'package:logger/logger.dart';

class LoggingService extends GetxService {
  final StorageService _storageService = Get.find();
  late final Logger _logger;

  final logs = <Map<String, dynamic>>[].obs;
  final logLevel = 'info'.obs;

  @override
  void onInit() {
    super.onInit();
    _initLogger();
    _loadLogs();
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

  // 记录日志
  Future<void> log(String level, String message, {Map<String, dynamic>? data}) async {
    try {
      final logEntry = {
        'level': level,
        'message': message,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      };

      // 添加到内存
      logs.insert(0, logEntry);

      // 保存到本地
      await _saveLogs();

      // 打印日志
      _printLog(level, message, data);

      // 检查是否需要上传
      await _checkUploadLogs();
    } catch (e) {
      print('Error logging: $e');
    }
  }

  // 设置日志级别
  Future<void> setLogLevel(String level) async {
    try {
      logLevel.value = level;
      await _storageService.saveLocal('log_level', level);
    } catch (e) {
      rethrow;
    }
  }

  // 清理日志
  Future<void> clearLogs() async {
    try {
      logs.clear();
      await _storageService.removeLocal('app_logs');
    } catch (e) {
      rethrow;
    }
  }

  // 导出日志
  Future<String> exportLogs() async {
    try {
      final exportData = {
        'logs': logs,
        'exported_at': DateTime.now().toIso8601String(),
      };
      return _formatLogsForExport(exportData);
    } catch (e) {
      rethrow;
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
      // 处理错误
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

  void _printLog(String level, String message, Map<String, dynamic>? data) {
    switch (level) {
      case 'debug':
        _logger.d(message, data);
        break;
      case 'info':
        _logger.i(message, data);
        break;
      case 'warning':
        _logger.w(message, data);
        break;
      case 'error':
        _logger.e(message, data);
        break;
    }
  }

  Future<void> _checkUploadLogs() async {
    try {
      // 检查是否需要上传日志
      final lastUpload = await _storageService.getLocal('last_log_upload');
      if (lastUpload == null || _shouldUploadLogs(lastUpload)) {
        await _uploadLogs();
      }
    } catch (e) {
      print('Error checking logs upload: $e');
    }
  }

  bool _shouldUploadLogs(String lastUpload) {
    final lastUploadTime = DateTime.parse(lastUpload);
    final now = DateTime.now();
    return now.difference(lastUploadTime).inHours >= 24;
  }

  Future<void> _uploadLogs() async {
    try {
      // TODO: 实现日志上传逻辑
      await _storageService.saveLocal(
        'last_log_upload',
        DateTime.now().toIso8601String(),
      );
    } catch (e) {
      print('Error uploading logs: $e');
    }
  }

  String _formatLogsForExport(Map<String, dynamic> data) {
    // TODO: 实现日志格式化
    return '';
  }
} 