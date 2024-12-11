import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../utils/logger.dart';

class AIService {
  static final AIService _instance = AIService._internal();
  factory AIService() => _instance;
  
  late final Dio _dio;
  final String _baseUrl;
  final String _apiKey;
  final String _accessToken;
  
  AIService._internal()
      : _baseUrl = dotenv.env['DOUBAO_API_URL'] ?? 'https://api.doubao.com/v1',
        _apiKey = dotenv.env['DOUBAO_API_KEY'] ?? '',
        _accessToken = dotenv.env['DOUBAO_ACCESS_TOKEN'] ?? '' {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_apiKey',
        'X-Access-Token': _accessToken,
      },
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));
    
    _dio.interceptors.add(LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
      logPrint: (obj) => Logger.debug(obj.toString()),
    ));
  }

  /// 与AI模型对话
  Future<String?> chat({
    required String modelId,
    required List<Map<String, dynamic>> messages,
    Map<String, dynamic>? options,
  }) async {
    try {
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': modelId,
          'messages': messages,
          'stream': false,
          ...?options,
        },
      );

      if (response.statusCode == 200 && response.data != null) {
        final choices = response.data['choices'] as List;
        if (choices.isNotEmpty) {
          final message = choices[0]['message'];
          return message['content'] as String;
        }
      }
      
      return null;
    } on DioException catch (e, stackTrace) {
      Logger.error('AI请求错误', e, stackTrace);
      rethrow;
    } catch (e, stackTrace) {
      Logger.error('AI服务错误', e, stackTrace);
      rethrow;
    }
  }

  /// 生成嵌入向量
  Future<List<double>?> createEmbedding({
    required String text,
    String? modelId,
  }) async {
    try {
      final response = await _dio.post(
        '/embeddings',
        data: {
          'model': modelId ?? dotenv.env['DOUBAO_EMBEDDING_KEY'],
          'input': text,
        },
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data['data'] as List;
        if (data.isNotEmpty) {
          return List<double>.from(data[0]['embedding']);
        }
      }
      
      return null;
    } on DioException catch (e, stackTrace) {
      Logger.error('嵌入向量生成错误', e, stackTrace);
      rethrow;
    } catch (e, stackTrace) {
      Logger.error('AI服务错误', e, stackTrace);
      rethrow;
    }
  }
} 