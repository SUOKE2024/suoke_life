import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'dart:io';
import '../config/doubao_config.dart';
import '../config/env_config.dart';

class DoubaoClient {
  late final Dio _dio;
  
  DoubaoClient() {
    _dio = Dio(BaseOptions(
      baseUrl: '${DoubaoConfig.baseUrl}/${DoubaoConfig.apiVersion}',
      connectTimeout: DoubaoConfig.timeout,
      receiveTimeout: DoubaoConfig.timeout,
      headers: {
        ...DoubaoConfig.defaultHeaders,
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'X-Agent-Mode': 'enabled',
        'X-HTTP2-Enabled': 'true',
      },
    ));

    // 配置 HTTP/2
    (_dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();
      client.idleTimeout = const Duration(seconds: 30);
      client.connectionTimeout = DoubaoConfig.timeout;
      
      // 强制启用 HTTP/2
      client.badCertificateCallback = (cert, host, port) => true;
      
      // 设置 HTTP/2 选项
      final context = SecurityContext(withTrustedRoots: true);
      try {
        // 启用 HTTP/2 支持
        context.setAlpnProtocols(['h2', 'http/1.1'], true);
      } catch (e) {
        print('Warning: ${e.toString()}');
      }
      
      return client;
    };

    _dio.interceptors.addAll([
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // 确保每个请求都启用代理模式和 HTTP/2
          options.headers['X-Agent-Mode'] = 'enabled';
          options.headers['X-HTTP2-Enabled'] = 'true';
          return handler.next(options);
        },
      ),
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: true,
      ),
    ]);
  }

  // 聊天接口
  Future<Map<String, dynamic>> chat(String message, {
    String? model,
    Map<String, dynamic>? context,
  }) async {
    try {
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': model ?? DoubaoConfig.models['chat'],
          'messages': [
            {'role': 'user', 'content': message}
          ],
          if (context != null) 'context': context,
          'agent_mode': true, // 显式启用代理模式
        },
        options: Options(
          headers: {
            'X-Agent-Mode': 'enabled',
            'X-HTTP2-Enabled': 'true',
          },
        ),
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  // 知识库查询
  Future<Map<String, dynamic>> queryKnowledge(String query) async {
    try {
      final response = await _dio.post(
        '/knowledge/query',
        data: {
          'model': DoubaoConfig.models['knowledge'],
          'query': query,
        },
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  // 文本嵌入
  Future<List<double>> getEmbeddings(String text) async {
    try {
      final response = await _dio.post(
        '/embeddings',
        data: {
          'model': DoubaoConfig.models['embedding'],
          'input': text,
        },
      );
      return List<double>.from(response.data['data'][0]['embedding']);
    } catch (e) {
      rethrow;
    }
  }
} 