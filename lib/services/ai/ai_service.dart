import 'package:dio/dio.dart' hide Response;
import 'package:get/get.dart';

abstract class AIService {
  Future<String> chat(String message);
  Future<String> generateImage(String prompt);
  Future<String> generateEmbedding(String text);
}

class AIServiceImpl extends AIService {
  final Dio _dio;
  final String _baseUrl;
  final String _apiKey;

  AIServiceImpl({
    required String baseUrl,
    required String apiKey,
  }) : _baseUrl = baseUrl,
       _apiKey = apiKey,
       _dio = Dio(BaseOptions(
         baseUrl: baseUrl,
         headers: {
           'Authorization': 'Bearer $apiKey',
           'Content-Type': 'application/json',
         },
       ));

  @override
  Future<String> chat(String message) async {
    try {
      final response = await _dio.post('/chat/completions', data: {
        'messages': [{'role': 'user', 'content': message}],
        'model': 'doubao-pro-32k',
      });
      return response.data['choices'][0]['message']['content'];
    } catch (e) {
      print('Chat error: $e');
      throw Exception('聊天请求失败');
    }
  }

  @override
  Future<String> generateImage(String prompt) async {
    try {
      final response = await _dio.post('/images/generations', data: {
        'prompt': prompt,
        'n': 1,
        'size': '1024x1024',
      });
      return response.data['data'][0]['url'];
    } catch (e) {
      print('Image generation error: $e');
      throw Exception('图片生成失败');
    }
  }

  @override
  Future<String> generateEmbedding(String text) async {
    try {
      final response = await _dio.post('/embeddings', data: {
        'input': text,
        'model': 'doubao-embedding',
      });
      return response.data['data'][0]['embedding'].toString();
    } catch (e) {
      print('Embedding error: $e');
      throw Exception('嵌入生成失败');
    }
  }
}
