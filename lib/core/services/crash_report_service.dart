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
    final deviceInfo = await _getDeviceInfo();
    return {
      'error': error.toString(),
      'stackTrace': stackTrace.toString(),
      'deviceInfo': deviceInfo,
      'extras': extras ?? {},
    };
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
    print('Uploading crash report...');
    // 示例：将崩溃报告发送到远程服务器
    // 实际实现中需要根据具体服务器进行上传
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
    print('Retrieving device information...');
    // 示例：获取设备信息
    // 实际实现中需要根据具体设备信息库进行获取
    return {
      'os': Platform.operatingSystem,
      'osVersion': Platform.operatingSystemVersion,
      'deviceModel': 'Unknown', // 需要替换为实际设备型号获取逻辑
    };
  }

  Future<Map<String, dynamic>> _getMemoryUsage() async {
    // TODO: 实现内存使用情况获取
    return {};
  }
} 