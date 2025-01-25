import 'package:injectable/injectable.dart';
import 'package:dio/dio.dart';

@lazySingleton
class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.suoke.com/v1',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
    ));
  }

  Future<Map<String, dynamic>> get(String path) async {
    final response = await _dio.get(path);
    return response.data;
  }

  Future<void> post(String path, Map<String, dynamic> data) async {
    await _dio.post(path, data: data);
  }
} 