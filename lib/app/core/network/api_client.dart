import 'package:injectable/injectable.dart';
import 'package:dio/dio.dart';

@singleton
class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.suoke.com/v1',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
    ));
  }

  Future<Response<T>> get<T>(String path) => _dio.get<T>(path);
  Future<Response<T>> post<T>(String path, dynamic data) => _dio.post<T>(path, data: data);
} 