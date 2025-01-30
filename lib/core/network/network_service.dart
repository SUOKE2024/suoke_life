import 'package:injectable/injectable.dart';
import 'package:dio/dio.dart';
import '../security/security_service.dart';
import '../cache/cache_service.dart';
import '../logger/app_logger.dart';
import '../error/api_exception.dart';
import 'dart:io' show SocketException;

@singleton
class NetworkService {
  final Dio _dio;
  bool forceOffline = false;
  bool forceError = false;

  NetworkService() : _dio = Dio() {
    _dio.options.baseUrl = 'https://api.example.com/v1';
    _dio.options.connectTimeout = const Duration(seconds: 5);
    _dio.options.receiveTimeout = const Duration(seconds: 3);
  }

  Future<Response> get(String path, {Map<String, dynamic>? params}) async {
    if (forceOffline) {
      throw const SocketException('No internet connection');
    }
    if (forceError) {
      throw DioException(
        requestOptions: RequestOptions(path: path),
        error: 'Forced error',
      );
    }
    return _dio.get(path, queryParameters: params);
  }

  Future<Response> post(String path, {dynamic data}) async {
    if (forceOffline) {
      throw const SocketException('No internet connection');
    }
    if (forceError) {
      throw DioException(
        requestOptions: RequestOptions(path: path),
        error: 'Forced error',
      );
    }
    return _dio.post(path, data: data);
  }
} 