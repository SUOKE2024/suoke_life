import 'package:dio/dio.dart';
import '../../core/network/http_client.dart';
import '../../core/values/api_config.dart';
import '../models/health_advice.dart';
import '../../core/error/error_types.dart';
import '../../core/error/app_exception.dart';

class HealthAdviceProvider {
  final HttpClient _httpClient;

  HealthAdviceProvider(this._httpClient);

  Future<List<HealthAdvice>> getAdvices() async {
    try {
      final response = await _httpClient.get(ApiConfig.healthAdvices);
      return (response.data as List)
          .map((json) => HealthAdvice.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw AppException(
        type: ErrorType.health,
        message: '获取健康建议失败: ${e.message}',
      );
    }
  }

  Future<HealthAdvice> getAdviceDetail(String id) async {
    try {
      final response = await _httpClient.get('${ApiConfig.healthAdvices}/$id');
      return HealthAdvice.fromJson(response.data);
    } on DioException catch (e) {
      throw AppException(
        type: ErrorType.health,
        message: '获取健康建议详情失败: ${e.message}',
      );
    }
  }

  Exception _handleDioError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return TimeoutException('连接超时');
      case DioExceptionType.badResponse:
        return ServerException('服务器错误');
      case DioExceptionType.cancel:
        return RequestCancelledException();
      default:
        return NetworkException('网络错误');
    }
  }
}

class TimeoutException implements Exception {
  final String message;
  TimeoutException(this.message);
}

class ServerException implements Exception {
  final String message;
  ServerException(this.message);
}

class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
}

class RequestCancelledException implements Exception {} 