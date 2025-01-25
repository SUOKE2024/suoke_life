import 'package:dio/dio.dart';
import 'package:suoke_life_app_app/core/network/network_service.dart';

class DioNetworkService implements NetworkService {
  final Dio _dio;

  DioNetworkService(this._dio);

  @override
  Future<Response> post(String path, dynamic data) async {
    return _dio.post(path, data: data);
  }

  @override
  Future<Response> get(String path) async {
    return _dio.get(path);
  }

  @override
  Future<Response> put(String path, dynamic data) async {
    return _dio.put(path, data: data);
  }

  @override
  Future<Response> delete(String path) async {
    return _dio.delete(path);
  }
}
