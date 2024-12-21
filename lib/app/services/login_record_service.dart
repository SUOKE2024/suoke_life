import 'package:get/get.dart';
import '../data/models/login_record.dart';
import '../core/network/api_client.dart';
import '../core/services/device_info_service.dart';

class LoginRecordService extends GetxService {
  final ApiClient _apiClient;
  final DeviceInfoService _deviceInfo;

  LoginRecordService({
    required ApiClient apiClient,
    required DeviceInfoService deviceInfo,
  })  : _apiClient = apiClient,
        _deviceInfo = deviceInfo;

  Future<void> recordLogin({
    required String userId,
    required String loginType,
    required bool success,
    String? errorMessage,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final deviceInfo = await _deviceInfo.getDeviceInfo();
      final ipAddress = await _getIpAddress();

      await _apiClient.post('/auth/login-records', data: {
        'user_id': userId,
        'device_info': deviceInfo.toJson(),
        'ip_address': ipAddress,
        'login_type': loginType,
        'success': success,
        'error_message': errorMessage,
        'metadata': metadata,
      });
    } catch (e) {
      debugPrint('记录登录失败: $e');
    }
  }

  Future<List<LoginRecord>> getLoginRecords({
    String? userId,
    DateTime? startTime,
    DateTime? endTime,
    bool? success,
    int? limit,
  }) async {
    try {
      final response = await _apiClient.get(
        '/auth/login-records',
        queryParameters: {
          if (userId != null) 'user_id': userId,
          if (startTime != null) 'start_time': startTime.toIso8601String(),
          if (endTime != null) 'end_time': endTime.toIso8601String(),
          if (success != null) 'success': success,
          if (limit != null) 'limit': limit,
        },
      );

      return (response['records'] as List)
        .map((json) => LoginRecord.fromJson(json))
        .toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<String> _getIpAddress() async {
    try {
      final response = await _apiClient.get('https://api.ipify.org?format=json');
      return response['ip'];
    } catch (e) {
      return 'unknown';
    }
  }
} 