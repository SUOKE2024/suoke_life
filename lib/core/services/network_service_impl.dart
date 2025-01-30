import 'package:dio/dio.dart';
import 'package:suoke_life/lib/core/config/app_config.dart';
import 'package:suoke_life/lib/core/services/network_service.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:encrypt/encrypt.dart';
import 'package:suoke_life/lib/core/services/infrastructure/local_storage_service.dart';

class NetworkServiceImpl implements NetworkService {
  final Dio _dio = Dio(BaseOptions(baseUrl: AppConfig.baseUrl));
  final String _encryptionKey = AppConfig.apiKey;
  final LocalStorageService _localStorageService;

  NetworkServiceImpl(this._localStorageService) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // 添加身份验证拦截器
        final token = await _localStorageService.getStringValue('auth_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        // 添加加密拦截器
        if (options.data is Map) {
          options.data = _encryptData(options.data);
        }
        return handler.next(options);
      },
      onResponse: (response, handler) {
        // 解密响应数据
        if (response.data is Map) {
          response.data = _decryptData(response.data);
        }
        return handler.next(response);
      },
      onError: (DioException e, handler) async {
        // 添加重试拦截器
        if (e.type == DioExceptionType.connectionTimeout ||
            e.type == DioExceptionType.receiveTimeout ||
            e.type == DioExceptionType.sendTimeout) {
          final connectivityResult = await (Connectivity().checkConnectivity());
          if (connectivityResult != ConnectivityResult.none) {
            final options = e.requestOptions;
            try {
              final response = await _dio.request(options.path,
                  cancelToken: options.cancelToken,
                  data: options.data,
                  queryParameters: options.queryParameters,
                  options: Options(
                    method: options.method,
                    headers: options.headers,
                    contentType: options.contentType,
                    responseType: options.responseType,
                  ));
              return handler.resolve(response);
            } on DioException catch (retryError) {
              return handler.reject(retryError);
            }
          }
        }
        return handler.reject(e);
      },
    ));
  }

  @override
  Future<dynamic> get(String path,
      {Map<String, dynamic>? queryParameters}) async {
    try {
      final token = await _localStorageService.getStringValue('auth_token');
      final response = await _dio.get(path,
          queryParameters: queryParameters,
          options: Options(headers: {'Authorization': 'Bearer $token'}));
      return response.data;
    } on DioException catch (e) {
      print('Error fetching data: $e');
      return null;
    }
  }

  @override
  Future<dynamic> post(String path, dynamic data) async {
    try {
      final response = await _dio.post(path, data: data);
      return response.data;
    } on DioException catch (e) {
      print('Error posting data: $e');
      return null;
    }
  }

  @override
  Future<dynamic> put(String path, dynamic data) async {
    try {
      final response = await _dio.put(path, data: data);
      return response.data;
    } on DioException catch (e) {
      print('Error putting data: $e');
      return null;
    }
  }

  @override
  Future<dynamic> delete(String path) async {
    try {
      final response = await _dio.delete(path);
      return response.data;
    } on DioException catch (e) {
      print('Error deleting data: $e');
      return null;
    }
  }

  @override
  Future<String?> getToken() async {
    final token = await _localStorageService.getStringValue('auth_token');
    return token;
  }

  Map<String, dynamic> _encryptData(Map<String, dynamic> data) {
    final key = Key.fromUtf8(_encryptionKey);
    final encrypter = Encrypter(AES(key));
    final encryptedData = <String, dynamic>{};
    data.forEach((key, value) {
      if (value is String) {
        final encrypted = encrypter.encrypt(value, iv: IV.fromLength(16));
        encryptedData[key] = encrypted.base64;
      } else {
        encryptedData[key] = value;
      }
    });
    return encryptedData;
  }

  Map<String, dynamic> _decryptData(Map<String, dynamic> data) {
    final key = Key.fromUtf8(_encryptionKey);
    final encrypter = Encrypter(AES(key));
    final decryptedData = <String, dynamic>{};
    data.forEach((key, value) {
      if (value is String) {
        try {
          final encrypted = Encrypted.fromBase64(value);
          decryptedData[key] =
              encrypter.decrypt(encrypted, iv: IV.fromLength(16));
        } catch (e) {
          decryptedData[key] = value;
        }
      } else {
        decryptedData[key] = value;
      }
    });
    return decryptedData;
  }

  Future<Options> _getRequestOptions() async {
    final token = await _localStorageService.getStringValue('auth_token');
    return Options(headers: {'Authorization': 'Bearer $token'});
  }
}
