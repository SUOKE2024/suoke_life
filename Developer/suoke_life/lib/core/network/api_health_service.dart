import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants/api_constants.dart';
import '../utils/logger.dart';

/// API健康状态
enum ApiHealthStatus {
  /// 未检查
  unchecked,
  
  /// 健康
  healthy,
  
  /// 不健康
  unhealthy,
  
  /// 检查中
  checking
}

/// API健康检查服务
/// 
/// 提供检查API服务健康状态的功能
class ApiHealthService {
  final Dio _dio;
  ApiHealthStatus _apiGatewayStatus = ApiHealthStatus.unchecked;
  ApiHealthStatus _authServiceStatus = ApiHealthStatus.unchecked;
  ApiHealthStatus _userServiceStatus = ApiHealthStatus.unchecked;
  
  /// 构造函数
  ApiHealthService({required Dio dio}) : _dio = dio;
  
  /// 获取API网关健康状态
  ApiHealthStatus get apiGatewayStatus => _apiGatewayStatus;
  
  /// 获取认证服务健康状态
  ApiHealthStatus get authServiceStatus => _authServiceStatus;
  
  /// 获取用户服务健康状态
  ApiHealthStatus get userServiceStatus => _userServiceStatus;
  
  /// 检查所有API服务健康状态
  Future<bool> checkAllServices() async {
    final gatewayHealthy = await checkApiGatewayHealth();
    final authHealthy = await checkAuthServiceHealth();
    final userHealthy = await checkUserServiceHealth();
    
    return gatewayHealthy && authHealthy && userHealthy;
  }
  
  /// 检查API网关健康状态
  Future<bool> checkApiGatewayHealth() async {
    _apiGatewayStatus = ApiHealthStatus.checking;
    try {
      final response = await _dio.get(
        '${ApiConstants.apiBaseUrl}/health',
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      
      if (response.statusCode == 200) {
        _apiGatewayStatus = ApiHealthStatus.healthy;
        Logger.info('API网关服务健康检查成功');
        return true;
      } else {
        _apiGatewayStatus = ApiHealthStatus.unhealthy;
        Logger.warning('API网关服务健康检查失败: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      _apiGatewayStatus = ApiHealthStatus.unhealthy;
      Logger.error('API网关服务健康检查异常: $e');
      return false;
    }
  }
  
  /// 检查认证服务健康状态
  Future<bool> checkAuthServiceHealth() async {
    _authServiceStatus = ApiHealthStatus.checking;
    try {
      final response = await _dio.get(
        '${ApiConstants.authServiceUrl}/health',
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      
      if (response.statusCode == 200) {
        _authServiceStatus = ApiHealthStatus.healthy;
        Logger.info('认证服务健康检查成功');
        return true;
      } else {
        _authServiceStatus = ApiHealthStatus.unhealthy;
        Logger.warning('认证服务健康检查失败: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      _authServiceStatus = ApiHealthStatus.unhealthy;
      Logger.error('认证服务健康检查异常: $e');
      return false;
    }
  }
  
  /// 检查用户服务健康状态
  Future<bool> checkUserServiceHealth() async {
    _userServiceStatus = ApiHealthStatus.checking;
    try {
      final response = await _dio.get(
        '${ApiConstants.userServiceUrl}/health',
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      
      if (response.statusCode == 200) {
        _userServiceStatus = ApiHealthStatus.healthy;
        Logger.info('用户服务健康检查成功');
        return true;
      } else {
        _userServiceStatus = ApiHealthStatus.unhealthy;
        Logger.warning('用户服务健康检查失败: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      _userServiceStatus = ApiHealthStatus.unhealthy;
      Logger.error('用户服务健康检查异常: $e');
      return false;
    }
  }
}

/// API健康检查服务Provider
final apiHealthServiceProvider = Provider<ApiHealthService>((ref) {
  final dio = Dio();
  return ApiHealthService(dio: dio);
});

/// API健康状态提供者
final apiHealthStatusProvider = FutureProvider<bool>((ref) async {
  final apiHealthService = ref.watch(apiHealthServiceProvider);
  return apiHealthService.checkAllServices();
}); 