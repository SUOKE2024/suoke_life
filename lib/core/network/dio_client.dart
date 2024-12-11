import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import '../config/app_config.dart';

class DioClient {
  static final DioClient _instance = DioClient._internal();
  late Dio dio;

  factory DioClient() => _instance;

  DioClient._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {'Accept': 'application/json'},
      ),
    );

    if (AppConfig.isDevelopment) {
      dio.interceptors.add(
        PrettyDioLogger(
          requestHeader: true,
          requestBody: true,
          responseHeader: true,
        ),
      );
    }

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // TODO: 添加token等认证信息
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (DioException e, handler) {
          // TODO: 统一错误处理
          return handler.next(e);
        },
      ),
    );
  }
} 