import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final healthServiceClientProvider = Provider<HealthServiceClient>((ref) {
  return HealthServiceClient(Dio());
});

class HealthServiceClient {
  final Dio _dio;

  HealthServiceClient(this._dio) {
    _dio.options.baseUrl = 'https://api.suoke.life/health/v1';
    _dio.options.connectTimeout = const Duration(seconds: 10);
    _dio.options.receiveTimeout = const Duration(seconds: 10);
  }

  Future<Response> get(String path) async {
    try {
      return await _dio.get(path);
    } on DioException catch (e) {
      throw Exception('Failed to GET $path: ${e.message}');
    }
  }

  Future<Response> post(String path, {required Map<String, dynamic> data}) async {
    try {
      return await _dio.post(path, data: data);
    } on DioException catch (e) {
      throw Exception('Failed to POST $path: ${e.message}');
    }
  }
}
