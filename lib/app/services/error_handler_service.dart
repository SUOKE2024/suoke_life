import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'notification_service.dart';

class ErrorHandlerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final NotificationService _notificationService = Get.find();

  final errorHistory = <Map<String, dynamic>>[].obs;
  final isHandling = false.obs;

  // 处理错误
  Future<void> handleError(dynamic error, {StackTrace? stackTrace, String? context}) async {
    if (isHandling.value) return;

    try {
      isHandling.value = true;

      final errorInfo = await _processError(error, stackTrace, context);
      await _saveErrorRecord(errorInfo);
      await _notifyError(errorInfo);
      await _executeRecoveryStrategy(errorInfo);
    } catch (e) {
      await _loggingService.log('error', 'Failed to handle error', data: {'error': e.toString()});
    } finally {
      isHandling.value = false;
    }
  }

  // 获取错误历史
  Future<List<Map<String, dynamic>>> getErrorHistory() async {
    try {
      return errorHistory.toList();
    } catch (e) {
      await _loggingService.log('error', 'Failed to get error history', data: {'error': e.toString()});
      return [];
    }
  }

  // 清除错误历史
  Future<void> clearErrorHistory() async {
    try {
      errorHistory.clear();
      await _storageService.removeLocal('error_history');
      await _loggingService.log('info', 'Error history cleared');
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear error history', data: {'error': e.toString()});
    }
  }

  Future<Map<String, dynamic>> _processError(
    dynamic error,
    StackTrace? stackTrace,
    String? context,
  ) async {
    try {
      final errorInfo = {
        'error': error.toString(),
        'stack_trace': stackTrace?.toString(),
        'context': context,
        'timestamp': DateTime.now().toIso8601String(),
        'severity': _calculateErrorSeverity(error),
        'type': error.runtimeType.toString(),
      };

      await _loggingService.log(
        'error',
        'Error occurred',
        data: errorInfo,
      );

      return errorInfo;
    } catch (e) {
      rethrow;
    }
  }

  String _calculateErrorSeverity(dynamic error) {
    // TODO: 实现错误严重程度计算
    if (error is Exception) {
      return 'high';
    } else if (error is Error) {
      return 'critical';
    }
    return 'medium';
  }

  Future<void> _saveErrorRecord(Map<String, dynamic> errorInfo) async {
    try {
      errorHistory.insert(0, errorInfo);

      // 只保留最近100条记录
      if (errorHistory.length > 100) {
        errorHistory.removeRange(100, errorHistory.length);
      }

      await _storageService.saveLocal('error_history', errorHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _notifyError(Map<String, dynamic> errorInfo) async {
    try {
      if (_shouldNotifyUser(errorInfo)) {
        await _notificationService.showNotification(
          title: '发生错误',
          body: _generateErrorMessage(errorInfo),
        );
      }
    } catch (e) {
      rethrow;
    }
  }

  bool _shouldNotifyUser(Map<String, dynamic> errorInfo) {
    final severity = errorInfo['severity'];
    return severity == 'high' || severity == 'critical';
  }

  String _generateErrorMessage(Map<String, dynamic> errorInfo) {
    // TODO: 实现错误消息生成
    return '应用程序遇到了一个问题,我们正在努力修复。';
  }

  Future<void> _executeRecoveryStrategy(Map<String, dynamic> errorInfo) async {
    try {
      final strategy = await _determineRecoveryStrategy(errorInfo);
      await _executeStrategy(strategy);
    } catch (e) {
      rethrow;
    }
  }

  Future<String> _determineRecoveryStrategy(Map<String, dynamic> errorInfo) async {
    // TODO: 实现恢复策略确定
    return 'restart';
  }

  Future<void> _executeStrategy(String strategy) async {
    try {
      switch (strategy) {
        case 'restart':
          // TODO: 实现应用重启
          break;
        case 'clear_cache':
          // TODO: 实现缓存清理
          break;
        case 'reset':
          // TODO: 实现应用重置
          break;
        default:
          // 默认不执行任何操作
          break;
      }
    } catch (e) {
      rethrow;
    }
  }
} 