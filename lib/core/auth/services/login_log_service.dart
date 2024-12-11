import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:get/get.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../models/login_log.dart';
import '../../network/dio_client.dart';

class LoginLogService extends GetxService {
  static LoginLogService get to => Get.find();
  
  final _dioClient = Get.find<DioClient>();
  final _deviceInfo = DeviceInfo();
  
  final _logs = <LoginLog>[].obs;
  List<LoginLog> get logs => _logs;
  
  // 初始化服务
  Future<LoginLogService> init() async {
    await _loadLogs();
    return this;
  }
  
  // 加载登录日志
  Future<void> _loadLogs() async {
    try {
      final response = await _dioClient.get('/auth/logs');
      final List<dynamic> logList = response.data['logs'];
      _logs.value = logList.map((json) => LoginLog.fromJson(json)).toList();
    } catch (e) {
      // 加载失败时使用空列表
      _logs.value = [];
    }
  }
  
  // 记录登录日志
  Future<void> recordLogin({
    required String userId,
    required String loginType,
    required bool isSuccess,
    String? failureReason,
  }) async {
    try {
      final deviceInfo = await _getDeviceInfo();
      final packageInfo = await PackageInfo.fromPlatform();
      
      final response = await _dioClient.post(
        '/auth/logs',
        data: {
          'userId': userId,
          'loginType': loginType,
          'deviceInfo': deviceInfo,
          'appVersion': packageInfo.version,
          'buildNumber': packageInfo.buildNumber,
          'isSuccess': isSuccess,
          'failureReason': failureReason,
        },
      );
      
      if (response.statusCode == 200) {
        final newLog = LoginLog.fromJson(response.data['log']);
        _logs.insert(0, newLog);
      }
    } catch (e) {
      // 记录失败时不影响主流程
    }
  }
  
  // 获取设备信息
  Future<String> _getDeviceInfo() async {
    try {
      if (Platform.isIOS) {
        final info = await _deviceInfo.iosInfo;
        return '${info.name} (${info.systemVersion})';
      } else if (Platform.isAndroid) {
        final info = await _deviceInfo.androidInfo;
        return '${info.brand} ${info.model} (Android ${info.version.release})';
      }
      return '未知设备';
    } catch (e) {
      return '获取设备信息失败';
    }
  }
  
  // 清理登录日志
  Future<void> clearLogs() async {
    try {
      await _dioClient.delete('/auth/logs');
      _logs.clear();
    } catch (e) {
      // 清理失败时不影响主流程
    }
  }
  
  // 获取最近一次登录记录
  LoginLog? getLastLog() {
    return _logs.isEmpty ? null : _logs.first;
  }
  
  // 获取指定时间范围的登录记录
  List<LoginLog> getLogsByDateRange(DateTime start, DateTime end) {
    return _logs.where((log) {
      return log.createdAt.isAfter(start) && log.createdAt.isBefore(end);
    }).toList();
  }
  
  // 获取指定登录类型的记录
  List<LoginLog> getLogsByType(String loginType) {
    return _logs.where((log) => log.loginType == loginType).toList();
  }
  
  // 获取登录失败记录
  List<LoginLog> getFailedLogs() {
    return _logs.where((log) => !log.isSuccess).toList();
  }
  
  // 导出登录日志
  Future<String> exportLogs() async {
    try {
      final response = await _dioClient.get(
        '/auth/logs/export',
        options: Options(responseType: ResponseType.bytes),
      );
      
      final directory = await getApplicationDocumentsDirectory();
      final file = File(
        '${directory.path}/login_logs_${DateTime.now().millisecondsSinceEpoch}.csv',
      );
      
      await file.writeAsBytes(response.data);
      return file.path;
    } catch (e) {
      rethrow;
    }
  }
} 