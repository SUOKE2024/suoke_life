import 'dart:async';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// 服务器测试结果
class ServerTestResult {
  /// 是否成功
  final bool success;
  
  /// 状态码
  final int? statusCode;
  
  /// 响应数据
  final dynamic data;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 响应时间（毫秒）
  final int responseTimeMs;

  /// 创建成功结果
  ServerTestResult.success({
    required this.statusCode,
    required this.data,
    required this.responseTimeMs,
  })  : success = true,
        errorMessage = null;

  /// 创建失败结果
  ServerTestResult.failure({
    this.statusCode,
    this.data,
    required this.errorMessage,
    required this.responseTimeMs,
  }) : success = false;
}

/// 网络连接测试器
class NetworkTester {
  final Dio _dio;
  static const String _tag = 'NetworkTester';

  /// 创建网络测试器
  NetworkTester({Dio? dio}) : _dio = dio ?? Dio();

  /// 测试服务器健康状态
  Future<ServerTestResult> testServerHealth() async {
    final stopwatch = Stopwatch()..start();
    try {
      final response = await _dio.get(
        ApiConstants.connectionTestUrl,
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      
      stopwatch.stop();
      
      return ServerTestResult.success(
        statusCode: response.statusCode,
        data: response.data,
        responseTimeMs: stopwatch.elapsedMilliseconds,
      );
    } catch (e) {
      stopwatch.stop();
      String errorMessage;
      
      if (e is DioException) {
        switch (e.type) {
          case DioExceptionType.connectionTimeout:
            errorMessage = '连接超时';
            break;
          case DioExceptionType.sendTimeout:
            errorMessage = '发送请求超时';
            break;
          case DioExceptionType.receiveTimeout:
            errorMessage = '接收响应超时';
            break;
          case DioExceptionType.badCertificate:
            errorMessage = '证书验证失败';
            break;
          case DioExceptionType.badResponse:
            errorMessage = '无效响应：${e.response?.statusCode}';
            break;
          case DioExceptionType.cancel:
            errorMessage = '请求已取消';
            break;
          case DioExceptionType.connectionError:
            errorMessage = '连接错误';
            break;
          case DioExceptionType.unknown:
          default:
            if (e.error is SocketException) {
              errorMessage = '网络连接失败';
            } else {
              errorMessage = '未知错误：${e.message}';
            }
        }
      } else {
        errorMessage = '发生错误：$e';
      }
      
      Logger.e(_tag, errorMessage);
      
      return ServerTestResult.failure(
        errorMessage: errorMessage,
        responseTimeMs: stopwatch.elapsedMilliseconds,
      );
    }
  }
  
  /// 测试API端点
  Future<ServerTestResult> testApiEndpoint(String endpoint) async {
    final stopwatch = Stopwatch()..start();
    try {
      final response = await _dio.get(
        endpoint,
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      
      stopwatch.stop();
      
      return ServerTestResult.success(
        statusCode: response.statusCode,
        data: response.data,
        responseTimeMs: stopwatch.elapsedMilliseconds,
      );
    } catch (e) {
      stopwatch.stop();
      
      return ServerTestResult.failure(
        errorMessage: '请求失败：$e',
        responseTimeMs: stopwatch.elapsedMilliseconds,
      );
    }
  }
  
  /// 测试多个端点
  Future<Map<String, ServerTestResult>> testMultipleEndpoints(List<String> endpoints) async {
    final results = <String, ServerTestResult>{};
    
    for (final endpoint in endpoints) {
      results[endpoint] = await testApiEndpoint(endpoint);
    }
    
    return results;
  }
  
  /// 测试API完整连接
  Future<Map<String, ServerTestResult>> testFullApiConnection() async {
    const endpoints = [
      ApiConstants.connectionTestUrl,                          // 健康检查
      ApiConstants.apiBaseUrl + ApiConstants.userEndpoint,     // 用户API
      ApiConstants.apiBaseUrl + ApiConstants.healthDataPath,   // 健康数据API
      ApiConstants.apiBaseUrl + ApiConstants.aiEndpoint,       // AI服务API
    ];
    
    return testMultipleEndpoints(endpoints);
  }
}

/// 网络测试器Provider
final networkTesterProvider = Provider<NetworkTester>((ref) {
  final dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));
  
  return NetworkTester(dio: dio);
}); 