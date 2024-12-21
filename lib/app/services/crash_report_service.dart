import 'package:get/get.dart';
import 'dart:io';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class CrashReportService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final crashReports = <Map<String, dynamic>>[].obs;
  final isProcessing = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initCrashReporting();
  }

  Future<void> _initCrashReporting() async {
    try {
      await _loadCrashReports();
      _setupErrorHandlers();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize crash reporting', data: {'error': e.toString()});
    }
  }

  // 记录崩溃
  Future<void> recordCrash(
    dynamic error,
    StackTrace stackTrace, {
    Map<String, dynamic>? extras,
  }) async {
    if (isProcessing.value) return;

    try {
      isProcessing.value = true;

      final report = await _generateCrashReport(error, stackTrace, extras);
      await _saveCrashReport(report);
      await _uploadCrashReport(report);
    } catch (e) {
      await _loggingService.log('error', 'Failed to record crash', data: {'error': e.toString()});
    } finally {
      isProcessing.value = false;
    }
  }

  // 获取崩溃报告
  Future<List<Map<String, dynamic>>> getCrashReports() async {
    try {
      return crashReports.toList();
    } catch (e) {
      await _loggingService.log('error', 'Failed to get crash reports', data: {'error': e.toString()});
      return [];
    }
  }

  // 清除崩溃报告
  Future<void> clearCrashReports() async {
    try {
      crashReports.clear();
      await _storageService.removeLocal('crash_reports');
      await _loggingService.log('info', 'Crash reports cleared');
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear crash reports', data: {'error': e.toString()});
    }
  }

  void _setupErrorHandlers() {
    // 捕获未处理的错误
    FlutterError.onError = (FlutterErrorDetails details) async {
      await recordCrash(
        details.exception,
        details.stack ?? StackTrace.current,
        extras: {'context': details.context?.toString()},
      );
    };

    // 捕获平台错误
    PlatformDispatcher.instance.onError = (error, stack) {
      recordCrash(error, stack);
      return true;
    };
  }

  Future<Map<String, dynamic>> _generateCrashReport(
    dynamic error,
    StackTrace stackTrace,
    Map<String, dynamic>? extras,
  ) async {
    try {
      return {
        'error': error.toString(),
        'stack_trace': stackTrace.toString(),
        'type': error.runtimeType.toString(),
        'platform': Platform.operatingSystem,
        'platform_version': Platform.operatingSystemVersion,
        'timestamp': DateTime.now().toIso8601String(),
        'app_version': await _getAppVersion(),
        'device_info': await _getDeviceInfo(),
        'memory_usage': await _getMemoryUsage(),
        'extras': extras,
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveCrashReport(Map<String, dynamic> report) async {
    try {
      crashReports.insert(0, report);

      // 只保留最近50条记录
      if (crashReports.length > 50) {
        crashReports.removeRange(50, crashReports.length);
      }

      await _storageService.saveLocal('crash_reports', crashReports);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _uploadCrashReport(Map<String, dynamic> report) async {
    try {
      // TODO: 实现崩溃报告上传
    } catch (e) {
      await _loggingService.log('error', 'Failed to upload crash report', data: {'error': e.toString()});
    }
  }

  Future<void> _loadCrashReports() async {
    try {
      final reports = await _storageService.getLocal('crash_reports');
      if (reports != null) {
        crashReports.value = List<Map<String, dynamic>>.from(reports);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<String> _getAppVersion() async {
    // TODO: 实现应用版本获取
    return '1.0.0';
  }

  Future<Map<String, dynamic>> _getDeviceInfo() async {
    // TODO: 实现设备信息获取
    return {};
  }

  Future<Map<String, dynamic>> _getMemoryUsage() async {
    // TODO: 实现内存使用情况获取
    return {};
  }
} 