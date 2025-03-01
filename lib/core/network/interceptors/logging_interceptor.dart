import 'dart:convert';
import 'package:dio/dio.dart';
import '../../utils/logger.dart';

/// 日志拦截器
/// 负责记录API请求和响应的详细信息
class LoggingInterceptor extends Interceptor {
  /// 是否打印请求体
  final bool logRequestBody;
  
  /// 是否打印响应体
  final bool logResponseBody;
  
  /// 是否打印头信息
  final bool logHeaders;
  
  /// 构造函数
  LoggingInterceptor({
    this.logRequestBody = true,
    this.logResponseBody = true,
    this.logHeaders = true,
  });
  
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final requestId = DateTime.now().millisecondsSinceEpoch.toString();
    options.extra['requestId'] = requestId;
    
    final method = options.method;
    final baseUrl = options.baseUrl;
    final path = options.path;
    final url = options.uri.toString();
    
    var logMessage = '[ 请求 ] ($requestId) - $method $path\n';
    logMessage += '完整URL：$url\n';
    
    if (logHeaders && options.headers.isNotEmpty) {
      logMessage += '请求头：\n';
      options.headers.forEach((key, value) {
        // 过滤敏感信息
        if (key.toLowerCase() == 'authorization') {
          value = '${value.toString().substring(0, 15)}...';
        }
        logMessage += '  $key: $value\n';
      });
    }
    
    if (logRequestBody && options.data != null) {
      try {
        var requestBody = '';
        if (options.data is FormData) {
          final formData = options.data as FormData;
          requestBody = '表单数据：\n';
          formData.fields.forEach((field) {
            requestBody += '  ${field.key}: ${field.value}\n';
          });
          if (formData.files.isNotEmpty) {
            requestBody += '包含 ${formData.files.length} 个文件\n';
          }
        } else if (options.data is Map || options.data is List) {
          requestBody = const JsonEncoder.withIndent('  ').convert(options.data);
        } else {
          requestBody = options.data.toString();
        }
        logMessage += '请求体：\n$requestBody\n';
      } catch (e) {
        logMessage += '请求体：[无法解析 - $e]\n';
      }
    }
    
    logger.d(logMessage);
    handler.next(options);
  }
  
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final requestId = response.requestOptions.extra['requestId'] as String?;
    final statusCode = response.statusCode;
    final method = response.requestOptions.method;
    final path = response.requestOptions.path;
    
    var logMessage = '[ 响应 ] ($requestId) - $method $path\n';
    logMessage += '状态码：$statusCode\n';
    
    if (logHeaders && response.headers.map.isNotEmpty) {
      logMessage += '响应头：\n';
      response.headers.forEach((key, values) {
        for (var value in values) {
          logMessage += '  $key: $value\n';
        }
      });
    }
    
    if (logResponseBody && response.data != null) {
      try {
        var responseBody = '';
        if (response.data is Map || response.data is List) {
          responseBody = const JsonEncoder.withIndent('  ').convert(response.data);
        } else {
          responseBody = response.data.toString();
        }
        
        // 如果响应体太长，只显示一部分
        if (responseBody.length > 5000) {
          responseBody = responseBody.substring(0, 5000) + '... [响应过长，已截断]';
        }
        
        logMessage += '响应体：\n$responseBody\n';
      } catch (e) {
        logMessage += '响应体：[无法解析 - $e]\n';
      }
    }
    
    logger.d(logMessage);
    handler.next(response);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final requestId = err.requestOptions.extra['requestId'] as String?;
    final method = err.requestOptions.method;
    final path = err.requestOptions.path;
    
    var logMessage = '[ 错误 ] ($requestId) - $method $path\n';
    logMessage += '错误类型：${err.type}\n';
    
    if (err.response != null) {
      final statusCode = err.response!.statusCode;
      logMessage += '状态码：$statusCode\n';
      
      if (logHeaders && err.response!.headers.map.isNotEmpty) {
        logMessage += '响应头：\n';
        err.response!.headers.forEach((key, values) {
          for (var value in values) {
            logMessage += '  $key: $value\n';
          }
        });
      }
      
      if (logResponseBody && err.response!.data != null) {
        try {
          var responseBody = '';
          if (err.response!.data is Map || err.response!.data is List) {
            responseBody = const JsonEncoder.withIndent('  ').convert(err.response!.data);
          } else {
            responseBody = err.response!.data.toString();
          }
          logMessage += '错误响应体：\n$responseBody\n';
        } catch (e) {
          logMessage += '错误响应体：[无法解析 - $e]\n';
        }
      }
    } else {
      logMessage += '错误消息：${err.message}\n';
    }
    
    if (err.error != null) {
      logMessage += '异常：${err.error}\n';
    }
    
    logger.e(logMessage);
    handler.next(err);
  }
} 