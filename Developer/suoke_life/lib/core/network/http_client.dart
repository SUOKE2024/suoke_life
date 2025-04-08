import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// HTTP客户端类
/// 提供基本的HTTP请求方法，并处理网络状态检查和错误处理
class HttpClient {
  final Dio dio;
  final NetworkInfo networkInfo;

  HttpClient({required this.dio, required this.networkInfo});

  /// 执行GET请求
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      if (!await networkInfo.isConnected) {
        throw Exception('网络连接不可用，请检查您的网络设置');
      }

      final response = await dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      LoggerUtils.error('GET请求错误: $path', e);
      rethrow;
    }
  }

  /// 执行POST请求
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      if (!await networkInfo.isConnected) {
        throw Exception('网络连接不可用，请检查您的网络设置');
      }

      final response = await dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      LoggerUtils.error('POST请求错误: $path', e);
      rethrow;
    }
  }

  /// 执行PUT请求
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      if (!await networkInfo.isConnected) {
        throw Exception('网络连接不可用，请检查您的网络设置');
      }

      final response = await dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      LoggerUtils.error('PUT请求错误: $path', e);
      rethrow;
    }
  }

  /// 执行DELETE请求
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      if (!await networkInfo.isConnected) {
        throw Exception('网络连接不可用，请检查您的网络设置');
      }

      final response = await dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response;
    } catch (e) {
      LoggerUtils.error('DELETE请求错误: $path', e);
      rethrow;
    }
  }

  /// 下载文件
  Future<Response> download(
    String urlPath,
    String savePath, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      if (!await networkInfo.isConnected) {
        throw Exception('网络连接不可用，请检查您的网络设置');
      }

      final response = await dio.download(
        urlPath,
        savePath,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      LoggerUtils.error('文件下载错误: $urlPath', e);
      rethrow;
    }
  }
} 